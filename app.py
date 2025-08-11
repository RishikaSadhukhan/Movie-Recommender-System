import pickle
import requests
from flask import Flask, render_template, request
import time
time.sleep(0.2)  # small delay between requests


app = Flask(__name__, static_url_path='/static')

# Load movie data and similarity matrix
movies = pickle.load(open('model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))


# Fetch movie poster from TMDB
API_KEY = "a714aca5bc120c6a5cfcc8e0628b4dc5"

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)  # timeout to avoid hanging
        response.raise_for_status()
        data = response.json()
        
        # If poster path exists, return full URL, else fallback
        if data.get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
        else:
            return "/static/fallback.jpg"  # <-- you need to put a fallback.jpg in /static
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for {movie_id}: {e}")
        return "/static/fallback.jpg"

# Recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended.append({
            'title': movies.iloc[i[0]].title,
            'poster': fetch_poster(movie_id)
        })
    return recommended

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_list = movies['title'].values
    recommendations = []
    selected_movie = None
    
    if request.method == 'POST':
        selected_movie = request.form['movie']
        recommendations = recommend(selected_movie)
    
    return render_template(
        'index.html',
        movie_list=movie_list,
        selected_movie=selected_movie,
        recommendations=recommendations
    )

if __name__ == '__main__':
    app.run(debug=True)
