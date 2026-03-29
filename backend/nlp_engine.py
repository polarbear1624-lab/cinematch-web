import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Locate the dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/master_global_movies.csv")

class NLPEngine:
    def __init__(self):
        self.df = None
        self.embeddings = None
        self.cosine_sim = None 
        
        # This downloads a tiny, lightning-fast Deep Learning model into your project!
        self.model = SentenceTransformer('all-mpnet-base-v2') 
        self.is_ready = False

    def train_model(self):
        print("🎭 Waking up the NLP Soul... (This might take 1-2 minutes to read 5000 plots!)")
        try:
            self.df = pd.read_csv(DATA_PATH)
            self.df['overview'] = self.df['overview'].fillna('')

            # --- SAFETY NET 1: FIXING THE YEAR COLUMN ---
            # If your CSV uses 'release_date', this automatically creates a 'year' column.
            if 'year' not in self.df.columns and 'release_date' in self.df.columns:
                self.df['year'] = pd.to_datetime(self.df['release_date'], errors='coerce').dt.year
            
            # Ensures the year column is pure math numbers, turning blanks into NaNs
            if 'year' in self.df.columns:
                self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')

            # --- THE DEEP LEARNING MAGIC ---
            self.embeddings = self.model.encode(self.df['overview'].tolist(), show_progress_bar=True)
            
            # --- THE MATH ---
            # Calculate how similar the 384-number arrays are to each other
            print("📐 Calculating Deep Learning similarity...")
            self.cosine_sim = cosine_similarity(self.embeddings)

            self.is_ready = True
            print("✅ NLP Soul has deeply understood all movies!")
            
        except Exception as e:
            print(f"❌ Error training NLP model: {e}")

    def get_recommendations(self, movie_title, target_genre="All Genres", target_year="Any Time", top_n=5):
        if not self.is_ready:
            return []

        exact_match = self.df[self.df['original_title'].str.lower() == movie_title.lower()]
        if exact_match.empty:
            return []

        idx = exact_match.index[0]
        
        # 1. Get ALL similarity scores and sort them
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # 2. Grab the indices of ALL movies (except the first one, which is the movie itself)
        all_indices = [i[0] for i in sim_scores[1:]]
        
        # 3. Create a dataframe of ALL matches in order of similarity
        similar_movies = self.df.iloc[all_indices].copy()

        # --- THE FILTERING LOGIC ---
        
        # 4. Filter the ENTIRE list by Genre
        if target_genre and target_genre != "All Genres":
            similar_movies = similar_movies[similar_movies['genres'].str.contains(target_genre, case=False, na=False)]
            
        # 5. Filter the ENTIRE list by Year (With Safety Net 2)
        if target_year and target_year != "Any Time":
            try:
                start_year = int(target_year[:4]) 
                end_year = start_year + 9
                similar_movies = similar_movies[(similar_movies['year'] >= start_year) & (similar_movies['year'] <= end_year)]
            except ValueError:
                # If the React app sends something weird, skip the filter instead of crashing the server
                pass

        # 6. NOW return the top N from whatever survived the filters!
        recommendations = similar_movies['original_title'].head(top_n).tolist()
        
        return recommendations
        
# Create an instance so the API can use it
nlp_recommender = NLPEngine()