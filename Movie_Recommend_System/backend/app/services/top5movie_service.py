from app.services.movie_service import get_movie_details, get_movie_id_tmdb
from app.services.recommend_service import get_movie_recommendations, extract_requirements
from dotenv import load_dotenv
import requests
import os
import pandas as pd
import difflib

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Xác định đường dẫn tuyệt đối của `movie.csv`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Đường dẫn của recommend_service.py
DATA_PATH = os.path.join(BASE_DIR, "../../data/movie.csv")  # Lùi 2 cấp thư mục lên

# Kiểm tra file có tồn tại không
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Không tìm thấy file: {DATA_PATH}")

# Đọc dữ liệu phim từ file CSV
df = pd.read_csv(DATA_PATH)
df["title_lower"] = df["Title"].str.lower()
df["Genre"] = df["Genre"].str.lower()
df["Actors"] = df["Actors"].str.lower().str.replace(", ", ",", regex=False).fillna("")

def get_movie_details_tmdb(movie_id):
    """Lấy thông tin chi tiết từ TMDB"""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title"),
            "overview": data.get("overview"),
            "release_date": data.get("release_date"),
            "poster": f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}"
        }
    return None

def find_exact_match(user_input):
    """Tìm kiếm chính xác tên phim với fuzzy matching"""
    # Chuẩn hóa input
    normalized_input = user_input.strip().lower()
    
    # Tìm kiếm trong dataset
    matches = difflib.get_close_matches(
        normalized_input,
        df["title_lower"].tolist(),
        n=1,
        cutoff=0.8  # Tăng độ chính xác
    )
    
    if matches:
        # Kiểm tra thêm độ tương đồng
        match_score = difflib.SequenceMatcher(
            None, normalized_input, matches[0]
        ).ratio()
        
        if match_score >= 0.9:
            return df[df["title_lower"] == matches[0]]["Title"].iloc[0]
    
    # Kiểm tra TMDB
    tmdb_id = get_movie_id_tmdb(user_input)
    if tmdb_id:
        details = get_movie_details_tmdb(tmdb_id)
        return details.get("title")
    
    return None


def preprocess_input(user_input):
    """Tự động thêm 'tôi thích xem phim' nếu chưa có, trừ khi nhập tên phim cụ thể."""
    user_input = user_input.strip().lower()
    
    # Kiểm tra nếu input trùng với tên phim trong dataset
    movie_titles = df["title_lower"].tolist()
    if user_input in movie_titles:
        return user_input  # Giữ nguyên nếu là tên phim cụ thể
    
    # Nếu không, kiểm tra và thêm 'tôi thích xem phim' nếu cần
    if not user_input.startswith("tôi thích xem phim "):
        return f"tôi thích xem phim {user_input}"
    
    return user_input

# Hàm gợi ý phim chỉ trả về tên phim với điểm cao nhất
def recommend_movies(user_input):
    """Luồng đề xuất chính đã được cải tiến"""
    print(f"\n=== New Request: {user_input} ===")
     # Bước 0: Tiền xử lý input
    processed_input = preprocess_input(user_input)
    
    # Bước 1: Tìm kiếm chính xác
    exact_match = find_exact_match(processed_input)
    if exact_match:
        print("Exact match found:", exact_match)
        return [get_movie_details(exact_match)] if get_movie_details(exact_match) else []

    # Bước 2: Phân tích yêu cầu
    try:
        requirements = extract_requirements(user_input)
        print("Parsed Requirements:", requirements)
    except Exception as e:
        print("Error parsing requirements:", e)
        requirements = {}

    # Bước 3: Lấy danh sách phim
    movie_list = get_movie_recommendations(user_input, requirements)
    print("Filtered Movies:", movie_list)
    
    # Bước 4: Xử lý chi tiết phim
    movie_details_list = []
    for movie in movie_list:
        details = get_movie_details(movie)
        if details and "ratingIMDB" in details:
            movie_details_list.append({
                "title": details["title"],
                "poster": details["poster"],
                "total_rating": details["ratingIMDB"]
            })
    sorted_movies = sorted(movie_details_list, key=lambda x: -x["total_rating"])
    
    # Bước 5: Sắp xếp theo rating
    return [{"title": movie["title"], "poster": movie["poster"]} for movie in sorted_movies[:5]]

