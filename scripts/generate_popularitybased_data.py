import os
import pandas as pd
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mimesis import Generic
import subprocess
import json
import logging

# Load environment variables
load_dotenv(dotenv_path="../.env")  # Adjust this path if needed

# Function to generate text using Ollama Llama2
def generate_text_ollama(prompt):
    """
    Generate text using the locally installed Ollama Llama 2 model.

    Args:
        prompt (str): The input prompt for text generation.

    Returns:
        str: The generated text response.
    """
    try:
        # Command to run the Ollama model
        result = subprocess.run(
            ["ollama", "generate", "--model", "llama2", "--json"],
            input=json.dumps({"prompt": prompt}),
            text=True,
            capture_output=True
        )
        # Parse the response
        output = json.loads(result.stdout)
        return output.get("response", "Default Description").strip()
    except Exception as e:
        logging.error(f"Error generating text with Ollama: {e}")
        return "Default Description"

def generate_batch_descriptions_ollama(titles):
    """
    Generate descriptions for a list of food titles using Ollama Llama 2.

    Args:
        titles (list): A list of food titles.

    Returns:
        list: A list of generated descriptions.
    """
    descriptions = []
    for title in titles:
        prompt = f"Write a short, engaging description for the food-related post titled: {title}."
        description = generate_text_ollama(prompt)
        descriptions.append(description)
    return descriptions

def generate_food_data(num_posts=100):
    """
    Generates a synthetic dataset for food-related social media posts.
    
    Args:
        num_posts (int): Number of posts to generate.

    Returns:
        pd.DataFrame: A DataFrame containing synthetic data.
    """
    # Initialize Generic for generating data
    generic = Generic()

    # Generate post IDs
    post_ids = [f"P{str(i).zfill(5)}" for i in range(1, num_posts + 1)]
    
    # Generate titles related to food
    titles = [generic.food.dish() for _ in range(num_posts)]
    
    # Generate descriptions in batches using Ollama Llama 2
    descriptions = generate_batch_descriptions_ollama(titles)
    
    # Check lengths of all lists before creating DataFrame
    print(f"Post IDs Length: {len(post_ids)}")
    print(f"Titles Length: {len(titles)}")
    print(f"Descriptions Length: {len(descriptions)}")
    
    # Ensure all lists are of equal length before proceeding
    if len(post_ids) != num_posts or len(titles) != num_posts or len(descriptions) != num_posts:
        raise ValueError("One or more lists have mismatched lengths.")

    # Generate metrics
    impressions = [random.randint(100, 10000) for _ in range(num_posts)]
    likes = [random.randint(0, max(10, impressions[i] // 10)) for i in range(num_posts)]
    comments = [random.randint(0, max(5, likes[i] // 5)) for i in range(num_posts)]
    
    # Generate timestamps
    start_date = datetime(2024, 1, 1)
    timestamps = [start_date + timedelta(days=random.randint(0, 365)) for _ in range(num_posts)]
    
    # Generate business post flags
    business_flag = [random.choice([True, False]) for _ in range(num_posts)]

    # Construct the DataFrame
    data = {
        "postId": post_ids,
        "title": titles,
        "description": descriptions,
        "impressions": impressions,
        "likesCount": likes,
        "commentsCount": comments,
        "createdAt": timestamps,
        "isBusinessPost": business_flag,
    }

    return pd.DataFrame(data)

# Generate dataset
num_posts = 200

try:
    food_data = generate_food_data(num_posts=num_posts)

    # Save to CSV
    output_path = "./data/food_popularity_data.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    food_data.to_csv(output_path, index=False)

    print(f"Dataset with {num_posts} food-related posts saved at {output_path}")

except Exception as e:
    logging.error(f"Error generating food data: {e}")
