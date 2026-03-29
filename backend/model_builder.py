import pandas as pd
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/master_global_movies.csv")
MODEL_DIR = os.path.join(BASE_DIR, "../models") # Let's make a folder for our saved models

def build_model():
    print("🧠 Starting NLP Model Builder...")

    # 1. Load the clean data
    print("📥 Loading master dataset...")
    df = pd.read_csv(DATA_PATH)
    
    # Just in case some missing values sneaked in, replace them with empty strings
    df['overview'] = df['overview'].fillna('')

    # 2. Vectorization (Turning words into numbers)
    print("🔢 Converting plot summaries into mathematical vectors (TF-IDF)...")
    # TfidfVectorizer removes standard English "stop words" (like 'the', 'is', 'in') 
    # and counts how important each word is to a specific movie.
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['overview'])

    # 3. Calculate Similarity
    print("📐 Calculating Cosine Similarity between all movies...")
    # This creates a massive grid comparing every movie to every other movie
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # 4. Save the logic for the backend API
    print("💾 Saving the similarity matrix and movie list...")
    
    # Create a models directory if it doesn't exist
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    # We use 'pickle' to save Python objects exactly as they are in memory
    with open(os.path.join(MODEL_DIR, 'movies_list.pkl'), 'wb') as f:
        pickle.dump(df.to_dict(), f)
        
    with open(os.path.join(MODEL_DIR, 'similarity_matrix.pkl'), 'wb') as f:
        pickle.dump(cosine_sim, f)

    print("✅ Model built and saved successfully! You are ready to make recommendations.")

if __name__ == "__main__":
    build_model()