# PyTorch 2.4.0 ကို သုံး၍ AttributeError ကို ဖြေရှင်းခြင်း
FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# လိုအပ်သော System Packages များ သွင်းခြင်း
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ComfyUI ကို Clone လုပ်ခြင်း
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

# Dependencies များ သွင်းခြင်း
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install runpod requests websocket-client

# --- NETWORK VOLUME နှင့် မော်ဒယ်များကို ချိတ်ဆက်ခြင်း ---
# RunPod Default Path ဖြစ်သော /runpod-volume ကို သုံးထားပါသည်
RUN rm -rf /comfyui/models && ln -s /runpod-volume/ComfyUI/models /comfyui/models

# သင့်ဖိုင်များကို ကူးထည့်ခြင်း
COPY workflow_api.json /comfyui/workflow_api.json
COPY handler.py /comfyui/handler.py

# Handler ကို စတင်ခြင်း
CMD [ "python", "-u", "handler.py" ]
