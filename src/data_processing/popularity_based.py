import pandas as pd
import numpy as np
import os
from datetime import datetime

# Load raw data from CSV
source_path = "./data/raw/food_popularity_data.csv"
data = pd.read_csv(source_path)

# Ensure createdAt is a datetime object
data["createdAt"] = pd.to_datetime(data["createdAt"])

# Get current date
current_date = datetime.now()

# Normalize Numerical Features
def normalize(column):
    return (column - column.min()) / (column.max() - column.min()) if column.max() != column.min() else column

data["likes_norm"] = normalize(data["likesCount"])
data["comments_norm"] = normalize(data["commentsCount"])
data["impressions_norm"] = normalize(data["impressions"])

# Calculate Engagement Score
alpha, beta, gamma = 0.5, 0.3, 0.2  # Weights for likes, comments, and impressions
data["engagement_score"] = (
    alpha * data["likes_norm"] + beta * data["comments_norm"] + gamma * data["impressions_norm"]
)

# Calculate Recency Score
lambda_decay = 0.1  # Decay factor for recency
data["days_since_posted"] = (current_date - data["createdAt"]).dt.days
data["recency_score"] = np.exp(-lambda_decay * data["days_since_posted"])

# Add Business Post Weight
business_weight = 1.5  # Weight for business posts
data["business_post_weight"] = data["isBusinessPost"].astype(int) * business_weight

# Final Score Calculation
w1, w2, w3 = 0.6, 0.3, 0.1  # Weights for engagement, recency, and business post weight
data["final_score"] = (
    w1 * data["engagement_score"] + w2 * data["recency_score"] + w3 * data["business_post_weight"]
)

# Sort Data by Final Score
data = data.sort_values(by="final_score", ascending=False)

# Save Processed Data
output_path = "./data/processed/processed_food_popularity_data.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)

print(f"Processed data saved at {output_path}")

# Display Processed Data
print(data.head())
