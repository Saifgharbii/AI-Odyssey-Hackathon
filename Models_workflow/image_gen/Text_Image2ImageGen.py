import os
import torch
from PIL import Image
from huggingface_hub import hf_hub_download
from xflux.src.flux.xflux_pipeline import XFluxPipeline

def download_model_and_lora(model_dir, lora_dir, lora_repo_id, lora_name):
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(lora_dir, exist_ok=True)
    
    lora_path = os.path.join(lora_dir, lora_name)
    if not os.path.exists(lora_path):
        print(f"Downloading LoRA weights: {lora_name}")
        lora_path = hf_hub_download(repo_id=lora_repo_id, filename=lora_name, cache_dir=lora_dir)
    else:
        print("LoRA weights already downloaded.")
    
    return lora_path

def generate_image(prompt, image : Image.Image, model_dir="../AI Models/Text2Image/flux-dev-fp8", lora_dir="../AI Models/Text2Image/flux-dev-fp8", lora_repo_id="XLabs-AI/flux-lora-collection", lora_name="realism_lora.safetensors", guidance=4, width=1024, height=1024, num_steps=25, seed=123456789, save_path="results"):
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6e9 else "cpu"
    offload = device == "cuda" and torch.cuda.get_device_properties(0).total_memory < 8e9
    
    print(f"Using device: {device} (Offload: {offload})")
    os.makedirs(save_path, exist_ok=True)
    
    # Download LoRA if needed
    lora_path = download_model_and_lora(model_dir, lora_dir, lora_repo_id, lora_name)
    
    # Load the model pipeline
    xflux_pipeline = XFluxPipeline("flux-dev-fp8", device, offload)
    xflux_pipeline.set_lora(lora_path, lora_repo_id, lora_name, lora_weight=0.9)
        
    # Generate image
    result = xflux_pipeline(prompt=prompt, controlnet_image=image, width=width, height=height, guidance=guidance, num_steps=num_steps, seed=seed)
    
    return result
