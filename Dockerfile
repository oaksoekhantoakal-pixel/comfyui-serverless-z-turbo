FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y git wget libgl1-mesa-glx libglib2.0-0 && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui
WORKDIR /comfyui

RUN pip install --upgrade pip && pip install -r requirements.txt && pip install runpod requests

# Linking your network volume to ComfyUI models folder
RUN rm -rf /comfyui/models && ln -s /runpod-volume/ComfyUI/models /comfyui/models

COPY workflow_api.json /comfyui/workflow_api.json
COPY handler.py /comfyui/handler.py

CMD [ "python", "-u", "handler.py" ]
