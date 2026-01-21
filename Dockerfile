FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git wget libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# ComfyUI ကို Clone လုပ်ခြင်း
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

RUN pip install --upgrade pip && pip install -r requirements.txt && pip install runpod requests websocket-client

# --- အရေးကြီးသောအပိုင်း ---
# Folder အဟောင်းကို ဖျက်ပြီး Symlink အသစ်လုပ်ခြင်း
RUN rm -rf /comfyui/models && mkdir -p /runpod-volume/ComfyUI/models
RUN ln -s /runpod-volume/ComfyUI/models /comfyui/models

COPY workflow_api.json /comfyui/workflow_api.json
COPY handler.py /comfyui/handler.py

# ဖိုင်တွေ ရှိမရှိ အတည်ပြုခြင်း
RUN ls -l /comfyui/handler.py && ls -l /comfyui/workflow_api.json

CMD [ "python", "-u", "handler.py" ]
