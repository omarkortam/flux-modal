import subprocess

import modal

PORT = 8000
a1111_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install(
        "wget",
        "git",
        "libgl1",
        "libglib2.0-0",
        "google-perftools",  # For tcmalloc
    )
    .env({"LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4"})
    .run_commands(
        "git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git /webui",
        "python -m venv /webui/venv",
        "cd /webui && . venv/bin/activate && pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121 && "
        + "python -c 'from modules import launch_utils; launch_utils.prepare_environment()'",
        gpu="a10g",
    )
    .run_commands(
        "cd /webui/models/Stable-diffusion/ && wget -O YM.safetensors https://huggingface.co/lllyasviel/flux1_dev/resolve/main/flux1-dev-fp8.safetensors ",
    )
    .run_commands(
        "cd /webui/models/VAE/ && wget -O vv.safetensors https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors",
        "mkdir -p /webui/models/Lora/",
        "cd /webui/models/Lora/ && wget -O frostinglan.safetensors https://huggingface.co/alvdansen/frosting_lane_flux/resolve/main/flux_dev_frostinglane_araminta_k.safetensors",

    )
    .run_commands(
        "mkdir -p /webui/models/ControlNet/",
        "cd /webui/models/ControlNet/ && wget -O flux-depth-controlnet-v3.safetensors https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors",

    )  
    .run_commands(
        "cd /webui/models/Lora/ && wget -O koda.safetensors https://huggingface.co/alvdansen/flux-koda/resolve/main/araminta_k_flux_koda.safetensors",

    )
    .run_commands( #civitai user &token=API
        "cd /webui/models/Lora/ && wget -O buttandbeavies.safetensors 'https://civitai.com/api/download/models/733525?type=Model&format=SafeTensor&token=caf97f3c450fcc0d5b10bb6bf9babfd0'",
        "cd /webui/models/Lora/ && wget -O MJanime.safetensors 'https://civitai.com/api/download/models/716064?type=Model&format=SafeTensor&token=caf97f3c450fcc0d5b10bb6bf9babfd0'",
    )  
    #.run_commands(
    #    "cd /webui/models/Lora/ && wget -O <NAME>.safetensors <URL>",

    #)
  #  .run_commands(
   #     "cd /webui && . venv/bin/activate && "
    #    + "python -c 'from modules import shared_init, initialize; shared_init.initialize(); initialize.initialize()'",
     #   gpu="a10g",
    #)
)

app = modal.App("example-a1111-webui", image=a1111_image)
@app.function(
    gpu="T4",
    cpu=2,
    memory=1024,
    timeout=3600,
    # Allows 100 concurrent requests per container.
    allow_concurrent_inputs=100,
    # Keep at least one instance of the server running.
    keep_warm=1,
)
@modal.web_server(port=PORT, startup_timeout=180)
def run():
    START_COMMAND = f"""
cd /webui && \
. venv/bin/activate && \
    chmod +x /webui/webui.sh &&\
    /webui/webui.sh -f\
        --skip-prepare-environment \
        --no-gradio-queue \
        --listen \
        --port {PORT}
"""
    subprocess.Popen(START_COMMAND, shell=True)
