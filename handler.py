import runpod
import json
import os
import subprocess
import time
import requests
import random

def check_models():
    print("--- MODEL CHECK START ---")
    # Check if the symlink is pointing to the right place
    base_path = "/comfyui/models"
    sub_folders = ["diffusion_models", "vae", "text_encoders"]
    
    for folder in sub_folders:
        path = os.path.join(base_path, folder)
        if os.path.exists(path):
            files = os.listdir(path)
            print(f"Folder {folder} found. Files: {files}")
        else:
            print(f"ERROR: Folder {path} NOT FOUND!")
    print("--- MODEL CHECK END ---")

try:
    check_models()
    print("Starting ComfyUI Server...")
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

    # Wait for server
    for i in range(30):
        try:
            if requests.get("http://127.0.0.1:8188").status_code == 200:
                print("ComfyUI is Ready!")
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
        prompt_text = job_input.get("prompt", "A futuristic city")
        workflow = json.loads(json.dumps(workflow_template))

        # Mapping input to Node 58
        if "58" in workflow:
            workflow["58"]["inputs"]["value"] = prompt_text
        
        # Random seed for Node 57:3
        if "57:3" in workflow:
            workflow["57:3"]["inputs"]["seed"] = random.randint(1, 1000000000)

        res = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
        return {"status": "success", "data": res.json()}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
