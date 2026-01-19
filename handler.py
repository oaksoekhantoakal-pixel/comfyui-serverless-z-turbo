import runpod
import json
import requests
import subprocess
import time
import os

# Start ComfyUI Background Process
subprocess.Popen(["python", "main.py", "--high-vram", "--listen", "127.0.0.1"])

def handler(event):
    job_input = event['input']
    prompt_text = job_input.get("prompt", "a stunning visual")
    denoise_val = job_input.get("denoise", 1.0)

    with open("image_z_image_turbo.json", "r") as f:
        workflow = json.load(f)

    # Automatically updated IDs
    workflow["57:27"]["inputs"]["text"] = prompt_text
    workflow["57:3"]["inputs"]["denoise"] = denoise_val

    # API Call to Local ComfyUI
    response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
    return response.json()

runpod.serverless.start({"handler": handler})
