import socket
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os

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

# Path to the raw CSV file
RAW_CSV_PATH = "./data/raw/food_popularity_data.csv"

@app.post("/add_post/")
async def add_post(post: Post):
    """
    Adds a new post to the raw CSV file.
    """
    try:
        # Use model_dump() instead of dict()
        post_data = post.model_dump()

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

        return {"message": "Post added successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add post: {e}")

def find_free_port(start_port=8000):
    """
    Finds an available port starting from the specified port.
    """
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:  # Port is free
                return port
            port += 1

if __name__ == "__main__":
    import uvicorn

    # Find an available port starting from 8000
    port = find_free_port(8000)
    print(f"Starting the API on port {port}")

    # Run the FastAPI app on the chosen port
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)
