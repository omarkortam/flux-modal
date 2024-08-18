import json
import subprocess
import uuid
from pathlib import Path
from typing import Dict

import modal

image = (  # build up a Modal Image to run ComfyUI, step by step
    modal.Image.debian_slim(  # start from basic Linux with Python
        python_version="3.10.6"
    )
    .apt_install("git")  # install git to clone ComfyUI
    .apt_install("nano")  # install git to clone ComfyUI
    .pip_install("comfy-cli")  # install comfy-cli
    .run_commands(  # use comfy-cli to install the ComfyUI repo and its dependencies
        "comfy --skip-prompt install --nvidia",
    )
    .run_commands(  # download the flux model
        "comfy --skip-prompt model download --url https://huggingface.co/lllyasviel/flux1-dev-bnb-nf4/resolve/main/flux1-dev-bnb-nf4-v2.safetensors --relative-path models/checkpoints"
    )
    .run_commands(  # download the flux fp8 model
        "comfy --skip-prompt model download --url  https://huggingface.co/lllyasviel/flux1_dev/resolve/main/flux1-dev-fp8.safetensors --relative-path models/checkpoints"
    )
    .run_commands(#GGUF model
    "comfy --skip-prompt model download --url https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q8_0.gguf  --relative-path models/unet",
    )
    .run_commands(  # download the vae model
        "comfy --skip-prompt model download --url https://huggingface.co/black-forest-labs/FLUX.1-schnell/resolve/main/ae.safetensors --relative-path models/vae"
    )
    .run_commands(  # download the lora anime 
        "comfy --skip-prompt model download --url https://civitai.com/models/640247/mjanimefluxlora?modelVersionId=716064 --relative-path models/loras --set-civitai-api-token 660761c07cb90e21999bb3637e78e007"
    )
    .run_commands(  # download the cliper model
        "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors --relative-path models/clip",
        "comfy --skip-prompt model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip"

    )
    .run_commands(  # download a custom node
        "comfy node install image-resize-comfyui",
        "comfy node install https://github.com/comfyanonymous/ComfyUI_bitsandbytes_NF4"
    )
    # can layer additional models and custom node downloads as needed
    .run_commands( #related to control net xlabs 
        "comfy node install https://github.com/XLabs-AI/x-flux-comfyui"
    )
    .run_commands( #download controlnet v3 xlabs ai
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-depth-v3/resolve/main/flux-depth-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-canny-v3/resolve/main/flux-canny-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-controlnet-hed-v3/resolve/main/flux-hed-controlnet-v3.safetensors --relative-path models/xlabs/controlnets",
    )
    .run_commands( #xlab loras
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/art_lora_comfy_converted.safetensors --relative-path models/xlabs/loras",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/anime_lora_comfy_converted.safetensors --relative-path models/xlabs/loras",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/disney_lora_comfy_converted.safetensors --relative-path models/xlabs/loras",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/mjv6_lora_comfy_converted.safetensors --relative-path models/xlabs/loras",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/realism_lora_comfy_converted.safetensors --relative-path models/xlabs/loras",
        "comfy --skip-prompt model download --url https://huggingface.co/XLabs-AI/flux-lora-collection/resolve/main/scenery_lora_comfy_converted.safetensors --relative-path models/xlabs/loras"
    )
    .run_commands( #someloras
        "comfy --skip-prompt model download --url https://huggingface.co/alvdansen/frosting_lane_flux/resolve/main/flux_dev_frostinglane_araminta_k.safetensors --relative-path models/loras",
        "comfy --skip-prompt model download --url https://civitai.com/models/654175/simpsons-style-flux-dev?modelVersionId=731876 --relative-path models/loras --set-civitai-api-token 660761c07cb90e21999bb3637e78e007",
    )
    .run_commands( #install control net requried for above
        "comfy node install https://github.com/Fannovel16/comfyui_controlnet_aux"
    )
    #.run_commands(
    #    "cd /root/comfy/ComfyUI/custom_nodes",
    #    "git clone https://github.com/XLabs-AI/x-flux-comfyui.git",
    #    "cd x-flux-comfyui && "
    #    "python setup.py",
    #)
    .run_commands( #CR APPLY lora stack
        "comfy node install https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes"
    )
    .run_commands( # gguf node required for q8 model
        "comfy node install https://github.com/city96/ComfyUI-GGUF"
    )

)

app = modal.App(name="example-comfyui", image=image)
@app.function(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=30,
    timeout=3200,
    gpu="a10g",
)
@modal.web_server(8000, startup_timeout=60)
def ui():
    subprocess.Popen("comfy launch -- --listen 0.0.0.0 --port 8000", shell=True)

'''
@app.cls(
    allow_concurrent_inputs=10,
    concurrency_limit=1,
    container_idle_timeout=300,
    gpu="a10g
    
)
class ComfyUI:
    @modal.enter()
    def launch_comfy_background(self):
        cmd = "comfy launch --background"
        subprocess.run(cmd, shell=True, check=True)

    @modal.method()
    def infer(self, workflow_path: str = "/root/workflow_api.json"):
        # runs the comfy run --workflow command as a subprocess
        cmd = f"comfy run --workflow {workflow_path} --wait"
        subprocess.run(cmd, shell=True, check=True)

        # completed workflows write output images to this directory
        output_dir = "/root/comfy/ComfyUI/output"
        # looks up the name of the output image file based on the workflow
        workflow = json.loads(Path(workflow_path).read_text())
        file_prefix = [
            node.get("inputs")
            for node in workflow.values()
            if node.get("class_type") == "SaveImage"
        ][0]["filename_prefix"]

        # returns the image as bytes
        for f in Path(output_dir).iterdir():
            if f.name.startswith(file_prefix):
                return f.read_bytes()

    @modal.web_endpoint(method="POST")
    def api(self, item: Dict):
        from fastapi import Response

        workflow_data = json.loads(
            (Path(__file__).parent / "workflow_api.json").read_text()
        )

        # insert the prompt
        workflow_data["3"]["inputs"]["text"] = item["prompt"]

        # give the output image a unique id per client request
        client_id = uuid.uuid4().hex
        workflow_data["11"]["inputs"]["filename_prefix"] = client_id

        # save this updated workflow to a new file
        new_workflow_file = f"{client_id}.json"
        json.dump(workflow_data, Path(new_workflow_file).open("w"))

        # run inference on the currently running container
        img_bytes = self.infer.local(new_workflow_file)

        return Response(img_bytes, media_type="image/jpeg")

'''