import runpod
import json
import os
import subprocess
import time
import requests
import random

def verify_models():
    print("--- MODEL VERIFICATION START ---")
    # This checks if the files are visible inside the container
    target_path = "/comfyui/models/diffusion_models"
    if os.path.exists(target_path):
        print(f"Success: Found diffusion_models folder.")
        print(f"Files inside: {os.listdir(target_path)}")
    else:
        print(f"Error: Cannot find models at {target_path}")
    print("--- MODEL VERIFICATION END ---")

try:
    verify_models()
    print("Starting ComfyUI Server...")
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

    # Health check for ComfyUI
    for i in range(30):
        try:
            if requests.get("http://127.0.0.1:8188").status_code == 200:
                print("Server is Ready!")
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
            workflow["57:3"]["inputs"]["seed"] = random.randint(1, 1000000)

        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        return {"status": "success", "data": res.json()}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
