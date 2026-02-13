# ml_scripts/pdf_to_video.py
import sys
import os
import subprocess
from pdf2image import convert_from_path # New import
import time

def generate_video_from_pdf(pdf_path, content_id):
    # --- Paths and Setup ---
    # !!! IMPORTANT: UPDATE THESE PATHS !!!
    POPPLER_PATH = r"C:\Users\likitha priya\Desktop\major\Major 2 - Copy\poppler-24.02.0\bin" # <--- UPDATE THIS TO YOUR POPPLER BIN PATH
    FFMPEG_EXE_PATH = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" # <--- CONFIRM THIS IS YOUR FFMPEG PATH

    output_video_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'videos')
    temp_frames_dir = os.path.join(os.path.dirname(__file__), '..', 'public', 'uploads', f'temp_pdf_frames_{content_id}')

    if not os.path.exists(output_video_dir):
        os.makedirs(output_video_dir)
    if not os.path.exists(temp_frames_dir):
        os.makedirs(temp_frames_dir)

    output_video_filename = f"video_pdf_{content_id}.mp4"
    output_video_path = os.path.join(output_video_dir, output_video_filename)

    sys.stderr.write(f"Starting PDF to video conversion for: {pdf_path}\n")

    # --- 1. Convert PDF pages to images ---
    images = []
    try:
        sys.stderr.write(f"Converting PDF pages to images. Poppler Path: {POPPLER_PATH}\n")
        # Use convert_from_path with poppler_path
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        sys.stderr.write(f"Successfully converted {len(images)} pages from PDF.\n")
    except Exception as e:
        sys.stderr.write(f"Error converting PDF to images: {e}\n")
        # For debug, print full traceback
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    if not images:
        sys.stderr.write("No images were extracted from the PDF.\n")
        sys.exit(1)

    # Save images to temp directory
    frame_paths = []
    for i, image in enumerate(images):
        frame_filename = f"pdf_frame_{i:03d}.png"
        frame_path = os.path.join(temp_frames_dir, frame_filename)
        try:
            image.save(frame_path, 'PNG')
            frame_paths.append(frame_path)
        except Exception as e:
            sys.stderr.write(f"Error saving image {i} to {frame_path}: {e}\n")
            sys.exit(1)
    
    sys.stderr.write(f"Saved {len(frame_paths)} temporary image frames.\n")

    # --- 2. Combine Images into a Video using FFmpeg ---
    try:
        # Use the sequence of generated PDF frames
        ffmpeg_command = [
            FFMPEG_EXE_PATH,
            '-framerate', '1', # 1 frame per second (each PDF page shown for 1 second)
            '-i', os.path.join(temp_frames_dir, 'pdf_frame_%03d.png'), # Input pattern
            '-c:v', 'libx264', # Video codec
            '-r', '30', # Output video framerate
            '-pix_fmt', 'yuv420p', # Pixel format for compatibility
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p', # Ensure yuv420p
            '-y', # Overwrite output file without asking
            output_video_path
        ]
        sys.stderr.write(f"Running FFmpeg command to combine PDF frames: {' '.join(ffmpeg_command)}\n")
        
        process = subprocess.run(ffmpeg_command, capture_output=True, text=True, check=False)
        
        if process.returncode != 0:
            sys.stderr.write(f"FFmpeg failed with error:\n{process.stderr}\n")
            sys.exit(1)
        else:
            sys.stderr.write(f"FFmpeg stdout:\n{process.stdout}\n")
            sys.stderr.write(f"Video generated at: {output_video_path}\n")
            
    except FileNotFoundError:
        sys.stderr.write("Error: FFmpeg not found at the specified path. Please check FFMPEG_EXE_PATH.\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error during FFmpeg conversion: {e}\n")
        sys.exit(1)
    finally:
        # Clean up temporary frames directory
        for f in frame_paths:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    sys.stderr.write(f"Error cleaning up frame {f}: {e}\n")
        if os.path.exists(temp_frames_dir):
            try:
                os.rmdir(temp_frames_dir) # Remove the directory if empty
            except OSError:
                sys.stderr.write(f"Could not remove temporary directory {temp_frames_dir} (may not be empty).\n")
            except Exception as e:
                sys.stderr.write(f"Error removing temp directory {temp_frames_dir}: {e}\n")

    print(f"storage/videos/{output_video_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        pdf_path_arg = sys.argv[1]
        content_id_arg = sys.argv[2]
        generate_video_from_pdf(pdf_path_arg, content_id_arg)
    else:
        sys.stderr.write("Usage: python pdf_to_video.py <pdf_file_path> <content_id>\n")
        sys.exit(1)