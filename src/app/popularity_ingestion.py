import socket
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import subprocess

app = FastAPI()

# Define the model for incoming post data
class Post(BaseModel):
    postId: str
    title: str
    impressions: int
    likesCount: int
    commentsCount: int
    createdAt: str
    isBusinessPost: bool
    latitude: float
    longitude: float

# Paths
RAW_CSV_PATH = "./data/raw/food_popularity_data.csv"
PROCESSED_SCRIPT_PATH = "./src/data_processing/popularity_based.py"

# Path to the virtual environment's Python executable
VENV_PYTHON_PATH = "venv\\Scripts\\python.exe"

def resolve_path(relative_path):
    """Resolve a relative path to an absolute path."""
    return os.path.abspath(relative_path)

VENV_PYTHON_PATH = resolve_path(VENV_PYTHON_PATH)

@app.post("/add_post/")
async def add_post(post: Post):
    """
    Adds a new post to the raw CSV file and runs the popularity-based processing script.
    """
    try:
        # Step 1: Add post data to the raw CSV
        post_data = post.model_dump()

        # Normalize createdAt to ensure consistency
        post_data["createdAt"] = pd.to_datetime(post_data["createdAt"]).strftime("%Y-%m-%dT%H:%M:%S")

        # Check if raw CSV exists; create it if not
        if not os.path.exists(RAW_CSV_PATH):
            pd.DataFrame(columns=post_data.keys()).to_csv(RAW_CSV_PATH, index=False)

        # Load existing data
        raw_data = pd.read_csv(RAW_CSV_PATH)

        # Convert the incoming data to a DataFrame
        new_post_df = pd.DataFrame([post_data])

        # Append and save
        raw_data = pd.concat([raw_data, new_post_df], ignore_index=True)
        raw_data.to_csv(RAW_CSV_PATH, index=False)

        # Step 2: Run the popularity-based script (processing only, no recommendations returned)
        command = [
            "python",
            PROCESSED_SCRIPT_PATH,
            str(post.latitude),
            str(post.longitude),
        ]

        # Execute the script
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error running script: {result.stderr}")

        return {"message": "Post added and processed successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add post: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

