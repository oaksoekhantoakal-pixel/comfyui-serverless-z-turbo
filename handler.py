import runpod
import json
import os
import subprocess
import time
import requests
import base64
import random

def check_paths():
    paths_to_check = [
        "/runpod-volume",
        "/runpod-volume/ComfyUI/models",
        "/comfyui/models",
        "workflow_api.json"
    ]
    print("--- STARTING PATH CHECK ---")
    for p in paths_to_check:
        exists = os.path.exists(p)
        print(f"Path {p}: {'EXISTS' if exists else 'NOT FOUND'}")
    print("--- END PATH CHECK ---")

try:
    check_paths()
    print("Launching ComfyUI Server...")
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

    # Wait for server to be ready
    ready = False
    for i in range(30):
        try:
            response = requests.get("http://127.0.0.1:8188")
            if response.status_code == 200:
                print("ComfyUI Server is up and running!")
                ready = True
                break
        except:
            pass
        time.sleep(2)
    
    if not ready:
        print("CRITICAL: ComfyUI failed to start.")
except Exception as e:
    print(f"BOOT ERROR: {str(e)}")

# Load JSON
with open("workflow_api.json", "r") as f:
    workflow_template = json.load(f)

def handler(job):
    try:
        job_input = job["input"]
        prompt_text = job_input.get("prompt", "A beautiful portrait")
        
        # Clone workflow template
        workflow = json.loads(json.dumps(workflow_template))

        # Update Node 58 with user prompt
        if "58" in workflow:
            workflow["58"]["inputs"]["value"] = prompt_text

        # Generate Random Seed for Node 57:3
        if "57:3" in workflow:
            workflow["57:3"]["inputs"]["seed"] = random.randint(1, 1000000)

        # Send request to ComfyUI
        payload = {"prompt": workflow}
        res = requests.post("http://127.0.0.1:8188/prompt", json=payload)
        
        return {"status": "success", "response": res.json()}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
