import sys
sys.path.append('..')
import argparse

import torch
from PIL import Image
from transformers import T5EncoderModel, T5Tokenizer
from diffusers import (
    CogVideoXDDIMScheduler,
    AutoencoderKLCogVideoX,
    CogVideoXTransformer3DModel
)
from diffusers.utils import export_to_video
from . import img2vid_pipeline

@torch.no_grad()
def generate_video(
    prompt: str,
    image_path: str,
    model_path: str = "../AI Models/Text-Image2Video/cogvideox-2b-img2vid",
    lora_path: str = None,
    lora_rank: int = 128,
    output_path: str = "./output.mp4",
    num_inference_steps: int = 50,
    guidance_scale: float = 6.0,
    num_videos_per_prompt: int = 1,
    dtype: torch.dtype = torch.bfloat16,
    seed: int = 42,
):
    """
    Generates a video based on the given prompt and saves it to the specified path.

    Parameters:
    - prompt (str): The description of the video to be generated.
    - image_path (str): The video for controlnet processing.
    - model_path (str): The path of the pre-trained model to be used.
    - lora_path (str): The path of the LoRA weights to be used.
    - lora_rank (int): The rank of the LoRA weights.
    - output_path (str): The path where the generated video will be saved.
    - num_inference_steps (int): Number of steps for the inference process. More steps can result in better quality.
    - guidance_scale (float): The scale for classifier-free guidance. Higher values can lead to better alignment with the prompt.
    - num_videos_per_prompt (int): Number of videos to generate per prompt.
    - dtype (torch.dtype): The data type for computation (default is torch.bfloat16).
    - seed (int): The seed for reproducibility.
    """

    # 1.  Load the pre-trained CogVideoX pipeline with the specified precision (bfloat16).
    tokenizer = T5Tokenizer.from_pretrained(
        model_path, subfolder="tokenizer"
    )
    text_encoder = T5EncoderModel.from_pretrained(
        model_path, subfolder="text_encoder"
    )
    transformer = CogVideoXTransformer3DModel.from_pretrained(
        model_path, subfolder="transformer"
    )
    vae = AutoencoderKLCogVideoX.from_pretrained(
        model_path, subfolder="vae"
    )
    scheduler = CogVideoXDDIMScheduler.from_pretrained(
        model_path, subfolder="scheduler"
    )

    pipe = img2vid_pipeline.CogVideoXImg2VidPipeline(
        tokenizer=tokenizer,
        text_encoder=text_encoder,
        transformer=transformer,
        vae=vae,
        scheduler=scheduler,
    )
    image = Image.open(image_path).convert("RGB")

    # 2. Set Scheduler.
    pipe.scheduler = CogVideoXDDIMScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")

    # 3. Set the precision and enable CPU offloading.
    pipe = pipe.to(dtype=dtype)
    pipe.enable_model_cpu_offload()
    pipe.enable_sequential_cpu_offload()

    # 4. Generate the video frames based on the prompt.
    # `num_frames` is the Number of frames to generate.
    # This is the default value for 6 seconds video and 8 fps and will plus 1 frame for the first frame and 49 frames.
    video_generate = pipe(
        image=image,
        prompt=prompt,
        num_videos_per_prompt=num_videos_per_prompt,  # Number of videos to generate per prompt
        num_inference_steps=num_inference_steps,  # Number of inference steps
        num_frames=49,  # Number of frames to generate，changed to 49 for diffusers version `0.30.3` and after.
        use_dynamic_cfg=False,  # This id used for DPM Sechduler, for DDIM scheduler, it should be False
        guidance_scale=guidance_scale,
        generator=torch.Generator().manual_seed(seed),  # Set the seed for reproducibility
    ).frames[0]

    # 5. Export the generated frames to a video file. fps must be 8 for original video.
    export_to_video(video_generate, output_path, fps=8)