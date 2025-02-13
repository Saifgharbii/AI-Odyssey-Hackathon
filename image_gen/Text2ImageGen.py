from diffusers import StableDiffusionPipeline
import torch

def generate_image(prompt, model_path="./AI Models/Text2Image/stable-diffusion-v1-5", output_path="output.png"):
    """
    Generates an image from a text prompt using Stable Diffusion.
    
    Parameters:
        prompt (str): The text prompt for image generation.
        model_path (str): Path to the pre-trained model.
        output_path (str): Path to save the generated image.
    """
    # Load the pipeline
    pipe = StableDiffusionPipeline.from_pretrained(model_path, torch_dtype=torch.float16)
    pipe = pipe.to("cuda")
    
    # Generate the image
    image = pipe(prompt).images[0]
    
    # Save the image
    image.save(output_path)
    print(f"Image saved to {output_path}")
    
# Example usage:
# generate_image("a photo of an astronaut riding a horse on Mars")
