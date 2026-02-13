# ml_scripts/image_gen.py
import sys
import os
import random # Import random for default seed generation
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

def generate_image(prompt, content_id, requested_seed):
    """
    Generates an image using Stable Diffusion, optionally using a specific seed for consistency.
    The function prints the final file path and the seed used to stdout.
    """
    
    # 1. Determine the final seed (Logic is correct)
    if requested_seed and requested_seed.lower() != "random":
        try:
            final_seed = int(requested_seed) 
        except ValueError:
            final_seed = random.randint(1, 1000000000)
    else:
        final_seed = random.randint(1, 1000000000)
    
    torch.manual_seed(final_seed)
    random.seed(final_seed)

    # 2. Load the Stable Diffusion Model (Logic is correct)
    try:
        # Using float16 is essential for GPU speed
        pipeline = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
    except Exception as e:
        sys.stderr.write(f"Error loading Stable Diffusion model: {e}\n")
        sys.exit(1)

    # 3. Move pipeline to CUDA GPU (Logic is correct)
    try:
        if torch.cuda.is_available():
            pipeline.to("cuda")
            sys.stderr.write("Using NVIDIA CUDA GPU for image generation. EXPECT FASTER SPEED!\n")
        else:
            pipeline.to("cpu")
            sys.stderr.write("NVIDIA CUDA GPU not available. Falling back to CPU (VERY SLOW).\n")
    except Exception as e:
        sys.stderr.write(f"Error with CUDA configuration: {e}\nFalling back to CPU (VERY SLOW).\n")
        pipeline.to("cpu")


    try:
        # Negative prompt includes crucial terms for quality
        negative_prompt = "blurry, low quality, bad anatomy, ugly, disfigured, poorly drawn face, bad hands, mutated, washed out colors, low contrast, text, signature" # <-- Extended list

        # ⭐ OPTIMIZED PARAMETERS FOR MAX QUALITY AND REALISM ⭐
        generator = torch.Generator(pipeline.device).manual_seed(final_seed) 
        
        image = pipeline(
            prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=50,      # <-- INCREASED: Provides maximum detail refinement (was 40)
            guidance_scale=11.5,         # <-- TUNED: Forces strong adherence to prompt, boosting CLIP score (was 12.0/too high)
            generator=generator
        ).images[0]
    except Exception as e:
        sys.stderr.write(f"Error during image generation: {e}\n")
        sys.exit(1)

    # 4. Save the Image (Logic is correct)
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'images')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = f"image_{content_id}_{final_seed}.png"
    output_path = os.path.join(output_dir, output_filename)
    relative_path = f"storage/images/{output_filename}"

    try:
        image.save(output_path)
    except Exception as e:
        sys.stderr.write(f"Error saving generated image: {e}\n")
        sys.exit(1)

    # 5. CRITICAL: Print the file path AND the final seed for Node.js to parse
    print(f"{relative_path}:{final_seed}")
    
# --- Execution Block (Logic is correct) ---

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        prompt_arg = sys.argv[1]
        content_id_arg = sys.argv[2]
        requested_seed_arg = sys.argv[3] if len(sys.argv) > 3 else None
        
        generate_image(prompt_arg, content_id_arg, requested_seed_arg)
    else:
        sys.stderr.write("Usage: python image_gen.py <prompt> <content_id> [seed_value]\n")
        sys.exit(1)


