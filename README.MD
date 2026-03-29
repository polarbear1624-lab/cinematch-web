🎬 CineMatch: AI Film Curator
Stop scrolling endlessly. Discover your next favorite movie through advanced Deep Learning and Collaborative Filtering.

CineMatch is a full-stack, AI-powered web application that acts as your personal mechanical cinephile. Instead of relying on basic genre tags, it uses Natural Language Processing (NLP) to read movie plot summaries and understand the actual "vibe" of a film, pairing it with collaborative filtering to find exactly what you should watch next.

✨ Key Features
🧠 "Vibe" Matching (Content-Based): Uses HuggingFace's all-mpnet-base-v2 sentence transformer to calculate cosine similarity between the plots of over 5,000 movies.

👯 Taste Twins (Collaborative Filtering): Recommends movies based on the viewing habits of users who share your specific cinematic taste.

🎛️ Smart Filtering: Refine AI recommendations and browse categories instantly by specific Genres and Decades.

🎞️ Rich Metadata: Integrates with the TMDB API to instantly fetch high-res posters, official YouTube trailers, and live streaming availability (e.g., Netflix, Hulu).

📝 Personal Vault: A built-in Watchlist feature to save discoveries for later.

💅 Premium UI: A custom "Midnight Cinematic" theme built with pure CSS, featuring floating cards, glassmorphism, and smooth hover animations.

🛠️ Tech Stack
The Brain (Backend):

Python & FastAPI (High-performance API routing)

Pandas (Data manipulation)

Scikit-Learn (Vector math & Cosine Similarity)

Sentence-Transformers (Deep Learning embeddings)

The Face (Frontend):

ReactJS (Built with Vite for lightning-fast hot reloading)

Pure CSS (Custom responsive styling)

TMDB API (External data fetching)

🚀 Project Roadmap
✅ Phase 1: The AI Engine & Backend
[x] Clean and preprocess a massive movie dataset (master_global_movies.csv).

[x] Train the NLP model to convert text plots into 384-dimensional math arrays.

[x] Build the hybrid recommendation logic (Vibe + Taste).

[x] Wrap the engine in a blazing-fast FastAPI server.

✅ Phase 2: The Web Interface
[x] Scaffold a modern React application using Vite.

[x] Build reusable UI components (MovieCard, FilterRow, Footer).

[x] Implement the "Midnight Cinematic" dark-mode theme.

✅ Phase 3: Integration & Polish
[x] Connect the React frontend to the Python backend via API calls (handling CORS).

[x] Integrate TMDB to fetch dynamic posters, trailers, and streaming providers.

[x] Build the "Rabbit Hole" feature (allowing users to endlessly click "Similar" on new movies).

[x] Implement local state management for the Watchlist.

⏳ Phase 4: The Launch (Current Phase)
[ ] Deploy the FastAPI Python backend to a cloud provider (Render/Railway).

[ ] Deploy the React frontend to a global edge network (Vercel/Netlify).

[ ] Connect the live URLs so the app is accessible to anyone in the world.

🔮 Phase 5: Future Enhancements
[ ] User Authentication: Add secure login/signup functionality.

[ ] Cloud Database: Migrate from a local CSV file to a managed PostgreSQL database (Supabase/Neon) to store individual user watchlists globally.

[ ] User Rating System: Allow users to rate movies 1-5 stars to actively improve the Collaborative Filtering algorithm over time.

💻 How to Run Locally
If you want to run this project on your own machine, you will need two terminal windows.

1. Start the Backend (FastAPI):

Bash
cd python-backend
pip install -r requirements.txt
uvicorn main:app --reload
(The API will be live at http://127.0.0.1:8000)

2. Start the Frontend (React):

Bash
cd cinephile-web
npm install
npm run dev
(The Web App will be live at http://localhost:5173)

👨‍💻 Developer
Manish Sahu

Location: Bhawanipatna, Odisha

Email: polarbear1624@gmail.com

Role: Full-Stack Developer & AI Enthusiast

Built with passion, coffee, and a deep love for cinema.