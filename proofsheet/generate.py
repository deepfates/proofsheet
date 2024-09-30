import os
import requests
from typing import Dict, Any
from fastcore.parallel import threaded
import replicate
from db import initialize_database
from proofsheet.utils import calculate_range, validate_params, correct_param_types

# Initialize database within generate module
db = initialize_database()
proofs = db.t.proofs

# Replicate setup (for generating images)
replicate_api_token = os.environ.get('REPLICATE_API_TOKEN', '')
if not replicate_api_token:
    raise EnvironmentError("REPLICATE_API_TOKEN not set in environment variables.")

client = replicate.Client(api_token=replicate_api_token)  

@threaded
def generate_proof(proof: Dict[str, Any]):
    x_values = calculate_range(proof['x_range_start'], proof['x_range_end'], proof['grid_size'], proof['x_param'])
    y_values = calculate_range(proof['y_range_start'], proof['y_range_end'], proof['grid_size'], proof['y_param'])

    for i, x_value in enumerate(x_values):
        for j, y_value in enumerate(y_values):
            params = {
                proof['x_param']: x_value,
                proof['y_param']: y_value
            }
            validate_params(params)
            image_id = f"{i}_{j}"
            generate_and_save_proof_image(proof['prompt'], image_id, proof['folder'], params, proof['id'])

@threaded
def generate_and_save_proof_image(prompt: str, image_id: str, folder: str, params: Dict[str, Any], proof_id: str):
    corrected_params = correct_param_types(params)
    # print(f"Corrected params: {corrected_params}")
    # Set defaults and ensure parameters are valid
    defaults = {
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
        "prompt_strength": 0.8,
        "seed": 42
    }

    for key, value in defaults.items():
        corrected_params.setdefault(key, value)

    # Ensure num_inference_steps is at least 1
    if 'num_inference_steps' in corrected_params:
        if corrected_params['num_inference_steps'] < 1:
            corrected_params['num_inference_steps'] = 1

    # Prepare the model input including any default parameters
    model_input = {
        "prompt": prompt,
        **corrected_params
    }

    # Run the model and save the image
    try:
        # print(f"Generating image {image_id} with params: {model_input}")
        
        # Replace the mock with actual image generation logic
        response = client.run("black-forest-labs/flux-dev", input=model_input)
        # print(response)
        
        if len(response) > 0:
            image_url = response[0]
            image_path = os.path.join(folder, f"{image_id}.png")
            image_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(image_data)
            # print(f"Image {image_id} generated and saved at {image_path}.")
            
            # Verify that the file was actually created
            if os.path.exists(image_path):
                # print(f"Confirmed: Image file exists at {image_path}")
            else:
                # print(f"Error: Image file was not created at {image_path}")
        else:
            # print(f"Failed to download placeholder image for {image_id}. Status code: {response.status_code}")
    except replicate.exceptions.ReplicateError as e:
        # print(f"Error generating image {image_id}: {e}")
    except Exception as e:
        # print(f"Unexpected error generating image {image_id}: {e}")
