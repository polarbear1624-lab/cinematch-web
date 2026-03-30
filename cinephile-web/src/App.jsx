import React, { useState, useEffect } from 'react';
import './App.css'; 
import Auth from './Auth'; 
import { supabase } from './supabaseClient'; 
import AccountCenter from './AccountCenter';

const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY; 
const GENRES = ["All Genres", "Action", "Comedy", "Drama", "Sci-Fi", "Romance", "Horror", "Thriller"];
const DECADES = ["Any Time", "2020s", "2010s", "2000s", "1990s", "1980s"];

// --- 🎬 MOVIE CARD COMPONENT ---
const MovieCard = ({ title, onFindSimilar, onToggleWatchlist, isInWatchlist }) => {
  const [posterUrl, setPosterUrl] = useState("https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/500px-No-Image-Placeholder.svg.png");
  const [trailerUrl, setTrailerUrl] = useState(null);
  const [providers, setProviders] = useState([]);

  useEffect(() => {
    const fetchMovieDetails = async () => {
      let searchTitle = title.split(" (")[0];
      if (searchTitle.endsWith(", The")) searchTitle = "The " + searchTitle.slice(0, -5);

      try {
        const searchRes = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${searchTitle}`);
        const searchData = await searchRes.json();
        
        if (searchData.results && searchData.results[0]) {
          const movieId = searchData.results[0].id;
          if (searchData.results[0].poster_path) setPosterUrl(`https://image.tmdb.org/t/p/w500${searchData.results[0].poster_path}`);

          const videoRes = await fetch(`https://api.themoviedb.org/3/movie/${movieId}/videos?api_key=${TMDB_API_KEY}`);
          const videoData = await videoRes.json();
          const trailer = videoData.results?.find(vid => vid.site === 'YouTube' && vid.type === 'Trailer');
          if (trailer) setTrailerUrl(`https://www.youtube.com/watch?v=${trailer.key}`);

          const provRes = await fetch(`https://api.themoviedb.org/3/movie/${movieId}/watch/providers?api_key=${TMDB_API_KEY}`);
          const provData = await provRes.json();
          const usData = provData.results?.US?.flatrate;
          if (usData) setProviders(usData.slice(0, 2).map(p => p.provider_name));
        }
      } catch (error) {}
    };
    fetchMovieDetails();
  }, [title]);

  return (
    <div className="movie-card">
      <img src={posterUrl} alt={title} className="poster" />
      <div className="card-content">
        <h4 className="card-title" title={title}>{title}</h4>
        <p className="provider-text">{providers.length > 0 ? `📺 ${providers.join(', ')}` : "🍿 Not streaming"}</p>

        {trailerUrl && (
          <button className="trailer-btn" onClick={() => window.open(trailerUrl, '_blank')}>
            ▶ Watch Trailer
          </button>
        )}

        <div className="button-row">
          <button 
            className={`action-btn ${isInWatchlist ? 'active-saved' : ''}`} 
            onClick={() => onToggleWatchlist(title)}
          >
            {isInWatchlist ? "✓ Saved" : "+ Save"}
          </button>
          <button className="action-btn secondary" onClick={() => onFindSimilar(title)}>
            🪄 Similar
          </button>
        </div>
      </div>
    </div>
  );
};

