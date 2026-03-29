import pandas as pd
import os
import ast 

# 1. Set up the paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TMDB_MOVIES_PATH = os.path.join(BASE_DIR, "../data/tmdb_5000_movies.csv")
TMDB_CREDITS_PATH = os.path.join(BASE_DIR, "../data/tmdb_5000_credits.csv") # <-- NEW FILE NEEDED!
BOLLYWOOD_PATH = os.path.join(BASE_DIR, "../data/bollywood.csv") 
OUTPUT_PATH = os.path.join(BASE_DIR, "../data/master_global_movies.csv")

# --- HELPER FUNCTIONS FOR TMDB JSON ---
def convert_tmdb_genres(genre_string):
    try:
        genres = ast.literal_eval(genre_string)
        return ", ".join([g['name'] for g in genres])
    except: return "Unknown"

def get_director(crew_string):
    try:
        crew = ast.literal_eval(crew_string)
        for person in crew:
            if person['job'] == 'Director':
                return person['name']
        return "Unknown Director"
    except: return "Unknown Director"

def get_top_3_cast(cast_string):
    try:
        cast = ast.literal_eval(cast_string)
        names = [actor['name'] for actor in cast[:3]]
        return ", ".join(names)
    except: return "Unknown Cast"

def run_etl():
    print("🚀 Starting ETL Pipeline V3 (The Metadata Soup Edition!)...")

    # --- 1. TMDB CLEANING & MERGING ---
    print("📥 Extracting TMDB Movies and Credits...")
    tmdb_movies = pd.read_csv(TMDB_MOVIES_PATH)
    tmdb_credits = pd.read_csv(TMDB_CREDITS_PATH)
    
    # Merge them together based on the movie ID
    tmdb_df = tmdb_movies.merge(tmdb_credits, on='title')
    tmdb_df.columns = tmdb_df.columns.str.strip() 

    print("   -> Parsing TMDB Genres, Cast, and Directors...")
    tmdb_clean = pd.DataFrame()
    tmdb_clean['original_title'] = tmdb_df['title']
    tmdb_clean['overview'] = tmdb_df['overview']
    tmdb_clean['genres'] = tmdb_df['genres'].apply(convert_tmdb_genres)
    tmdb_clean['director'] = tmdb_df['crew'].apply(get_director)
    tmdb_clean['cast'] = tmdb_df['cast'].apply(get_top_3_cast)
    
    # Extract Year
    tmdb_clean['year'] = pd.to_datetime(tmdb_df['release_date'], errors='coerce').dt.year

    # --- 2. BOLLYWOOD CLEANING ---
    print("📥 Extracting Bollywood Data...")
    bolly_df = pd.read_csv(BOLLYWOOD_PATH)
    bolly_df.columns = bolly_df.columns.str.strip()
    
    bolly_clean = pd.DataFrame()
    bolly_clean['original_title'] = bolly_df['title']
    bolly_clean['overview'] = bolly_df['desc']
    bolly_clean['genres'] = bolly_df['genre']
    # Bollywood datasets usually have these columns. If yours are named differently, change them!
    bolly_clean['director'] = bolly_df.get('director', 'Unknown Director') 
    bolly_clean['cast'] = bolly_df.get('cast', 'Unknown Cast') 
    
    bolly_clean['year'] = bolly_df['year'].astype(str).str.extract(r'(\d{4})').astype(float)

    # --- 3. MERGE & CLEANUP ---
    print("🤝 Smashing global datasets together...")
    master_df = pd.concat([tmdb_clean, bolly_clean], ignore_index=True)
    master_df.dropna(subset=['overview'], inplace=True)
    master_df.drop_duplicates(subset=['original_title'], inplace=True)
    
    master_df['year'] = master_df['year'].fillna(0).astype(int)
    master_df['genres'] = master_df['genres'].fillna('Unknown')

    # --- 4. CREATE THE METADATA SOUP ---
    print("🍲 Cooking the Metadata Soup...")
    master_df['metadata_soup'] = (
        "Title: " + master_df['original_title'] + ". " +
        "Genres: " + master_df['genres'] + ". " +
        "Directed by: " + master_df['director'] + ". " +
        "Starring: " + master_df['cast'] + ". " +
        "Plot: " + master_df['overview']
    )

    # --- LOAD ---
    print("💾 Saving the ultimate Master Dataset...")
    master_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ ETL Complete! Brain expanded to {len(master_df)} movies.")

if __name__ == "__main__":
    run_etl()