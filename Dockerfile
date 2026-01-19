FROM runpod/pytorch:2.1.0-py3.10-cuda12.1.1-devel-ubuntu22.04
WORKDIR /app
RUN git clone https://github.com/comfyanonymous/ComfyUI.git .
RUN pip install --no-cache-dir -r requirements.txt && pip install runpod requests
COPY image_z_image_turbo.json /app/image_z_image_turbo.json
COPY handler.py /app/handler.py
CMD ["python", "-u", "handler.py"]
