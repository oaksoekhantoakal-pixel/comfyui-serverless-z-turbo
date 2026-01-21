import runpod
import json
import os
import subprocess
import time
import requests
import base64
import random

# Error ရှာဖွေရန် function
def check_paths():
    paths_to_check = [
        "/runpod-volume",
        "/runpod-volume/ComfyUI/models",
        "/comfyui/models",
        "workflow_api.json"
    ]
    print("--- PATH CHECK START ---")
    for p in paths_to_check:
        exists = os.path.exists(p)
        print(f"Checking {p}: {'EXISTS' if exists else 'NOT FOUND'}")
    print("--- PATH CHECK END ---")

try:
    check_paths()
    
    print("Starting ComfyUI Server...")
    # main.py ရှိမရှိ စစ်ပါ
    if not os.path.exists("main.py"):
        print("ERROR: main.py not found in /comfyui!")
    
    subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

    # Server တက်လာအောင် စောင့်ခြင်း
    max_retries = 30
    ready = False
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8188")
            if response.status_code == 200:
                print("ComfyUI is ready!")
                ready = True
                break
        except:
            pass
        if i % 5 == 0: print(f"Waiting for ComfyUI... ({i}/{max_retries})")
        time.sleep(2)
    
    if not ready:
        print("ERROR: ComfyUI server failed to start in time.")

except Exception as e:
    print(f"CRITICAL STARTUP ERROR: {str(e)}")

# Workflow ဖတ်ခြင်း
with open("workflow_api.json", "r") as f:
    workflow_template = json.load(f)

def handler(job):
    try:
        job_input = job["input"]
        prompt_text = job_input.get("prompt", "A beautiful landscape")
        workflow = json.loads(json.dumps(workflow_template))

        # Node 58 update
        if "58" in workflow:
            workflow["58"]["inputs"]["value"] = prompt_text

        # Queue prompt
        p = {"prompt": workflow}
        res = requests.post("http://127.0.0.1:8188/prompt", json=p)
        return {"status": "success", "data": res.json()}
    except Exception as e:
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})
