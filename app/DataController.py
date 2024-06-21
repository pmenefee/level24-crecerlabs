from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cosine
import Settings

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["speaker_recognition"]
collection = db["embeddings"]                       # The records are only pulled once, when the script is loaded.
in_memory_collection = list(collection.find())      # build an in memory list of records.

# Function to store embedding in MongoDB
def store_embedding(embedding, speaker_id):
    # Add to database
    collection.insert_one({
        "speaker_id": speaker_id,
        "embedding": embedding.tolist()
    })
    # Add to in-memory list
    in_memory_collection.append({
        "speaker_id": speaker_id,
        "embedding": embedding.tolist()
    })

# Function to compare new embedding with stored embeddings
def compare_with_stored_embeddings(new_embedding):  # Adjusted threshold
    for record in in_memory_collection:
        stored_embedding = np.array(record["embedding"])
        similarity = 1 - cosine(new_embedding, stored_embedding)

        print(f"Similarity with {record['speaker_id']}: {similarity}")  # Debugging print

        # Compare the cosine similarity with the hardcoded threshold.
        if similarity > Settings.similarity_threshold:
            return record['speaker_id']
    return None