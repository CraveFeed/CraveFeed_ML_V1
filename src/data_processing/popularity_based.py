import pandas as pd
import numpy as np
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import sys

# Load raw data from CSV
source_path = "./data/raw/food_popularity_data.csv"
data = pd.read_csv(source_path)

# Ensure createdAt is a datetime object and normalize to a consistent format
data["createdAt"] = pd.to_datetime(data["createdAt"], format="%Y-%m-%dT%H:%M:%S", errors='coerce').fillna(
    pd.to_datetime(data["createdAt"], format="%Y-%m-%d", errors='coerce')
)

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

# Final Score Calculation (without distance adjustment)
w1, w2, w3 = 0.6, 0.3, 0.1  # Weights for engagement, recency, and business post weight
data["final_score"] = (
    w1 * data["engagement_score"] + w2 * data["recency_score"] + w3 * data["business_post_weight"]
)

# ----------- New Distance Logic -----------

# Function to calculate Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius_earth_km = 6371  # Radius of Earth in km
    return radius_earth_km * c

# Function to update final score with distance-based weighting
def update_final_score_with_distance(data, user_lat, user_lon, distance_weight=0.2):
    # Calculate distance from user for each post
    data["distance_from_user"] = data.apply(
        lambda row: haversine(user_lat, user_lon, row["latitude"], row["longitude"]), axis=1
    )
    
    # Normalize the distance to [0, 1] range
    data["distance_norm"] = 1 - (data["distance_from_user"] / data["distance_from_user"].max())

    # Update the final score by incorporating the distance
    data["final_score"] = (
        (1 - distance_weight) * data["final_score"] + distance_weight * data["distance_norm"]
    )

    return data

# ----------- End Distance Logic -----------

# Check if latitude and longitude are passed as arguments
if len(sys.argv) > 2:
    user_lat = float(sys.argv[1])
    user_lon = float(sys.argv[2])
    
    # Update final score with distance information
    data = update_final_score_with_distance(data, user_lat, user_lon)

# Sort Data by Final Score
data = data.sort_values(by="final_score", ascending=False)

# Save Processed Data
output_path = "./data/processed/processed_food_popularity_data.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)

# print(f"Processed data saved at {output_path}")

# # Display Processed Data
# print(data.head())

# Get only the unique postId column from the sorted data
recommended_post_ids = data["postId"].drop_duplicates().tolist()  # Updated here

# Print the unique postId values as a newline-separated list
for post_id in recommended_post_ids:  # Updated here
    print(post_id)
