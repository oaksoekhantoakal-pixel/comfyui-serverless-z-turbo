import runpod
import json
import os
import subprocess
import time
import requests
import base64
import random

# Start the ComfyUI Server in the background
try:
    print("Starting ComfyUI Server...")
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

    # Wait for the server to be ready
    for i in range(30):
        try:
            if requests.get("http://127.0.0.1:8188").status_code == 200:
                print("ComfyUI Server is Ready!")
                break
        except:
            pass
        time.sleep(2)
except Exception as e:
    print(f"Startup Error: {str(e)}")

# Load the workflow template
with open("workflow_api.json", "r") as f:
    workflow_template = json.load(f)

def handler(job):
    try:
        job_input = job["input"]
        
        # Get prompt and resolution from the job input
        prompt_text = job_input.get("prompt", "A high quality cinematic photo")
        width = job_input.get("width", 1024)
        height = job_input.get("height", 1024)
        
        # Create a copy of the workflow to modify
        workflow = json.loads(json.dumps(workflow_template))

        # 1. Update Prompt (Mapping to your specific Node IDs)
        if "58" in workflow:
            workflow["58"]["inputs"]["value"] = prompt_text
        if "57:27" in workflow:
            workflow["57:27"]["inputs"]["text"] = prompt_text

        # 2. Update Aspect Ratio (Mapping to your EmptySD3LatentImage node)
        if "57:13" in workflow:
            workflow["57:13"]["inputs"]["width"] = width
            workflow["57:13"]["inputs"]["height"] = height

        # 3. Randomize Seed for varied results (Mapping to KSampler)
        if "57:3" in workflow:
            workflow["57:3"]["inputs"]["seed"] = random.randint(1, 10**12)

        # 4. Submit the job to ComfyUI
        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        prompt_id = res.json()["prompt_id"]
        print(f"Job submitted to ComfyUI. ID: {prompt_id}")

        # 5. Poll for completion (Wait up to 5 minutes)
        for _ in range(150): # 150 iterations * 2s = 300s
            history_response = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
            history = history_response.json()

            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]
                # Search for the generated image in the output nodes
                for node_id in outputs:
                    if "images" in outputs[node_id]:
                        image_info = outputs[node_id]["images"][0]
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")
                        
                        # 6. Read image file and convert to Base64
                        image_path = os.path.join("/comfyui/output", subfolder, filename)
                        with open(image_path, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        
                        print(f"Successfully generated image: {filename}")
                        return {
                            "status": "success",
                            "image": base64_image
                        }
            
            time.sleep(2)
            
        return {"status": "error", "message": "Generation timed out"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Initialize RunPod Serverless
runpod.serverless.start({"handler": handler})
