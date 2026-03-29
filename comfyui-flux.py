import subprocess
import modal

HF_TOKEN = "YOUR HUGGINGFACE API KEY"
CIVITAI_API = "YOUR CIVITAI API KEY"

flux = (  # Download image layers to run FLUX_Q8.gguf model
    modal.Image.debian_slim(  #this starts with a basic and supported python version
        python_version="3.11"
    )
    .apt_install("git")  # install git
    .apt_install("nano")  # install to have a minimal text editor if we wanted to change something minimal
    .pip_install("comfy-cli")  # install comfy-cli
    .run_commands(  # use comfy-cli to install the ComfyUI repo and its dependencies
        "comfy --skip-prompt install --nvidia",
    )
    .run_commands(# download the GGUF Q8 model
    f"comfy --skip-prompt model download --url https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q8_0.gguf  --relative-path models/unet --set-hf-api-token {HF_TOKEN}",
    )
    .run_commands( # gguf node required for q8 model
        "comfy node install https://github.com/city96/ComfyUI-GGUF"
    )
    .run_commands(  # download the vae model required to use with the gguf model
        f"comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors --relative-path models/vae --set-hf-api-token {HF_TOKEN}"
    )
    .run_commands(  # download the cliper model required to use with GGUF model
        f"comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip --set-hf-api-token {HF_TOKEN}",
    )
    .run_commands(  # download the lora anime -- optional you can disbale
        f"comfy --skip-prompt model download --url https://civitai.com/models/640247/mjanimefluxlora?modelVersionId=716064 --relative-path models/loras --set-civitai-api-token {CIVITAI_API}"
    )
    # put down here additional layers to your likings below
    .run_commands( # XLabs ControlNet node 
        "comfy node install https://github.com/XLabs-AI/x-flux-comfyui"
    )
    .run_commands( #download controlnet v3 xlabs ai
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/xlabs/controlnets --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-canny-v3/resolve/main/flux-canny-controlnet-v3.safetensors --relative-path models/xlabs/controlnets --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-hed-v3/resolve/main/flux-hed-controlnet-v3.safetensors --relative-path models/xlabs/controlnets --set-hf-api-token {HF_TOKEN}",
    )
    .run_commands( #install control net requried for above xlabs
        "comfy node install https://github.com/Fannovel16/comfyui_controlnet_aux"
    )
    .run_commands( #xlab loras --optional
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/art_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/anime_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/disney_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/mjv6_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/realism_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/scenery_lora_comfy_converted.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}"
    )
    .run_commands( #someloras optional
        f"comfy --skip-prompt model download --url https://huggingface.co/alvdansen/frosting_lane_flux/resolve/main/flux_dev_frostinglane_araminta_k.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
        f"comfy --skip-prompt model download --url https://huggingface.co/multimodalart/flux-tarot-v1/resolve/main/flux_tarot_v1_lora.safetensors --relative-path models/loras --set-hf-api-token {HF_TOKEN}",
    )
    .run_commands( #CR APPLY lora stack -- useful node -- optional
        "comfy node install https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes"
    )

)

app = modal.App(name="flux-comfyui", image=flux)
@app.function(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=30,
    timeout=3200,
    gpu="a10g", # here you can change the gpu, i recommend either a10g or T4
)
@modal.web_server(8000, startup_timeout=60)
def ui():
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)
