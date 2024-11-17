from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path

# Initialize FastAPI app
app = FastAPI()

# Pydantic model to validate input data (latitude and longitude)
class LocationRequest(BaseModel):
    latitude: float
    longitude: float

def resolve_path(relative_path):
    """Resolve a relative path to an absolute path."""
    return os.path.abspath(relative_path)

# Path to the processed dataset and popularity-based script
PROCESSED_DATA_PATH = "./data/processed/processed_food_popularity_data.csv"
POPULARITY_BASED_SCRIPT_PATH = "./src/data_processing/popularity_based.py"

# Path to the virtual environment's Python executable
VENV_PYTHON_PATH = "venv\\Scripts\\python.exe"

VENV_PYTHON_PATH = resolve_path(VENV_PYTHON_PATH)

@app.post("/explore")
async def get_recommendations(location: LocationRequest):
    """
    Endpoint to get recommended post IDs based on popularity and distance from the user.

    Args:
        location (LocationRequest): Latitude and longitude of the user.

    Returns:
        dict: A JSON object containing the recommended post IDs in order of recommendation strength.
    """
    try:
        # Check if processed data file exists
        if not os.path.exists(PROCESSED_DATA_PATH):
            raise FileNotFoundError(f"Processed data not found at {PROCESSED_DATA_PATH}")
        
        # Construct the command to run the script using the virtual environment's Python
        command = [
            VENV_PYTHON_PATH, 
            POPULARITY_BASED_SCRIPT_PATH,
            str(location.latitude),  # Use latitude
            str(location.longitude)   # Use longitude
        ]
        
        # Run the script
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Error running script: {result.stderr}")
        
        # The output of the script is expected to be a list of recommended post IDs
        recommended_post_ids = result.stdout.strip().split("\n")
        
        # Return the recommended post IDs
        return {"recommended_post_ids": recommended_post_ids}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
