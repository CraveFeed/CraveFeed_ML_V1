import pandas as pd
from math import radians, sin, cos, sqrt, atan2

def load_processed_data(file_path):
    """
    Loads the processed dataset.

    Args:
        file_path (str): Path to the processed dataset CSV.

    Returns:
        pd.DataFrame: Processed dataset as a DataFrame.
    """
    return pd.read_csv(file_path)

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface using the Haversine formula.

    Args:
        lat1, lon1: Latitude and longitude of the first point in degrees.
        lat2, lon2: Latitude and longitude of the second point in degrees.

    Returns:
        float: Distance in kilometers between the two points.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    radius_earth_km = 6371  # Earth's radius in kilometers
    return radius_earth_km * c

def update_final_score_with_distance(data, user_lat, user_lon, distance_weight=0.2):
    """
    Updates the final score by incorporating the distance from the user.

    Args:
        data (pd.DataFrame): Processed dataset.
        user_lat (float): Latitude of the user.
        user_lon (float): Longitude of the user.
        distance_weight (float): Weight for the distance factor in the final score.

    Returns:
        pd.DataFrame: Data with updated final scores.
    """
    # Calculate distance from the user for each post
    data["distance_from_user"] = data.apply(
        lambda row: haversine(user_lat, user_lon, row["latitude"], row["longitude"]), axis=1
    )
    
    # Normalize the distance to [0, 1] range
    data["distance_norm"] = 1 - (data["distance_from_user"] / data["distance_from_user"].max())

    # Update the final score by incorporating distance
    data["final_score"] = (
        (1 - distance_weight) * data["final_score"] + distance_weight * data["distance_norm"]
    )

    return data

def recommend_posts(data):
    """
    Generates a recommendation list of post IDs based on their updated final scores.

    Args:
        data (pd.DataFrame): Processed dataset.

    Returns:
        list: List of post IDs sorted by recommendation strength.
    """
    # Ensure the DataFrame is sorted by final_score in descending order
    data = data.sort_values(by="final_score", ascending=False)

    # Return only the post IDs in sorted order
    return data["postId"].tolist()

if __name__ == "__main__":
    # Path to the processed dataset
    processed_data_path = "./data/processed/processed_food_popularity_data.csv"

    # Load the processed data
    try:
        processed_data = load_processed_data(processed_data_path)
    except FileNotFoundError:
        print(f"Error: Processed data file not found at {processed_data_path}")
        exit(1)

    # User's latitude and longitude (example inputs)
    user_latitude = 37.7749  # Replace with the actual latitude
    user_longitude = -122.4194  # Replace with the actual longitude

    # Update the final scores with distance
    processed_data = update_final_score_with_distance(
        processed_data, user_latitude, user_longitude
    )

    # Generate recommendations
    recommended_post_ids = recommend_posts(processed_data)

    # Output the recommended post IDs
    print("Recommended Post IDs (in order of recommendation strength):")
    print(recommended_post_ids)
