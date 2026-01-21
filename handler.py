import runpod
import json
import os
import subprocess
import time
import requests
import base64
import random

# Start ComfyUI
try:
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])
    # Wait for server to start
    for _ in range(30):
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
        prompt_text = job_input.get("prompt", "A cinematic portrait")
        workflow = json.loads(json.dumps(workflow_template))

        # Map user input to your workflow nodes
        if "58" in workflow: workflow["58"]["inputs"]["value"] = prompt_text
        if "57:3" in workflow: workflow["57:3"]["inputs"]["seed"] = random.randint(1, 10**9)

        # 1. Send Prompt
        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        prompt_id = res.json()["prompt_id"]
        print(f"Job processing: {prompt_id}")

        # 2. Wait up to 300 seconds (5 minutes)
        for i in range(150): # 150 * 2 seconds = 300s
            history_res = requests.get(f"http://127.0.0.1:8188/history/{prompt_id}")
            history = history_res.json()

            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]
                # 3. Search for any node that contains an image
                for node_id in outputs:
                    if "images" in outputs[node_id]:
                        image_info = outputs[node_id]["images"][0]
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")
                        
                        # 4. Convert generated image to Base64
                        image_path = os.path.join("/comfyui/output", subfolder, filename)
                        with open(image_path, "rb") as img_file:
                            base64_image = base64.b64encode(img_file.read()).decode("utf-8")
                        
                        return {"status": "success", "image": base64_image}
            
            time.sleep(2) # Check every 2 seconds

        return {"status": "error", "message": "Generation timed out after 5 minutes"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

runpod.serverless.start({"handler": handler})
