const API_KEY = '738f8682fc5143163b145d03a2016b0b'; // Thay bằng key bảo mật
const BASE_URL = 'https://api.themoviedb.org/3/';
let currentMovieId = 19995; // Mặc định là Avatar (2009)


document.addEventListener("DOMContentLoaded", () => {
    const movieTitle = getQueryParam("title");
    if (movieTitle) {
        document.getElementById("search-input").value = decodeURIComponent(movieTitle);
        searchMovie(); // Gọi hàm tìm kiếm ngay khi trang load
    }
});

document.addEventListener("DOMContentLoaded", () => {
    const movieTitle = getQueryParam("title");
    if (movieTitle) {
        searchMovieByTitle(movieTitle);
    }
});

function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
}

async function searchMovieByTitle(title) {
    try {
        const response = await fetch(`${BASE_URL}search/movie?api_key=${API_KEY}&language=vi-VN&query=${encodeURIComponent(title)}`);
        const data = await response.json();

        if (data.results.length > 0) {
            const movieId = data.results[0].id;
            fetchMovieData(movieId);
        } else {
            alert("Không tìm thấy phim.");
        }
    } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
    }
}


async function fetchMovieData(movieId) {
    try {
        const response = await fetch(`${BASE_URL}movie/${movieId}?api_key=${API_KEY}&language=vi-VN&append_to_response=videos,credits,images`);
        const data = await response.json();

        document.getElementById("title").textContent = `${data.title} (${data.release_date.split('-')[0]})`;
        document.getElementById("release-date").textContent = `${data.release_date}`;
        document.getElementById("genres").textContent = ` ${data.genres.map(g => g.name).join(', ')}`;
        document.getElementById("runtime").textContent = ` ${data.runtime} min `;
        document.getElementById("overview").textContent = data.overview;
        document.getElementById("poster").src = `https://image.tmdb.org/t/p/w500${data.poster_path}`;
        document.getElementById("score").textContent = `${Math.round(data.vote_average * 10)}%`;

        const director = data.credits.crew.find(person => person.job === "Director");
        document.getElementById("director").textContent = director ? director.name : "Không rõ";

        // Lấy video trailer đầu tiên
        const trailer = data.videos.results.length > 0 ? data.videos.results[0] : null;
        document.getElementById("trailer-btn").onclick = () => {
            if (trailer) {
                window.open(trailer.site === "YouTube" ? 
                    `https://www.youtube.com/watch?v=${trailer.key}` : trailer.url, 
                    "_blank"
                );
            } else {
                alert("Không tìm thấy trailer.");
            }
        };
        

        // Cập nhật ảnh nền (backdrop)
        if (data.backdrop_path) {
            document.querySelector(".background-overlay").style.backgroundImage = `url(https://image.tmdb.org/t/p/original${data.backdrop_path})`;
        }
    } catch (error) {
        console.error("Lỗi tải dữ liệu:", error);
    }
}

async function searchMovie() {
    const query = document.getElementById("search-input").value.trim();
    if (!query) return;

    try {
        const response = await fetch(`${BASE_URL}search/movie?api_key=${API_KEY}&language=vi-VN&query=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.results.length > 0) {
            currentMovieId = data.results[0].id;
            fetchMovieData(currentMovieId);
        } else {
            alert("Không tìm thấy phim.");
        }
    } catch (error) {
        console.error("Lỗi tìm kiếm:", error);
    }
}

document.getElementById("search-btn").addEventListener("click", searchMovie);

// Load phim mặc định
fetchMovieData(currentMovieId);
