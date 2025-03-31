import pandas as pd
import difflib
import os
from dotenv import load_dotenv
import requests
from urllib.parse import unquote


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Xác định đường dẫn tuyệt đối của `movie.csv`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn của recommend_service.py
DATA_PATH = os.path.join(BASE_DIR, "../../data/movie.csv")  # Lùi 2 cấp thư mục lên

# Kiểm tra file có tồn tại không
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")

# Đọc dữ liệu phim từ file CSV
df = pd.read_csv(DATA_PATH, dtype={
    "imdbRating": float,
    "rottenRating": float
})
df["title_lower"] = df["Title"].str.lower()  # Chuẩn hóa cột tiêu đề

# Hàm lấy ID phim từ TMDB
def get_movie_id_tmdb(movie_name):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
    response = requests.get(url).json()
    return response["results"][0]["id"] if response.get("results") else None

# Hàm lấy trailer của phim từ TMDB
def get_movie_trailer_tmdb(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    trailers = [v for v in requests.get(url).json().get("results", []) 
               if v["type"] == "Trailer" and v["site"] == "YouTube"]
    return f"https://www.youtube.com/watch?v={trailers[0]['key']}" if trailers else None

def get_movie_details(movie_name):
    movie_name = unquote(movie_name).lower().strip() 
    matches = difflib.get_close_matches(
        movie_name,
        df["title_lower"].tolist(),
        n=1,
        cutoff=0.6  # Giảm cutoff để tăng độ linh hoạt
    )
    if not matches:
        # Thử tìm kiếm theo từ khóa
        matched_rows = df[df["title_lower"].str.contains(movie_name, case=False, na=False)]
        if not matched_rows.empty:
            matches = [matched_rows.iloc[0]["title_lower"]]
    
    if matches:
        movie = df[df["title_lower"] == matches[0]].iloc[0]
        movie_id = get_movie_id_tmdb(movie["Title"])
        return {
            "title": movie["Title"],
            "overview": movie.get("Overview", "Không có mô tả."),
            # CHUYỂN ĐỔI SANG KIỂU PYTHON
            "ratingIMDB": float(movie.get("imdbRating", 0)),  # <-- Sửa ở đây
            "ratingRotten": float(movie.get("rottenRating", 0)),  # <-- Và ở đây
            "poster": movie.get("Poster_Link", None),
            "actors": movie.get("Actors", "N/A"),
            "director": movie.get("Director", "N/A"),
            "runtime": int(movie["Runtime (min)"]) if not pd.isna(movie["Runtime (min)"]) else "N/A",
            "genre": movie.get("Genre", "N/A"),
            "trailer": get_movie_trailer_tmdb(movie_id) if movie_id else None
        }
    return None
