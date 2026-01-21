# PyTorch Version မြှင့်ထားသော Image ကို သုံးပါ
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git wget libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

# နောက်ဆုံးပေါ် requirements များသွင်းခြင်း
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install runpod requests websocket-client

# --- NETWORK VOLUME နှင့် ချိတ်ဆက်ခြင်း ---
RUN rm -rf /comfyui/models && ln -s /runpod-slim/ComfyUI/models /comfyui/models

COPY workflow_api.json /comfyui/workflow_api.json
COPY handler.py /comfyui/handler.py

CMD [ "python", "-u", "handler.py" ]
