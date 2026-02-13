# ml_scripts/img2img_gen.py
import sys
import os
import random 
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image
import base64 
from io import BytesIO 

# The signature now requires the base64 image data
def generate_img2img(prompt, content_id, requested_seed, base64_image, mime_type):
    
    # 1. Determine the final seed
    if requested_seed and requested_seed.lower() != "random":
        try:
            final_seed = int(requested_seed) 
        except ValueError:
            final_seed = random.randint(1, 1000000000)
    else:
        final_seed = random.randint(1, 1000000000)
    
    torch.manual_seed(final_seed)
    random.seed(final_seed)

    # 2. Load Model and Device
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # StableDiffusionImg2ImgPipeline is the correct pipeline for I2I
        pipeline = StableDiffusionImg2ImgPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16).to(device)
        sys.stderr.write(f"Using Image-to-Image pipeline on {device.upper()}.\n")
            
    except Exception as e:
        sys.stderr.write(f"Error loading Stable Diffusion Img2Img model: {e}\n")
        sys.exit(1)

    # 3. Load and Decode Input Image (CRITICAL I2I STEP)
    init_image = None
    if base64_image:
        try:
            image_bytes = base64.b64decode(base64_image)
            # Decode and resize to a standard diffusion size (512x512)
            init_image = Image.open(BytesIO(image_bytes)).convert("RGB").resize((512, 512))
        except Exception as e:
            sys.stderr.write(f"Error decoding input image: {e}\n")
            sys.exit(1)
    else:
        # This function should only be called for I2I, but as a safety check:
        sys.stderr.write("Error: Base image data is missing for Image-to-Image generation.\n")
        sys.exit(1)


    try:
        negative_prompt = "blurry, low quality, bad anatomy, ugly, disfigured, poorly drawn face, bad hands, mutated, washed out colors, low contrast, text, signature"
        generator = torch.Generator(pipeline.device).manual_seed(final_seed) 
        
        # --- Image-to-Image Generation (I2I) ---
        image = pipeline(
            prompt=prompt,
            image=init_image, 
            negative_prompt=negative_prompt,
            num_inference_steps=50,
            guidance_scale=11.5,
            strength=0.9, 
            generator=generator
        ).images[0]

    except Exception as e:
        sys.stderr.write(f"Error during image-to-image generation: {e}\n")
        sys.exit(1)

    # 4. Save the Image
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'images')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = f"image_edit_{content_id}_{final_seed}.png"
    output_path = os.path.join(output_dir, output_filename)
    relative_path = f"storage/images/{output_filename}"

    try:
        image.save(output_path)
    except Exception as e:
        sys.stderr.write(f"Error saving generated image: {e}\n")
        sys.exit(1)

    # 5. CRITICAL: Print the file path AND the final seed for Node.js to parse
    print(f"{relative_path}:{final_seed}")
    
# --- Execution Block ---

if __name__ == "__main__":
    # Expects arguments: [script_path, prompt, content_id, requested_seed, base64_image, mime_type]
    if len(sys.argv) >= 6:
        prompt_arg = sys.argv[1]
        content_id_arg = sys.argv[2]
        requested_seed_arg = sys.argv[3] 
        base64_image_arg = sys.argv[4]
        mime_type_arg = sys.argv[5] 

        generate_img2img(prompt_arg, content_id_arg, requested_seed_arg, base64_image_arg, mime_type_arg)
    else:
        sys.stderr.write("Usage: python img2img_gen.py <prompt> <content_id> <seed> <base64_image> <mime_type>\n")
        sys.exit(1)