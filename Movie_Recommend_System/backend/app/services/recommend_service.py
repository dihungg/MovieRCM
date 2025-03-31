import openai
import os
import pandas as pd
from app.config.config import Config
import difflib
import json
from dotenv import load_dotenv
import requests
from functools import lru_cache

# Khởi tạo OpenAI client
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Xác định đường dẫn tuyệt đối của `movie.csv`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn của recommend_service.py
DATA_PATH = os.path.join(BASE_DIR, "../../data/movie.csv")  # Lùi 2 cấp thư mục lên

# Kiểm tra file có tồn tại không
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")

# Đọc dữ liệu phim từ file CSV
df = pd.read_csv(DATA_PATH)

# Chuẩn hóa dữ liệu
df["title_lower"] = df["Title"].str.lower()
df["Genre"] = df["Genre"].str.lower()
df["Actors"] = df["Actors"].str.lower().str.replace(", ", ",", regex=False).fillna("")

def extract_requirements(user_input):
    """Phân tích yêu cầu người dùng bằng OpenAI"""
    prompt = f"""
    Phân tích yêu cầu: "{user_input}"
    Trả về JSON chứa:
    - "actors": list diễn viên (viết thường, cách nhau bằng phẩy)
    - "genres": list thể loại (viết thường)
    
    Ví dụ: 
    Input: "phim drama có Tom Hanks" 
    Output: {{"actors": ["tom hanks"], "genres": ["drama"]}}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)



def filter_local_movies(actors=[], genres=[]):
    """Lọc phim từ dataset theo điều kiện"""
    mask = pd.Series([True]*len(df))
    
    if actors:
        actor_mask = pd.Series([False]*len(df))
        for actor in actors:
            actor_mask |= df["Actors"].str.contains(actor.lower(), na=False)
        mask &= actor_mask
    
    if genres:
        genre_mask = pd.Series([False]*len(df))
        for genre in genres:
            closest_genre = difflib.get_close_matches(
                genre.lower(), 
                df["Genre"].unique(), 
                n=1, 
                cutoff=0.6
            )
            if closest_genre:
                genre_mask |= df["Genre"].str.contains(closest_genre[0], na=False)
        mask &= genre_mask
    
    return df[mask]["Title"].tolist()

# ==================== TMDB API Functions ====================
@lru_cache(maxsize=100)
def get_genre_id(genre_name):
    """Lấy ID thể loại từ TMDB"""
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    genres = requests.get(url).json()["genres"]
    for g in genres:
        if g["name"].lower() == genre_name.lower():
            return g["id"]
    return None

def get_movies_by_actor(actor_name):
    """Lấy phim từ TMDB theo diễn viên"""
    url = f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={actor_name}"
    response = requests.get(url).json()
    
    if response["results"]:
        actor_id = response["results"][0]["id"]
        movies_url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={TMDB_API_KEY}"
        movies_response = requests.get(movies_url).json()
        return [movie["title"] for movie in movies_response.get("cast", [])]
    return []

# Hàm gọi OpenAI API để gợi ý phim
def get_movie_recommendations(user_input, requirements):
    """Kết hợp AI và rule-based recommendations"""
    # Rule-based filtering
    local_results = filter_local_movies(requirements.get("actors", []), requirements.get("genres", []))
    
    # TMDB results
    tmdb_results = []
    for actor in requirements.get("actors", []):
        tmdb_results += get_movies_by_actor(actor)
    
    # Combine and validate
    combined = list(set(local_results + tmdb_results))
    valid_movies = [movie for movie in combined if movie in df["Title"].values]
    
    # AI fallback
    if not valid_movies:
        prompt = f"""
        Danh sách phim: {', '.join(df['Title'].tolist()[:200])}
        Thể loại: {', '.join(df['Genre'].unique()[:50])}
        Yêu cầu: {user_input}
        Đề xuất phim kết hợp các yếu tố trên (nếu có). Chỉ trả về tên phim.
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        valid_movies = [x.strip() for x in response.choices[0].message.content.split("\n")]
    
    return valid_movies[:5]
