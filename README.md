# Flux on ComfyUI Modal App

This is a small script to run ComfyUI within a Modal container. It includes the FLUX_Q8.gguf model and various additional nodes and models for enhanced functionality.

## Features

* **FLUX_Q8.gguf Model:** High-quality quanitized model.
* **VAE and CLIP Models:** Necessary components for image generation.
* **XLabs ControlNet Node and Models:** For advanced control over image generation.
* **CR Apply Lora Stack Node:** Useful for managing and applying Lora models.
* **Optional Loras:** Includes several optional Loras for different styles and effects.
* **Modal Integration:** Runs seamlessly within a Modal container, allowing for easy deployment and scaling.

## Requirements

* **Modal Account:** You'll need a Modal account to deploy and run this app. Sign up for free at [https://modal.com/](https://modal.com/).
* **Modal CLI:** Install the Modal CLI using `pip install modal-client`.


## Customization

* **Optional Loras:** You can comment out or add more Lora downloads in the `comfyui-flux.py` file.
* **GPU:** Change the `gpu` parameter in the `@app.function` decorator to select a different GPU type (e.g., `gpu="T4"`).
* **Additional Nodes:** Add more `run_commands` layers to install additional ComfyUI nodes.

## Important Notes

* **Concurrency:** The app is configured with a concurrency limit of 1 to prevent resource conflicts. Adjust this if needed.
* **Timeout:** The function has a timeout of 3200 seconds. Increase this if you encounter timeouts with long-running generation tasks.

## Running the App

1. **Set up Virtual Environment:**
   - Open a terminal in the directory where you want to set up the virtual environment.
   - Run the following commands:
     ```bash
     python -m venv modal  # Or python3 -m venv modal
     cd modal && . bin/activate
     ```

2. **Run with Modal:**
   - Make sure you are inside the activated virtual environment (you should see `(modal)` at the beginning of your terminal prompt).
   - Run the following command:
     ```bash
     modal serve comfyui-flux.py  
     ```
## Using ComfyUI Commands

This script utilizes `comfy-cli` for managing ComfyUI. For more information on available commands and their usage, please refer to the official `comfy-cli` repository:

[https://github.com/Comfy-Org/comfy-cli](https://github.com/Comfy-Org/comfy-cli)
## Contributing

Contributions are welcome! Feel free to open issues or pull requests.
