# ml_scripts/prompt_assistant.py
import sys
import json
import requests
import os

# --- Configuration ---
# Ensure this URL is correct for the default Ollama API endpoint
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL_NAME = "llama3" 

def generate_enhanced_prompt(user_prompt, system_instruction):
    """
    Sends the user's prompt and system instruction to the local Ollama LLM 
    to generate a detailed, enhanced prompt for image generation.
    """
    
    # Check server reachability (Optional but good practice)
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5) 
    except requests.exceptions.RequestException:
        sys.stderr.write("ERROR: Ollama server is not running or unreachable at http://localhost:11434.\n")
        return None

    # Construct the payload for Ollama
    # Ollama's /api/generate endpoint requires the prompt structure
    payload = {
        "model": OLLAMA_MODEL_NAME, 
        
        # Structure the prompt clearly using the system instruction and user input.
        # This acts as the conversational context.
        "prompt": f"System Instruction: {system_instruction}\n\nUser Input: {user_prompt}\n\nEnhanced Prompt:", 
        
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 2048,
            # Use a clear stop token to get only the output text
            "stop": ["User Input:", "System Instruction:", "\n\n", "Enhanced Prompt:"], 
        }
    }

    try:
        # Make the synchronous POST request
        response = requests.post(
            OLLAMA_API_URL, 
            json=payload, 
            timeout=120
        )
        
        # Raise an HTTPError if the status code is 4xx or 5xx (e.g., if model is missing)
        response.raise_for_status() 

        data = response.json()
        
        # The enhanced prompt is in the 'response' key
        enhanced_prompt = data.get("response", "").strip()
        
        # Final cleanup to remove any leading instruction text the LLM might have missed
        if enhanced_prompt.lower().startswith("enhanced prompt:"):
            enhanced_prompt = enhanced_prompt.split(':', 1)[-1].strip()
            
        return enhanced_prompt

    except requests.exceptions.HTTPError as err:
        sys.stderr.write(f"ERROR: HTTP Error connecting to Ollama (Code {response.status_code}). Check if '{OLLAMA_MODEL_NAME}' is pulled.\nDetail: {err}\n")
        return None
    except requests.exceptions.ConnectionError:
        sys.stderr.write("ERROR: Could not connect to Ollama. Ensure the service is running.\n")
        return None
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred: {e}\n")
        return None


if __name__ == "__main__":
    # Node.js passes arguments: [script_path, user_prompt, system_instruction]
    # We expect arguments 1 and 2 (indices 1 and 2 in sys.argv)
    if len(sys.argv) >= 3:
        user_prompt_arg = sys.argv[1]
        system_instruction_arg = sys.argv[2]
        
        enhanced_prompt = generate_enhanced_prompt(user_prompt_arg, system_instruction_arg)

        if enhanced_prompt:
            # CRITICAL: Print ONLY the final enhanced string to stdout for Node.js
            print(enhanced_prompt)
            sys.exit(0)
        else:
            sys.stderr.write("Failed to generate a clean enhanced prompt.\n")
            sys.exit(1)
            
    else:
        sys.stderr.write("Usage: python prompt_assistant.py <user_prompt> <system_instruction>\n")
        sys.exit(1)
        