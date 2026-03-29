import pandas as pd
import pickle
import os

# 1. Set up the paths to our saved brain
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../models")

print("⏳ Waking up the recommendation engine...")

# 2. Load the saved "LITE" files into memory
with open(os.path.join(MODEL_DIR, 'movies_list_lite.pkl'), 'rb') as f:
    movies_dict = pickle.load(f)
    movies_df = pd.DataFrame(movies_dict)

with open(os.path.join(MODEL_DIR, 'similarity_matrix_lite.pkl'), 'rb') as f:
    cosine_sim = pickle.load(f)

print("✅ Engine ready!")