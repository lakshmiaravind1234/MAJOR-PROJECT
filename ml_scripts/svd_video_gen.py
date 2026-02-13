import sys
import os
import torch
import random
from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
from diffusers.utils import export_to_video

def generate_svd_video(prompt, content_id):
    # 1. Setup Device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sys.stderr.write(f"Using device: {device}\n")

    try:
        # 2. Load Base Image Model (Phase 1)
        sys.stderr.write("Loading Phase 1: Image Model...\n")
        pipeline = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        pipeline.to(device)

        # Generate the starting image
        final_seed = random.randint(1, 1000000000)
        generator = torch.Generator(device).manual_seed(final_seed)
        
        starting_image = pipeline(
            prompt,
            num_inference_steps=25,
            generator=generator
        ).images[0]

        # 3. CLEAN UP MEMORY BEFORE PHASE 2
        del pipeline # Remove image model from RAM/VRAM
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        # 4. Load Video Model (Phase 2)
        sys.stderr.write("Loading Phase 2: Video Model...\n")
        svd_pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            variant="fp16" if device == "cuda" else None
        )
        
        if device == "cuda":
            # This is the magic line for lower VRAM (8GB-12GB cards)
            svd_pipeline.enable_model_cpu_offload() 
        else:
            svd_pipeline.to("cpu")

        video_frames = svd_pipeline(
            starting_image,
            num_frames=25, # Reduced from 40 to prevent OOM crash
            decode_chunk_size=4, # Lower chunks = less VRAM
            motion_bucket_id=100,
            fps=7
        ).frames[0]

    except Exception as e:
        sys.stderr.write(f"CRITICAL ERROR: {e}\n")
        sys.exit(1)

    # 5. Save the Video
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'videos')
    os.makedirs(output_dir, exist_ok=True)
    
    output_filename = f"video_{content_id}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    export_to_video(video_frames, output_path)
    print(f"storage/videos/{output_filename}") # Clean path for Node.js

if __name__ == "__main__":
    if len(sys.argv) > 2:
        generate_svd_video(sys.argv[1], sys.argv[2])
    else:
        sys.exit(1)