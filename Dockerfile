FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git wget libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

# ComfyUI ကို Clone လုပ်ခြင်း
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

# လိုအပ်သော library များသွင်းခြင်း
RUN pip install -r requirements.txt
RUN pip install runpod requests websocket-client

# --- NETWORK VOLUME နှင့် မော်ဒယ်များကို ချိတ်ဆက်ခြင်း ---
# ComfyUI ရဲ့ models folder တစ်ခုလုံးကို ဖျက်ပြီး သင့် Volume ထဲက folder နဲ့ ချိတ်ပါမယ်
RUN rm -rf /comfyui/models && ln -s /runpod-slim/ComfyUI/models /comfyui/models

# သင့်ရဲ့ Workflow နှင့် Handler ဖိုင်များကို ကူးထည့်ခြင်း
COPY workflow_api.json /comfyui/workflow_api.json
COPY handler.py /comfyui/handler.py

CMD [ "python", "-u", "handler.py" ]
