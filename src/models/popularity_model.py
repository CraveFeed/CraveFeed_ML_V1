import pandas as pd

def load_processed_data(file_path):
    """
    Loads the processed dataset.

    Args:
        file_path (str): Path to the processed dataset CSV.

    Returns:
        pd.DataFrame: Processed dataset as a DataFrame.
    """
    return pd.read_csv(file_path)

def recommend_posts(data):
    """
    Generates a recommendation list of post IDs based on their final scores.

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

    # Generate recommendations
    recommended_post_ids = recommend_posts(processed_data)

    # Output the recommended post IDs
    print("Recommended Post IDs (in order of recommendation strength):")
    print(recommended_post_ids)
