import pandas as pd
import os
import warnings

# Ignore pandas warnings for cleaner terminal output
warnings.filterwarnings('ignore')

# Locate our two datasets
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RATINGS_PATH = os.path.join(BASE_DIR, "../data/ratings.csv")
MOVIES_PATH = os.path.join(BASE_DIR, "../data/movies.csv")

class CollaborativeRecommender:
    def __init__(self):
        self.user_movie_matrix = None
        self.ratings_df = None
        self.movies_df = None
        self.is_ready = False

    def train_model(self):
        print("👥 Waking up the Hive Mind... Analyzing user behavior...")
        try:
            # 1. Load the data
            ratings = pd.read_csv(RATINGS_PATH)
            movies = pd.read_csv(MOVIES_PATH)

            # 2. Merge them so we have Titles instead of just ID numbers
            df = pd.merge(ratings, movies, on='movieId')

            # 3. Build the Taste Matrix! 
            # Rows = Users, Columns = Movie Titles, Values = Ratings (0.5 to 5.0)
            self.user_movie_matrix = df.pivot_table(index='userId', columns='title', values='rating')

            # 4. Count the ratings
            # We need to know HOW MANY people rated a movie. If only 1 person watched 
            # a weird movie and gave it 5 stars, we don't want it ruining our math.
            ratings_count = pd.DataFrame(df.groupby('title')['rating'].mean())
            ratings_count['num_ratings'] = df.groupby('title')['rating'].count()
            self.ratings_df = ratings_count
            self.movies_df = movies.set_index('title')

            self.is_ready = True
            print("✅ Hive Mind is fully synchronized!")
            
        except Exception as e:
            print(f"❌ Error training collaborative model: {e}")

    def get_recommendations(self, movie_title, target_genre="All Genres", target_decade="Any Time", min_ratings=50, top_n=5):
        if not self.is_ready:
            return ["Error: The Hive Mind is still booting up!"]

        # --- THE FIX: SMART SEARCH ---
        # Look through all columns and find one that contains the typed text (ignoring capitals)
        matching_movies = [col for col in self.user_movie_matrix.columns if movie_title.lower() in str(col).lower()]
        
        if not matching_movies:
            # Return an empty list instead of a fake movie title
            return [] 
            
        # Take the very first match it finds (e.g., "superman" -> "Superman (1978)")
        exact_title = matching_movies[0]
        
        # Now use that exact title to do the math
        movie_user_ratings = self.user_movie_matrix[exact_title]

        # --- THE MAGIC MATH ---
        similar_to_movie = self.user_movie_matrix.corrwith(movie_user_ratings)
        corr_movie = pd.DataFrame(similar_to_movie, columns=['Correlation'])
        corr_movie.dropna(inplace=True)
        corr_movie = corr_movie.join(self.ratings_df['num_ratings'])
        recommended = corr_movie[corr_movie['num_ratings'] > min_ratings].sort_values('Correlation', ascending=False)

        top_titles = []
        for title in recommended.index:
            if title == exact_title:
                continue
                
            row = self.movies_df.loc[title] if title in self.movies_df.index else None
            if row is not None:
                # Handle possible duplicated titles
                if isinstance(row, pd.DataFrame):
                    row = row.iloc[0]
                    
                # 1. Apply Genre Filter
                if target_genre != "All Genres":
                    if pd.isna(row.get('genres')) or target_genre.lower() not in str(row['genres']).lower():
                        continue
                        
                # 2. Apply Decade Filter
                if target_decade != "Any Time":
                    start_year = int(target_decade[:4])
                    end_year = start_year + 9
                    try:
                        year = int(str(title)[-5:-1])
                        if year < start_year or year > end_year:
                            continue
                    except:
                        continue
                        
            top_titles.append(title)
            if len(top_titles) >= top_n:
                break

        return top_titles

# Create an instance so the API can use it
collab_recommender = CollaborativeRecommender()