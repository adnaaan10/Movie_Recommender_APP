import streamlit as st
import pickle
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = st.secrets["api_key"]

st.write(f"API Key: {api_key}")



st.set_option('client.showErrorDetails', False)

# Define a placeholder image for when the poster is not available
DEFAULT_POSTER = "https://img.freepik.com/free-vector/cinema-realistic-poster-with-illuminated-bucket-popcorn-drink-3d-glasses-reel-tickets-blue-background-with-tapes-vector-illustration_1284-77070.jpg"



# Cache the poster fetching function
@st.cache
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

    try:
        # Use a session to make the request
        with requests.Session() as session:
            response = session.get(url)
            response.raise_for_status()  # Raises an error for HTTP errors
            data = response.json()

            # Check if 'poster_path' exists and return the poster URL
            if data and 'poster_path' in data and data['poster_path']:
                poster_path = data['poster_path']
                full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return full_path
            else:
                # Return default placeholder if no poster is available
                return DEFAULT_POSTER

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return DEFAULT_POSTER  # Return default poster in case of an error


# Recommend movies based on a selected movie
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    # Get 5 movie recommendations
    for i in distances[1:6]:  # Start from 1 to exclude the selected movie itself
        movie_id = movies.iloc[i[0]].movie_id
        poster = fetch_poster(movie_id)  # Fetch poster
        recommended_movie_posters.append(poster)
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters


# Streamlit App
st.header('Movie Recommendation System')

# Load the movies and similarity data

movies = pickle.load(open('Resources/Movie_list.pkl', 'rb'))
similarity = pickle.load(open('Resources/Similarity.pkl', 'rb'))

# Movie list dropdown with a unique key to avoid duplicate widget ID
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list, key="movie_selectbox")

# Store recommendations in session state to persist them across runs
if 'recommended_movie_names' not in st.session_state:
    st.session_state.recommended_movie_names = []
    st.session_state.recommended_movie_posters = []

# If button is clicked, get recommendations
if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    # Store the results in session state
    st.session_state.recommended_movie_names = recommended_movie_names
    st.session_state.recommended_movie_posters = recommended_movie_posters

# Display recommendations from session state
if st.session_state.recommended_movie_names:
    col1, col2, col3, col4, col5 = st.columns(5)

    for i, col in enumerate([col1, col2, col3, col4, col5]):
        if i < len(st.session_state.recommended_movie_names):  # Check if there are enough recommendations
            with col:
                st.text(st.session_state.recommended_movie_names[i])
                st.image(st.session_state.recommended_movie_posters[i])
