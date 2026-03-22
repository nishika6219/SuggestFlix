import streamlit as st
import pandas as pd
import requests
import pickle
import os

# ---------------------------
# Load data with caching
# ---------------------------
@st.cache_data
def load_data():
    with open('movie_dict.pkl', 'rb') as file:
        movies, cosine_sim = pickle.load(file)
    return movies, cosine_sim

movies, cosine_sim = load_data()

# ---------------------------
# Recommendation function
# ---------------------------
def get_recommendations(title):
    if title not in movies['title'].values:
        return pd.DataFrame(columns=['title', 'movie_id'])
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # top 10
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# ---------------------------
# Poster fetch function
# ---------------------------
def fetch_poster(movie_id):
    api_key = os.getenv("TMDB_API_KEY", "05e71f7da661348ccbd7a896e7254338")
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    
    response = requests.get(url)
    data = response.json()
    
    poster_path = data.get('poster_path')
    if poster_path:
        return f'https://image.tmdb.org/t/p/w500/{poster_path}'
    else:
        return 'https://via.placeholder.com/130x200?text=No+Image'

# ---------------------------
# Streamlit UI
# ---------------------------
st.title('SuggestFlix 🎬')

# Search bar + dropdown
search_query = st.text_input("Search for a movie")
if search_query:
    filtered = movies[movies['title'].str.contains(search_query, case=False)]
    if not filtered.empty:
        selected_movie = st.selectbox('Select a movie', filtered['title'].values)
    else:
        st.warning("No movies found with that search term.")
        selected_movie = None
else:
    selected_movie = st.selectbox('Select a movie', movies['title'].values)

# Show recommendations
if selected_movie and st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)

    if recommendations.empty:
        st.write("No recommendations found.")
    else:
        for i in range (0,10,5):
            cols = st.columns(5)
            for col, j in zip(cols, range(i, i+5)):
                if j< len(recommendations):
                    moviee_title =recommendations.iloc[j]['title']
                    moviee_id = recommendations.iloc[j]['movie_id']
                    poster_url = fetch_poster(moviee_id)
                    with col:   
                        st.image(poster_url, width=130)
                        st.write(moviee_title)
    #     cols = st.columns(len(recommendations))
    #     for col, (_, row) in zip(cols, recommendations.iterrows()):
    #         poster_url = fetch_poster(row['movie_id'])
    #         with col:
    #             st.image(poster_url, width=130)
    #             st.write(row['title'])
