# Use the official Python image from the Docker Hub
FROM python:3.10.0

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the ports for both APIs
EXPOSE 8000 8001

# Command to run both API endpoints
CMD ["sh", "-c", "uvicorn src.app.popularity_ingestion:app --reload --port 8000 & uvicorn src.app.explore:app --reload --port 8001"]