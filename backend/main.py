from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

# Import our active ML brains
from ml_engine import recommender
from collaborative_engine import collab_recommender 
# from nlp_engine import nlp_recommender # <-- DISABLED FOR RENDER FREE TIER

# 1. Create the cinephile.db file and the tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# --- THE NEW CORS FIX ---
# This tells the Python server: "It's okay to accept requests from our React Native app!"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd put your exact website URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Train ALL the ML models when the server starts
#recommender.train_model()
#collab_recommender.train_model() 
# nlp_recommender.train_model() # <-- DISABLED FOR RENDER FREE TIER

# 3. Helper function to open and close the database connection safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- PHASE 1: FOUNDATION (READ/WRITE) ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mechanical Cinephile API! 🎬 (Running in Lite Mode)"}

@app.post("/movies/")
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    new_movie = models.Movie(**movie.model_dump())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@app.get("/movies/")
def get_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).offset(skip).limit(limit).all()
    return movies

# --- PHASE 2: RULE-BASED RECOMMENDATIONS ---

@app.get("/recommendations/genre/")
def recommend_by_genre(genre: str, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).filter(models.Movie.genre.ilike(f"%{genre}%")).all()
    if not movies:
        return {"message": f"No movies found for the genre: {genre}. Time to add some!"}
    return movies

@app.get("/recommendations/director/")
def recommend_by_director(director: str, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).filter(models.Movie.director.ilike(f"%{director}%")).all()
    if not movies:
        return {"message": f"No movies found directed by: {director}."}
    return movies

# --- PHASE 3 & 4: INDIVIDUAL ML ENGINES ---

@app.get("/recommendations/ai/")
def recommend_with_ai(movie_title: str):
    suggestions = recommender.get_recommendations(movie_title=movie_title, top_n=5)
    return {
        "searched_movie": movie_title,
        "ai_recommendations": suggestions
    }

@app.get("/recommendations/collaborative/")
def recommend_with_collaborative(movie_title: str):
    suggestions = collab_recommender.get_recommendations(movie_title=movie_title, top_n=5)
    return {
        "searched_movie": movie_title,
        "hive_mind_recommendations": suggestions
    }

# ==========================================
# ⚠️ TEMPORARILY DISABLED FOR RENDER FREE TIER
# The following routes require heavy PyTorch/NLP libraries 
# that exceed the 512MB RAM limit.
# ==========================================

# @app.get("/recommendations/nlp/")
# def recommend_with_nlp(movie_title: str):
#     suggestions = nlp_recommender.get_recommendations(movie_title=movie_title, top_n=5)
#     return {
#         "searched_movie": movie_title,
#         "vibe_recommendations": suggestions
#     }

# @app.get("/browse/")
# def browse_movies(genre: str = "All Genres", decade: str = "Any Time", limit: int = 10):
#     df = nlp_recommender.df.copy()
#     if genre != "All Genres":
#         df = df[df['genres'].str.contains(genre, case=False, na=False)]
#     if decade != "Any Time":
#         start_year = int(decade[:4])
#         end_year = start_year + 9
#         df = df[(df['year'] >= start_year) & (df['year'] <= end_year)]
#     if df.empty:
#         return {"movies": []}
#     top_movies = df['original_title'].head(limit).tolist()
#     return {"movies": top_movies}

# @app.get("/recommendations/hybrid/")
# def recommend_hybrid(movie_title: str, genre: str = "All Genres", decade: str = "Any Time"):
#     hive_mind_titles = collab_recommender.get_recommendations(movie_title, top_n=10)
#     clean_title = movie_title.split(" (")[0]
#     if clean_title.endswith(", The"):
#         clean_title = "The " + clean_title[:-5]
#     vibe_titles = nlp_recommender.get_recommendations(clean_title, target_genre=genre, target_year=decade, top_n=10)
#     return {
#         "searched_movie": movie_title,
#         "recommendations": {
#             "because_you_like_the_story_vibe": vibe_titles[:5],
#             "because_people_with_your_taste_watched": hive_mind_titles[:5]
#         },
#         "system_notes": "Hybrid Engine successfully combined Collaborative and NLP models."
#     }
# --- LITE HYBRID ROUTE (Safe for Render Free Tier) ---
@app.get("/recommendations/hybrid/")
def recommend_hybrid(movie_title: str, genre: str = "All Genres", decade: str = "Any Time"):
    # Ask the Hive Mind (Collaborative)
    hive_mind_titles = collab_recommender.get_recommendations(movie_title, top_n=5)
    
    # Ask the Content AI (Substituting for NLP to save memory)
    ai_titles = recommender.get_recommendations(movie_title, top_n=5)
    
    # Package it exactly how the React frontend expects it!
    return {
        "searched_movie": movie_title,
        "recommendations": {
            "because_you_like_the_story_vibe": ai_titles,
            "because_people_with_your_taste_watched": hive_mind_titles
        },
        "system_notes": "Lite Hybrid Engine running (Content AI + Collaborative)."
    }
