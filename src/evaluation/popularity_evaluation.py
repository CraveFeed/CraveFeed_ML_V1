import pandas as pd
import numpy as np

def load_processed_data(file_path: str) -> pd.DataFrame:
    """
    Loads the processed dataset from a CSV file.

    Args:
        file_path (str): Path to the processed data file.

    Returns:
        pd.DataFrame: Processed dataset.
    """
    return pd.read_csv(file_path)

def evaluate_model(data: pd.DataFrame, k_values=[5, 10, 20]):
    """
    Evaluates the popularity-based recommendation model.

    Args:
        data (pd.DataFrame): Processed dataset containing posts and their scores.
        k_values (list): List of K values to evaluate precision and recall.

    Returns:
        dict: Evaluation metrics (Precision@K, Recall@K, Coverage).
    """
    # Sort posts by final_score in descending order
    sorted_data = data.sort_values(by="final_score", ascending=False)

    # Extract the ground truth (true popular posts)
    true_positive_posts = sorted_data[data["engagement_score"] > data["engagement_score"].median()]["postId"].tolist()

    # Initialize metrics
    metrics = {"precision": {}, "recall": {}, "coverage": None}

    # Calculate Precision@K and Recall@K for each K
    for k in k_values:
        top_k_posts = sorted_data.head(k)["postId"].tolist()
        
        # Relevant items in top-K
        relevant_items = [post for post in top_k_posts if post in true_positive_posts]
        
        precision_at_k = len(relevant_items) / k
        recall_at_k = len(relevant_items) / len(true_positive_posts)
        
        metrics["precision"][f"Precision@{k}"] = precision_at_k
        metrics["recall"][f"Recall@{k}"] = recall_at_k

    # Calculate Coverage
    recommended_posts = sorted_data["postId"].tolist()
    coverage = len(set(recommended_posts)) / len(data["postId"].unique())
    metrics["coverage"] = coverage

    return metrics

if __name__ == "__main__":
    # Path to the processed dataset
    PROCESSED_DATA_PATH = "./data/processed/processed_food_popularity_data.csv"

    try:
        # Load the processed data
        data = load_processed_data(PROCESSED_DATA_PATH)

        # Evaluate the model
        evaluation_metrics = evaluate_model(data)

        # Print the results
        print("Popularity-Based Model Evaluation Metrics:")
        for metric, values in evaluation_metrics.items():
            if isinstance(values, dict):  # For Precision and Recall
                for k, value in values.items():
                    print(f"{k}: {value:.4f}")
            else:  # For Coverage
                print(f"Coverage: {values:.4f}")

    except Exception as e:
        print(f"Error during model evaluation: {e}")
