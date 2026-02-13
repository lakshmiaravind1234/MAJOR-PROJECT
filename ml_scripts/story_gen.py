# ml_scripts/story_gen.py
import sys
import os
import torch
from transformers import pipeline

def generate_story(file_path, content_id):
    try:
        # Load a high-quality LLM model (e.g., fine-tuned Mistral)
        llm_pipeline = pipeline(
            "text-generation", 
            model="TheBloke/Mistral-7B-Instruct-v0.2-AWQ", # A good, fast model
            device=0,
            torch_dtype=torch.float16
        )

        sys.stderr.write("LLM pipeline loaded.\n")

    except Exception as e:
        sys.stderr.write(f"Error loading LLM model: {e}\n")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
        
        # Use an improved prompt template for better story quality
        prompt = f"### Instruction:\nWrite a high-quality, creative short story with a clear beginning, middle, and end, based on the following content. The story should be coherent and engaging.\n### Content:\n{file_content}\n### Response:\n"

        story_output = llm_pipeline(
            prompt,
            max_new_tokens=1024, # Increased for a longer, more detailed story
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95
        )

        generated_story = story_output[0]['generated_text']
        
    except Exception as e:
        sys.stderr.write(f"Error during story generation: {e}\n")
        sys.exit(1)

    # Save the generated story to a text file
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'stories')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = f"story_{content_id}.txt"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_story)
        
        # Print the relative path to Node.js
        print(f"storage/stories/{output_filename}")
        
    except Exception as e:
        sys.stderr.write(f"Error saving story: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        file_path_arg = sys.argv[1]
        content_id_arg = sys.argv[2]
        generate_story(file_path_arg, content_id_arg)
    else:
        sys.stderr.write("Usage: python story_gen.py <file_path> <content_id>\n")
        sys.exit(1)
















# # ml_scripts/story_gen.py
# import sys
# import os
# import torch
# from transformers import pipeline

# def generate_story(file_path, content_id):
#     try:
#         # Load the LLM pipeline
#         # Using a model that does not require authentication
#         llm_pipeline = pipeline(
#             "text-generation", 
#             model="microsoft/phi-2",
#             device=0,
#             torch_dtype=torch.float16
#         )

#         sys.stderr.write("LLM pipeline loaded.\n")

#     except Exception as e:
#         sys.stderr.write(f"Error loading LLM model: {e}\n")
#         sys.exit(1)

#     try:
#         # Read the content of the uploaded file
#         with open(file_path, 'r', encoding='utf-8',errors='ignore') as f:
#             file_content = f.read()
        
#         # Craft a prompt for the LLM
#         prompt = f"Based on the following content, write a compelling short story:\n\n{file_content}\n\nStory:"

#         # Generate the story
#         story_output = llm_pipeline(
#             prompt,
#             max_new_tokens=512, # Adjust length of the story
#             do_sample=True,
#             temperature=0.7,
#             top_k=50,
#             top_p=0.95
#         )

#         generated_story = story_output[0]['generated_text']
        
#     except Exception as e:
#         sys.stderr.write(f"Error during story generation: {e}\n")
#         sys.exit(1)

#     # Save the generated story to a text file
#     output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'stories')
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     output_filename = f"story_{content_id}.txt"
#     output_path = os.path.join(output_dir, output_filename)

#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(generated_story)
        
#         # Print the relative path to Node.js
#         print(f"storage/stories/{output_filename}")
        
#     except Exception as e:
#         sys.stderr.write(f"Error saving story: {e}\n")
#         sys.exit(1)

# if __name__ == "__main__":
#     if len(sys.argv) > 2:
#         file_path_arg = sys.argv[1]
#         content_id_arg = sys.argv[2]
#         generate_story(file_path_arg, content_id_arg)
#     else:
#         sys.stderr.write("Usage: python story_gen.py <file_path> <content_id>\n")
#         sys.exit(1)












# # ml_scripts/story_gen.py
# import sys
# import os
# import torch
# from transformers import pipeline

# def generate_story(file_path, content_id):
#     try:
#         # Load the LLM pipeline
#         # Using a model from Hugging Face, e.g., "mistralai/Mistral-7B-Instruct-v0.2"
#         # The 'device=0' will use the first available CUDA GPU
#         llm_pipeline = pipeline(
#             "text-generation", 
#             model="mistralai/Mistral-7B-Instruct-v0.2",
#             device=0,
#             torch_dtype=torch.float16
#         )

#         sys.stderr.write("LLM pipeline loaded.\n")

#     except Exception as e:
#         sys.stderr.write(f"Error loading LLM model: {e}\n")
#         sys.exit(1)

#     try:
#         # Read the content of the uploaded file
#         with open(file_path, 'r', encoding='utf-8') as f:
#             file_content = f.read()
        
#         # Craft a prompt for the LLM
#         prompt = f"Based on the following content, write a compelling short story:\n\n{file_content}\n\nStory:"

#         # Generate the story
#         story_output = llm_pipeline(
#             prompt,
#             max_new_tokens=512, # Adjust length of the story
#             do_sample=True,
#             temperature=0.7,
#             top_k=50,
#             top_p=0.95
#         )

#         generated_story = story_output[0]['generated_text']
        
#     except Exception as e:
#         sys.stderr.write(f"Error during story generation: {e}\n")
#         sys.exit(1)

#     # Save the generated story to a text file
#     output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'stories')
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     output_filename = f"story_{content_id}.txt"
#     output_path = os.path.join(output_dir, output_filename)

#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(generated_story)
        
#         # Print the relative path to Node.js
#         print(f"storage/stories/{output_filename}")
        
#     except Exception as e:
#         sys.stderr.write(f"Error saving story: {e}\n")
#         sys.exit(1)

# if __name__ == "__main__":
#     if len(sys.argv) > 2:
#         file_path_arg = sys.argv[1]
#         content_id_arg = sys.argv[2]
#         generate_story(file_path_arg, content_id_arg)
#     else:
#         sys.stderr.write("Usage: python story_gen.py <file_path> <content_id>\n")
#         sys.exit(1)