import openai
import os
import pandas as pd
from app.config.config import Config
import difflib
import json
from dotenv import load_dotenv
import requests
from functools import lru_cache
from typing import Tuple

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

genre_mapping = {
    # Cơ bản
    "hành động": "action",
    "hài": "comedy",
    "lãng mạn": "romance",
    "kịch": "drama",
    "kịch tính": "drama",
    "kinh dị": "horror",
    "giật gân": "thriller",
    "tội phạm": "crime",
    "bí ẩn": "mystery",
    "khoa học viễn tưởng": "Science Fiction",
    "viễn tưởng": "Science Fiction",
    "phiêu lưu": "adventure",
    "giả tưởng": "fantasy",
    "kỳ ảo": "fantasy",
    "hoạt hình": "animation",
    "âm nhạc": "musical",
    "chiến tranh": "war",
    "tài liệu": "documentary",
    "tiểu sử": "biography",
    "lịch sử": "historical",
    "gia đình": "family",
    "tâm lý": "drama",
    "siêu anh hùng": "superhero",
    "thần thoại": "mythology",
    "chiếu rạp": "theatrical",        # thường dùng cho phim chiếu rạp
    "giáo dục": "educational",
    "hành động phiêu lưu": "action adventure",
    "hài lãng mạn": "romantic comedy",
    "hài chính kịch": "comedy drama",
    "tâm lý xã hội": "social drama",
    "hình sự": "crime drama",
    # có thể thêm loại khác
}

