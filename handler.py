import runpod
import json
import os
import subprocess
import time
import requests
import base64
import random

def verify_models():
    print("--- MODEL VERIFICATION START ---")
    target_path = "/comfyui/models/diffusion_models"
    if os.path.exists(target_path):
        print(f"Success: Found models at {target_path}")
    else:
        print(f"Error: Cannot find models at {target_path}")
    print("--- MODEL VERIFICATION END ---")

try:
    verify_models()
    print("Starting ComfyUI Server...")
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

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

with open("workflow_api.json", "r") as f:
    workflow_template = json.load(f)

def handler(job):
    try:
        job_input = job["input"]
        prompt_text = job_input.get("prompt", "A high quality photo")
        workflow = json.loads(json.dumps(workflow_template))

        if "58" in workflow:
            workflow["58"]["inputs"]["value"] = prompt_text
        
        if "57:3" in workflow:
            workflow["57:3"]["inputs"]["seed"] = random.randint(1, 1000000000)

        # 1. Send Prompt to ComfyUI
        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        res_data = res.json()
        prompt_id = res_data["prompt_id"]
        print(f"Prompt sent. ID: {prompt_id}")

        # 2. Wait for the image generation to complete
        max_wait = 60 # 1 minute timeout
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait:
                return {"error": "Generation timed out"}

            history_res = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
            history = history_res.json()

            if prompt_id in history:
                # 3. Find the image filename in the history
                # Node 9 is standard for SaveImage in many workflows
                outputs = history[prompt_id]["outputs"]
                for node_id in outputs:
                    if "images" in outputs[node_id]:
                        image_info = outputs[node_id]["images"][0]
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")
                        
                        # 4. Read the image and convert to Base64
                        image_path = os.path.join("/comfyui/output", subfolder, filename)
                        with open(image_path, "rb") as img_file:
                            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
                        
                        print(f"Image generated and converted: {filename}")
                        return {
                            "status": "success",
                            "image": base64_image
                        }
            
            time.sleep(1)

    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
