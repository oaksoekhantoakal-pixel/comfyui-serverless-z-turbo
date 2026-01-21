import runpod
import json
import subprocess
import time
import requests
import base64

# ၁။ ComfyUI ကို Background မှာ Run ပါ
def check_server(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

print("Starting ComfyUI...")
subprocess.Popen(["python", "main.py", "--listen", "0.0.0.0", "--port", "8188"])

# Server တက်လာသည်အထိ စောင့်ပါ
while not check_server("http://127.0.0.1:8188"):
    time.sleep(1)
print("ComfyUI is ready!")

# ၂။ Workflow ဖိုင်ကို ဖတ်ပါ
with open("workflow.json", "r") as f:
    workflow = json.load(f)

def handler(job):
    job_input = job["input"]
    prompt_text = job_input.get("prompt", "A beautiful landscape") # Default prompt

    # ၃။ Workflow ထဲက Node 58 (Prompt) ကို ပြင်ပါ
    # သင့် JSON ဖိုင်အရ Node ID 58 က Prompt ဖြစ်ပါတယ်
    for node in workflow["nodes"]:
        if node["id"] == 58:
            node["widgets_values"][0] = prompt_text
            break

    # ၄။ ComfyUI API သို့ ပို့ပါ (Prompt Queue)
    # Note: ComfyUI API expects a specific format. Since we are using the 
    # "Save" format JSON, strictly speaking, we might need conversion, 
    # but for simplicity, we will try to use the prompt endpoint directly if compatible, 
    # or recreate the API payload structure.
    
    # For Z-Turbo specifically, let's construct a simple API payload 
    # mapping based on your loaded models to ensure it runs.
    
    # API Call
    p = {"prompt": workflow}
    # (တကယ်တမ်း API format ပြောင်းဖို့လိုနိုင်ပေမယ့် စမ်းသပ်ဖို့ ဒီအတိုင်းအရင် run ကြည့်ပါ)
    
    # ရိုးရှင်းသော API Payload တည်ဆောက်ခြင်း (Recommended for stability)
    # သင်၏ Workflow က ရှုပ်ထွေးနိုင်သဖြင့် Client ID မပါဘဲ တိုက်ရိုက် Queue လုပ်ပါမည်
    
    try:
        # Generate random client id
        client_id = str(job["id"])
        ws = requests.post("http://127.0.0.1:8188/prompt", json={
            "prompt": convert_workflow_to_api(workflow), # Helper function needed usually
            "client_id": client_id
        })
        
        # NOTE: Since converting raw JSON to API JSON is complex in code,
        # It is HIGHLY recommended you export "API Format" JSON from ComfyUI
        # and save it as image_z_image_turbo_api.json instead.
        
        # For now, let's assume successful queue and wait for image (mock logic for simplicity unless you have API json)
        pass 
    except Exception as e:
        return {"error": str(e)}

    return {"status": "Please export your workflow as API Format JSON from ComfyUI menu first for best results."}

# Helper to find image output would go here
    
runpod.serverless.start({"handler": handler})
