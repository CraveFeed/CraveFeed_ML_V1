from fastapi import FastAPI, HTTPException
from src.models.popularity_model import load_processed_data, recommend_posts
import os

# Initialize FastAPI app
app = FastAPI()

# Path to the processed dataset
PROCESSED_DATA_PATH = "./data/processed/processed_food_popularity_data.csv"

@app.get("/explore")
def get_recommendations():
    """
    Endpoint to get recommended post IDs based on popularity.

    Returns:
        dict: A JSON object containing the recommended post IDs in order of recommendation strength.
    """
    try:
        # Load the processed dataset
        if not os.path.exists(PROCESSED_DATA_PATH):
            raise FileNotFoundError(f"Processed data not found at {PROCESSED_DATA_PATH}")

        data = load_processed_data(PROCESSED_DATA_PATH)

        # Generate recommendations
        recommended_post_ids = recommend_posts(data)

        # Return as JSON
        return {"recommended_post_ids": recommended_post_ids}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while generating recommendations")