@lru_cache(maxsize=500)
def extract_requirements(user_input: str):
    """Phân tích yêu cầu người dùng bằng OpenAI và ánh xạ thể loại"""
    prompt = f"""
    Phân tích yêu cầu: "{user_input}"
    Trả về JSON chứa:
    - "actors": list diễn viên (viết thường, cách nhau bằng phẩy)
    - "genres": list thể loại (viết thường)
    - "directors": list đạo diễn (viết thường)
    
    Ví dụ: 
    Input: "phim drama có Tom Hanks" 
    Output: {{"actors": ["tom hanks"], "genres": ["drama"], "directors": []}}
    
    Input: "phim của Christopher Nolan"
    Output: {{"actors": [], "genres": [], "directors": ["christopher nolan"]}}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    parsed_data = json.loads(response.choices[0].message.content)
    
    # Ánh xạ thể loại từ tiếng Việt sang tiếng Anh
    if "genres" in parsed_data:
        mapped_genres = []
        for genre in parsed_data["genres"]:
            # Chuẩn hóa đầu vào
            normalized_genre = genre.lower().strip()
            
            # Tìm ánh xạ chính xác
            if normalized_genre in genre_mapping:
                mapped_genres.append(genre_mapping[normalized_genre])
            else:
                # Fallback: Tìm ánh xạ gần đúng nhất
                closest_match = difflib.get_close_matches(
                    normalized_genre,
                    genre_mapping.keys(),
                    n=1,
                    cutoff=0.7
                )
                if closest_match:
                    mapped_genres.append(genre_mapping[closest_match[0]])
                else:
                    mapped_genres.append(normalized_genre)
        
        parsed_data["genres"] = list(set(mapped_genres))  # Remove duplicates
    
    return parsed_data


@lru_cache(maxsize=500)
def filter_local_movies(actors: Tuple[str], genres: Tuple[str], directors: Tuple[str]):
    """Lọc phim từ dataset theo điều kiện"""
    mask = pd.Series([True] * len(df))
    
    # Xử lý directors
    if directors:
        director_mask = pd.Series([False] * len(df))
        all_directors = set(df["Director"].str.lower().str.split(", ").sum())
        
        for director_query in directors:
            closest_director = difflib.get_close_matches(
                director_query.lower(),
                list(all_directors),
                n=1,
                cutoff=0.7
            )
            
            if closest_director:
                print(f"Mapped director: {director_query} -> {closest_director[0]}")
                director_mask |= df["Director"].str.lower().str.contains(closest_director[0], na=False)
        
        mask &= director_mask
    
    # Xử lý actors với fuzzy matching
    if actors:
        actor_mask = pd.Series([False] * len(df))
        
        all_actors = set()
        
        for actor_list in df["Actors"].str.lower().str.split(", "):
            if isinstance(actor_list, list):
                all_actors.update(actor_list)
        
        for actor in actors:
            # Tìm genre gần nhất trong danh sách đã tách
            closest_actor = difflib.get_close_matches(
                actor.lower(), 
                list(all_actors), 
                n=1, 
                cutoff=0.7  # Giảm cutoff để bắt với tên gần giống
            )
            
            if closest_actor:
                print(f"Mapped actor: {actor} -> {closest_actor[0]}")
                actor_mask |= df["Actors"].str.lower().str.contains(closest_actor[0], na=False)
        
        mask &= actor_mask
    # Xử lý genres như cũ
    if genres:
        genre_mask = pd.Series([False] * len(df))
        
        # Tạo danh sách tất cả genre đơn lẻ trong dataset
        all_genres = set()
        for genre_list in df["Genre"].str.lower().str.split(", "):
            if isinstance(genre_list, list):
                all_genres.update(genre_list)
        
        for genre in genres:
            # Tìm genre gần nhất trong danh sách đã tách
            closest_genre = difflib.get_close_matches(
                genre.lower(), 
                list(all_genres), 
                n=1, 
                cutoff=0.6  # Giảm cutoff để bắt "scifi" -> "sci-fi"
            )
            
            if closest_genre:
                print(f"Mapped genre: {genre} -> {closest_genre[0]}")
                genre_mask |= df["Genre"].str.lower().str.contains(closest_genre[0], na=False)
        
        mask &= genre_mask
    
    return tuple(df[mask]["Title"].tolist()) if mask.any() else tuple()

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

@lru_cache(maxsize=200)
def get_movies_by_actor(actor_name):
    """Lấy phim từ TMDB theo diễn viên (giới hạn 10 phim)"""
    url = f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={actor_name}"
    response = requests.get(url).json()
    
    if response["results"]:
        actor_id = response["results"][0]["id"]
        movies_url = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={TMDB_API_KEY}"
        movies_response = requests.get(movies_url).json()
        # Thêm slice [:10] để lấy tối đa 10 phim đầu tiên
        return tuple(movie["title"] for movie in movies_response.get("cast", [])[:10])
    return tuple()
    
# ==================== Core Recommendation Logic ====================
def get_movie_recommendations(user_input: str, requirements: dict):
    """Kết hợp AI và rule-based recommendations"""
    # Rule-based filtering
    # Chuyển đổi yêu cầu sang dạng hashable
    actors = tuple(requirements.get("actors", []))
    genres = tuple(requirements.get("genres", []))
    directors = tuple(requirements.get("directors", []))
    local_results = filter_local_movies(actors, genres, directors)
    print("[Source] Rule-based results:", local_results)  # <-- Thêm dòng này
    
    # TMDB results
    tmdb_results = []
    for actor in requirements.get("actors", []):
        actor_movies = get_movies_by_actor(actor)
        tmdb_results += actor_movies
        print(f"[Source] TMDB results for {actor}:", actor_movies)  # <-- Thêm dòng này
    
    # Combine and validate
    combined = list(set(list(local_results) + tmdb_results))
    print("[Source] Combined results before validation:", combined)  # <-- Thêm dòng này
    
    valid_movies = [movie for movie in combined if movie in df["Title"].values]
    print("[Source] Valid movies after local check:", valid_movies)  # <-- Thêm dòng này
    
    # AI fallback
    valid_movies_fuzzy = []
    
    if not valid_movies:
        print("[Source] Triggering AI fallback")  # <-- Thêm dòng này
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
        print("[Source] AI generated results:", valid_movies)
        
        # Xử lý fuzzy matching
        valid_movies_fuzzy = []
        for valid_movie in valid_movies:
            closest_match = difflib.get_close_matches(
                valid_movie,
                df['Title'].tolist(),
                n=1,
                cutoff=0.6
            )
            if closest_match:
                valid_movies_fuzzy.append(closest_match[0])
                
        valid_movies = list(set(valid_movies_fuzzy))  # <-- Cập nhật valid_movies
    
    # Nếu không dùng AI fallback, xử lý fuzzy matching cho kết quả thường
    else:
        valid_movies_fuzzy = []
        for movie in valid_movies:
            closest_match = difflib.get_close_matches(
                movie,
                df['Title'].tolist(),
                n=1,
                cutoff=0.6
            )
            if closest_match:
                valid_movies_fuzzy.append(closest_match[0])
        
        valid_movies = list(set(valid_movies_fuzzy))  # <-- Cập nhật lại
    
    # Lọc phim tồn tại trong dataset
    valid_movies_in_df = [title for title in valid_movies if title in df['Title'].values]
    
    # Sắp xếp
    sorted_movies = sorted(
        valid_movies_in_df,
        key=lambda title: df.loc[df['Title'] == title, 'imdbRating'].values[0],
        reverse=True
    )[:5]

    return sorted_movies