// --- 💻 MAIN APP COMPONENT ---
export default function App() {
  const [user, setUser] = useState(null); 
  const [activeTab, setActiveTab] = useState("Search");
  const [selectedGenre, setSelectedGenre] = useState("All Genres");
  const [selectedDecade, setSelectedDecade] = useState("Any Time");
  
  const [searchQuery, setSearchQuery] = useState("");
  const [vibeMovies, setVibeMovies] = useState([]);
  const [tasteMovies, setTasteMovies] = useState([]);
  const [browseMovies, setBrowseMovies] = useState([]);
  const [browseTitle, setBrowseTitle] = useState("");
  const [watchlist, setWatchlist] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // NEW STATES FOR DROPDOWN AND USERNAME
  const [profileName, setProfileName] = useState("Cinephile"); 
  const [showDropdown, setShowDropdown] = useState(false);

  // Check Supabase session AND load permanent watchlist + profile
  useEffect(() => {
    const fetchUserData = async (currentUser) => {
      if (!currentUser) return;
      
      // 1. Fetch Watchlist
      const { data: watchData } = await supabase
        .from('watchlists')
        .select('movie_title')
        .eq('user_id', currentUser.id);
        
      if (watchData) {
        setWatchlist(watchData.map(row => row.movie_title));
      }

      // 2. Fetch Profile Name
      const { data: profileData } = await supabase
        .from('profiles')
        .select('username')
        .eq('id', currentUser.id)
        .single();
        
      if (profileData && profileData.username) {
        setProfileName(profileData.username);
      } else {
        // Fallback: Use the first part of their email if no name is set yet
        setProfileName(currentUser.email.split('@')[0]);
      }
    };

    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      if (session?.user) fetchUserData(session.user);
    });
    
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (session?.user) {
        fetchUserData(session.user);
      } else {
        setWatchlist([]); 
        setProfileName("Cinephile");
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  const fetchRecommendations = async (query) => {
    if (!query) return;
    setIsLoading(true);
    setSearchQuery(query);
    setActiveTab("Search");
    setVibeMovies([]);
    setTasteMovies([]);

    try {
      // Use the deployed Render backend instead of localhost
      const API_URL = `https://cinematch-web.onrender.com/recommendations/hybrid/?movie_title=${encodeURIComponent(query)}&genre=${encodeURIComponent(selectedGenre)}&decade=${encodeURIComponent(selectedDecade)}`;
      const response = await fetch(API_URL);
      const data = await response.json();

      if (data.recommendations) {
        setVibeMovies(data.recommendations.because_you_like_the_story_vibe || []);
        setTasteMovies(data.recommendations.because_people_with_your_taste_watched || []);
      } else {
        alert("Movie not found in the archives.");
      }
    } catch (error) { alert("🚨 Backend disconnected!"); }
    finally { setIsLoading(false); }
  };

  const fetchBrowse = async () => {
    setIsLoading(true);
    setBrowseMovies([]);
    try {
      // Use the deployed Render backend instead of localhost
      const API_URL = `https://cinematch-web.onrender.com/browse/?genre=${encodeURIComponent(selectedGenre)}&decade=${encodeURIComponent(selectedDecade)}`;
      const response = await fetch(API_URL);
      const data = await response.json();
      
      if (data.movies) {
        setBrowseMovies(data.movies);
        setBrowseTitle(`✨ Top ${selectedGenre} of the ${selectedDecade}`);
      }
    } catch (error) { alert("🚨 Backend disconnected!"); }
    finally { setIsLoading(false); }
  };

  // Save directly to Cloud Database
  const handleToggleWatchlist = async (title) => {
    if (!user) return alert("You must be logged in to save movies!");

    if (watchlist.includes(title)) {
      await supabase.from('watchlists').delete().match({ user_id: user.id, movie_title: title });
      setWatchlist(watchlist.filter(m => m !== title));
    } else {
      await supabase.from('watchlists').insert({ user_id: user.id, movie_title: title });
      setWatchlist([...watchlist, title]);
    }
  };

  // --- REUSABLE FILTER ROW ---
  const FilterRow = ({ title, options, selected, onSelect }) => (
    <div className="filter-section">
      <span className="filter-title">{title}</span>
      <div className="chip-container">
        {options.map(opt => (
          <button 
            key={opt} 
            className={`chip ${selected === opt ? 'active' : ''}`}
            onClick={() => onSelect(opt)}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );

  // --- THE GATEKEEPER ---
  if (!user) {
    return (
      <div className="app-container">
        <header className="hero-section">
          <h1 className="hero-logo">CINEMATCH</h1>
          <span className="hero-tagline">YOUR AI FILM CURATOR</span>
        </header>
        <Auth onLogin={(loggedInUser) => setUser(loggedInUser)} />
      </div>
    );
  }

  return (
    <div className="app-container">
      
      {/* --- PREMIUM HERO SECTION --- */}
      <header className="hero-section" style={{ position: 'relative' }}>
        
        {/* NEW: Interactive User Profile Dropdown */}
        <div className="top-right-controls">
          <div className="user-menu-trigger" onClick={() => setShowDropdown(!showDropdown)}>
            <div className="user-avatar">🍿</div>
            <span className="user-greeting">{profileName}</span>
            <span className="dropdown-arrow">▼</span>
          </div>

          {showDropdown && (
            <div className="user-dropdown-menu">
              <button 
                onClick={() => { setActiveTab("Account"); setShowDropdown(false); }} 
                className="dropdown-item"
              >
                👤 Edit Profile
              </button>
              <button onClick={handleLogout} className="dropdown-item logout-text">
                🚪 Sign Out
              </button>
            </div>
          )}
        </div>

        <h1 className="hero-logo">CINEMATCH</h1>
      </header>

      {/* TABS */}
      <div className="tab-bar-wrapper">
        <div className="tab-bar">
          {["Search", "Browse", "Watchlist"].map(tab => (
            <button 
              key={tab} 
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`} 
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>
      

      {/* MAIN CONTENT AREA */}
      <main className="main-content">
        
        {/* TAB 1: SEARCH */}
        {activeTab === "Search" && (
          <div className="tab-content fade-in">
            <div className="search-box">
              <input 
                type="text" 
                placeholder="Enter a movie you love..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchRecommendations(searchQuery)}
              />
              <button className="search-btn" onClick={() => fetchRecommendations(searchQuery)}>Discover</button>
            </div>

            <FilterRow title="REFINE GENRE" options={GENRES} selected={selectedGenre} onSelect={setSelectedGenre} />
            <FilterRow title="REFINE ERA" options={DECADES} selected={selectedDecade} onSelect={setSelectedDecade} />

            {isLoading && <div className="spinner"></div>}

            {vibeMovies.length > 0 && (
              <div className="results-container">
                <h3 className="results-header">Because of the Vibe</h3>
                <div className="carousel">
                  {vibeMovies.map((movie, idx) => (
                    <MovieCard key={idx} title={movie} onFindSimilar={fetchRecommendations} onToggleWatchlist={handleToggleWatchlist} isInWatchlist={watchlist.includes(movie)} />
                  ))}
                </div>
              </div>
            )}

            {tasteMovies.length > 0 && (
              <div className="results-container">
                <h3 className="results-header">Because of your Taste Twins</h3>
                <div className="carousel">
                  {tasteMovies.map((movie, idx) => (
                    <MovieCard key={idx} title={movie} onFindSimilar={fetchRecommendations} onToggleWatchlist={handleToggleWatchlist} isInWatchlist={watchlist.includes(movie)} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: BROWSE */}
        {activeTab === "Browse" && (
          <div className="tab-content fade-in">
            <FilterRow title="SELECT GENRE" options={GENRES} selected={selectedGenre} onSelect={setSelectedGenre} />
            <FilterRow title="SELECT ERA" options={DECADES} selected={selectedDecade} onSelect={setSelectedDecade} />
            
            <button className="large-gradient-btn" onClick={fetchBrowse}>Explore Archives</button>

            {isLoading && <div className="spinner"></div>}

            {browseMovies.length > 0 && (
              <div className="results-container">
                <h3 className="results-header">{browseTitle}</h3>
                <div className="carousel">
                  {browseMovies.map((movie, idx) => (
                    <MovieCard key={idx} title={movie} onFindSimilar={fetchRecommendations} onToggleWatchlist={handleToggleWatchlist} isInWatchlist={watchlist.includes(movie)} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: WATCHLIST */}
        {activeTab === "Watchlist" && (
          <div className="tab-content fade-in">
            <h3 className="results-header">Your Collection ({watchlist.length})</h3>
            
            {watchlist.length === 0 ? (
              <div className="empty-state">
                <div className="empty-emoji">🎞️</div>
                <p>Your vault is empty.<br/>Discover some movies to save them here.</p>
              </div>
            ) : (
              <div className="grid-container">
                {watchlist.map((movie, idx) => (
                  <MovieCard key={`watch_${idx}`} title={movie} onFindSimilar={fetchRecommendations} onToggleWatchlist={handleToggleWatchlist} isInWatchlist={true} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ACCOUNT */}
        {activeTab === "Account" && (
          <div className="tab-content fade-in">
            <AccountCenter user={user} />
          </div>
        )}

      </main>

    </div>
  );
}