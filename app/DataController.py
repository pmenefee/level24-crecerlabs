from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cosine
import Settings

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["speaker_recognition"]
collection = db["embeddings"]

# Function to store embedding in MongoDB
def store_embedding(embedding, speaker_id):
    collection.insert_one({
        "speaker_id": speaker_id,
        "embedding": embedding.tolist()
    })

# Function to compare new embedding with stored embeddings
def compare_with_stored_embeddings(new_embedding):  # Adjusted threshold
    for record in collection.find():
        stored_embedding = np.array(record["embedding"])
        similarity = 1 - cosine(new_embedding, stored_embedding)

        print(f"Similarity with {record['speaker_id']}: {similarity}")  # Debugging print

        # Compare the cosine similarity with the hardcoded threshold.
        if similarity > Settings.similarity_threshold:
            return record['speaker_id']
    return None