import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

# 1. Locate the dataset (Look one folder up, inside the 'data' folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "../data/tmdb_5000_movies.csv")

class MovieRecommender:
    def __init__(self):
        self.df = None
        self.similarity_matrix = None
        self.is_ready = False

    def train_model(self):
        print("🧠 Waking up the ML Engine... Reading 5000 movies...")
        try:
            # Load the CSV into a Pandas DataFrame
            self.df = pd.read_csv(DATA_PATH)

            # Clean the data: If a movie has no plot summary, replace it with an empty string
            self.df['overview'] = self.df['overview'].fillna('')

            # --- THE MAGIC HAPPENS HERE ---
            
            # 1. TF-IDF Vectorizer: This converts English words into numbers. 
            # It gives more weight to unique words (like "dream", "heist") and ignores 
            # common words (like "the", "and", "is" -> 'stop_words').
            tfidf = TfidfVectorizer(stop_words='english')
            
            # 2. Create the Matrix: Every movie's plot becomes a mathematical array (vector).
            tfidf_matrix = tfidf.fit_transform(self.df['overview'])

            # 3. Calculate Cosine Similarity: This compares every movie's vector against 
            # every other movie's vector to see how close their angles are.
            self.similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

            self.is_ready = True
            print("✅ ML Engine is fully trained and ready!")
            
        except Exception as e:
            print(f"❌ Error training model: {e}. Did you put the CSV in the right place?")

    def get_recommendations(self, movie_title, top_n=5):
        if not self.is_ready:
            return ["Error: The brain is still booting up!"]

        try:
            # Find the exact row number (index) of the movie the user searched for
            # We use .lower() to make the search case-insensitive
            idx = self.df[self.df['original_title'].str.lower() == movie_title.lower()].index[0]
        except IndexError:
            return [f"Sorry, '{movie_title}' is not in our 5000-movie database."]

        # Get the similarity scores for this specific movie against all other 4999 movies
        sim_scores = list(enumerate(self.similarity_matrix[idx]))

        # Sort the movies based on their similarity score (Highest to lowest)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the IDs of the top 5 most similar movies 
        # (We skip the 1st one because it will be the exact movie the user searched for!)
        top_movies_indices = [i[0] for i in sim_scores[1:top_n+1]]

        # Return the actual titles of those top movies
        recommendations = self.df.iloc[top_movies_indices]['original_title'].tolist()
        return recommendations

# Create an instance of the brain so our API can use it
recommender = MovieRecommender()