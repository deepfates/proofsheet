from typing import Dict, Any
from fastcore.parallel import threaded

# Define parameter lists
integer_params = [
    "num_inference_steps",
    "seed",
    "output_quality"  # Corrected typo
]

float_params = [
    "guidance_scale",
    "prompt_strength",
]

valid_params = integer_params + float_params

# Helper function to calculate parameter ranges
def calculate_range(start: float, end: float, size: int, param_name: str):
    step = (end - start) / (size - 1) if size > 1 else 0
    values = [start + i * step for i in range(size)]

    # Validation specific to parameters
    if param_name in integer_params:
        values = [max(int(round(value)), 1) for value in values]
    elif param_name in float_params:
        # Add any parameter-specific validations here if needed
        pass

    return values

# Validate user-provided parameters
def validate_params(params: Dict[str, Any]):
    for key, value in params.items():
        if key not in valid_params:
            raise ValueError(f"Invalid parameter: {key}")

        # Additional checks for parameter ranges
        if key in integer_params:
            int_value = int(round(float(value)))
            if int_value < 1:
                raise ValueError(f"{key} must be greater than or equal to 1.")
        elif key in float_params:
            float_value = float(value)
            if key == 'guidance_scale' and not (0 <= float_value <= 20):
                raise ValueError(f"{key} must be between 1 and 20.")
            # Add more checks as needed

# Correct parameter types based on definitions
def correct_param_types(params: Dict[str, Any]) -> Dict[str, Any]:
    corrected_params = {}
    for key, value in params.items():
        try:
            if key in integer_params:
                corrected_params[key] = int(round(float(value)))
            elif key in float_params:
                corrected_params[key] = float(value)
            else:
                corrected_params[key] = str(value)
        except ValueError as e:
            print(f"Error converting parameter '{key}' with value '{value}': {e}")
            raise
    return corrected_params
