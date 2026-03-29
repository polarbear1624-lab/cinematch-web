import pickle

print("⏳ Shrinking the movie list to match the 2500 matrix...")
with open('models/movies_list.pkl', 'rb') as f:
    movies = pickle.load(f)

# Safely shrink it down based on exactly what type of data it is
if isinstance(movies, dict):
    # If it's a Dictionary
    lite_movies = dict(list(movies.items())[:2500])
elif hasattr(movies, 'iloc'):
    # If it's a Pandas DataFrame or Series
    lite_movies = movies.iloc[:2500]
else:
    # If it's a standard List
    lite_movies = movies[:2500]

with open('models/movies_list_lite.pkl', 'wb') as f:
    pickle.dump(lite_movies, f)

print("✅ Success! Movie list is synced.")