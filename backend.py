import pandas as pd
import re
import google.generativeai as genai
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (serves App.html and App.css)
app.mount("/static", StaticFiles(directory="."), name="static")

# Serve the main HTML page
@app.get("/")
def serve_homepage():
    return FileResponse("App.html")

# Load movie dataset
df = pd.read_csv("merged_file_movie.csv")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GENRE_KEYWORDS = {
    "comedy": ["comedy", "funny", "laugh", "hilarious"],
    "action": ["action", "fight", "battle", "war", "explosions"],
    "sci-fi": ["sci-fi", "science fiction", "space", "future", "aliens"],
    "thriller": ["thriller", "suspense", "mystery", "tense"],
    "romance": ["romance", "love", "romantic", "heartfelt"],
    "horror": ["horror", "scary", "ghost", "frightening"],
    "drama": ["drama", "emotional", "serious", "realistic"]
}

@app.get("/random_movies")
def get_random_movies():
    """Return 3 random high-rated movies."""
    top_movies = df.nlargest(1000, "imdbRating")
    selected_movies = top_movies.sample(n=3)
    
    movies_list = [
        {
            "title": row["Title"],
            "poster": row["Poster_Link"],
            "genre": row["Genre"],
            "actors": row["Actors"], 
            "imdb_rating": row["imdbRating"],
            "rotten_rating": row["rottenRating"],
            "description": row["Overview"],
            "year": row["Year"],
            "director": row["Director"],
            "runtime": row["Runtime (min)"]
        }
        for _, row in selected_movies.iterrows()
    ]

    return JSONResponse(content={"movies": movies_list})

def detect_genre(user_query: str):
    """Detects the genre in user input."""
    user_query = user_query.lower()
    for genre, keywords in GENRE_KEYWORDS.items():
        if any(keyword in user_query for keyword in keywords):
            return genre
    return None  # No genre detected

def extract_year(user_query: str):
    """Extracts a year from user input (e.g., 'movies from 2010')."""
    match = re.search(r"\b(19\d{2}|20\d{2})\b", user_query)
    return int(match.group()) if match else None

def extract_runtime(user_query: str):
    """Extracts runtime information (e.g., 'movies under 90 minutes')."""
    match = re.search(r"(\d+)\s?(minutes|min)", user_query)
    return int(match.group(1)) if match else None

def recommend_movies(query: str):
    """Recommend movies based on user input (Genre, Actor, Director, Year, Runtime)."""
    query_lower = query.lower().strip()
    detected_genre = detect_genre(query_lower)
    detected_year = extract_year(query_lower)
    detected_runtime = extract_runtime(query_lower)

    # 1️⃣ Filter by Genre
    if detected_genre:
        filtered_movies = df[df["Genre"].str.contains(detected_genre, case=False, na=False)]
        response_text = f"Here are some {detected_genre} movies you might like!"

    # 2️⃣ Filter by Year
    elif detected_year:
        filtered_movies = df[df["Year"] == detected_year]
        response_text = f"Here are some movies from {detected_year}!"

    # 3️⃣ Filter by Runtime (Movies under X minutes)
    elif detected_runtime:
        filtered_movies = df[df["Runtime (min)"] <= detected_runtime]
        response_text = f"Here are some movies under {detected_runtime} minutes!"

    # 4️⃣ Filter by Director
    elif "directed by" in query_lower:
        director_name = query_lower.replace("directed by", "").strip()
        filtered_movies = df[df["Director"].str.contains(director_name, case=False, na=False)]
        response_text = f"Here are some movies directed by {director_name}!"

    # 5️⃣ Filter by Actor
    elif "with" in query_lower or "starring" in query_lower:
        actor_name = query_lower.replace("with", "").replace("starring", "").strip()
        filtered_movies = df[df["Actors"].str.contains(actor_name, case=False, na=False)]
        response_text = f"Here are some movies with {actor_name}!"

    # 6️⃣ Filter by Movie Overview (Description)
    elif "about" in query_lower:
        keyword = query_lower.replace("about", "").strip()
        filtered_movies = df[df["Overview"].str.contains(keyword, case=False, na=False)]
        response_text = f"Here are some movies about {keyword}!"

    # 7️⃣ Fallback to Keyword Matching (Title, Genre, Overview, Actors)
    else:
        important_words = [
            word for word in re.findall(r'\b\w+\b', query_lower)
            if word not in ["any", "recommend", "me", "some", "top", "movies", "please", "good", "find", "best"]
        ]

        def matches(row):
            """Check if query matches title, genre, overview, or actors."""
            content = f"{row['Title']} {row['Genre']} {row['Overview']} {row['Actors']}".lower()
            return any(word in content for word in important_words)
        
        filtered_movies = df[df.apply(matches, axis=1)]
        response_text = "Here are some movies you might like!"

    # If no results, return top-rated random picks
    if filtered_movies.empty:
        filtered_movies = df.nlargest(1000, "imdbRating").sample(n=5)
        response_text = "Couldn't find an exact match, but here are some great movies!"

    return response_text, [
        {
            "title": row["Title"],
            "poster": row["Poster_Link"],
            "genre": row["Genre"],
            "actors": row["Actors"], 
            "imdb_rating": row["imdbRating"],
            "rotten_rating": row["rottenRating"],
            "description": row["Overview"],
            "year": row["Year"],
            "director": row["Director"],
            "runtime": row["Runtime (min)"]
        }
        for _, row in filtered_movies.head(5).iterrows()
    ]

@app.get("/chatbot")
def chatbot_response(user_message: str = Query(..., description="User's movie-related message")):
    """Generate chatbot response with improved search filters."""
    response_text, recommended_movies = recommend_movies(user_message)

    if recommended_movies:
        return JSONResponse(content={"bot_response": response_text, "movies": recommended_movies})

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"You are a movie recommendation chatbot. Answer movie-related questions only. User: {user_message}")

    return JSONResponse(content={"bot_response": response.text, "movies": []})

# Run with: uvicorn backend:app --reload
# python -m http.server 8000
# Then open http://127.0.0.1:8000/static/App.html
