FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# ၁။ လိုအပ်သော System Package များ
RUN apt-get update && apt-get install -y \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ၂။ ComfyUI ကို Clone လုပ်ခြင်း
RUN git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui

# ၃။ Python Requirements များ
WORKDIR /comfyui
RUN pip install -r requirements.txt
RUN pip install runpod requests

# ၄။ Model များ Download ဆွဲခြင်း (နေရာမှန်သို့)
# UNET (z_image_turbo_bf16)
RUN wget -O models/unet/z_image_turbo_bf16.safetensors "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/diffusion_models/z_image_turbo_bf16.safetensors"

# CLIP (qwen_3_4b)
RUN wget -O models/clip/qwen_3_4b.safetensors "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors"

# VAE (ae.safetensors)
RUN wget -O models/vae/ae.safetensors "https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/vae/ae.safetensors"

# ၅။ ဖိုင်များကူးထည့်ခြင်း
COPY image_z_image_turbo.json /comfyui/workflow.json
COPY handler.py /comfyui/handler.py

# ၆။ Handler ကို Run ခြင်း
CMD [ "python", "-u", "handler.py" ]
