const API_KEY = '738f8682fc5143163b145d03a2016b0b'; // Thay bằng key bảo mật
const BASE_URL = 'https://api.themoviedb.org/3/';

document.addEventListener("DOMContentLoaded", function () {
    fetchAndProcessCSV();
    
    const movieModal = document.getElementById("movieModal");
    const closeModal = document.querySelector(".close");

    closeModal.addEventListener("click", function () {
        movieModal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === movieModal) {
            movieModal.style.display = "none";
        }
    });
});

let movies = [];

// Đọc file CSV
function fetchAndProcessCSV() {
    fetch("movie.csv")
        .then(response => response.text())
        .then(data => {
            movies = parseCSV(data);
            console.log("Movies đã tải:", movies);
            if (movies.length > 0) {
                displayGenres();
            } else {
                console.error("Không có phim nào được tải!");
            }
        })
        .catch(error => console.error("Lỗi tải file CSV:", error));
}

// Chuyển đổi dữ liệu từ CSV
function parseCSV(data) {
    const rows = data.split("\n").slice(1);
    return rows.map(row => {
        const columns = row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);
        if (columns.length < 12) {
            console.warn("Dòng không hợp lệ:", row);
            return null;
        }

        return {
            poster: columns[0].replace(/"/g, '').trim(),
            name: columns[1].replace(/"/g, '').trim(),
            genre: columns[5]?.replace(/"/g, '').trim() || "Unknown",
            year: columns[8] || "N/A",
            director: columns[7] || "N/A",
            runtime: columns[4]?.replace(/"/g, '').trim() + " min" || "N/A",
            overview: columns[3] || "Không có mô tả.",
            imdbRating: parseFloat(columns[9]) || 0,
            rottenRating: parseFloat(columns[10]) || 0,
            tmdbRating: parseFloat(columns[11]) || 0,
            actors: columns[6]?.replace(/"/g, '').trim() || "N/A"
        };
    }).filter(Boolean);
}

// Xác định thể loại chính
function getMainGenre(genreString) {
    const genreMapping = {
        "Hành động & Phiêu lưu": ["Action", "Adventure"],
        "Khoa học viễn tưởng": ["Science Fiction"],
        "Tội phạm & Hành động": ["Crime", "Thriller"],
        "Kinh dị & Giật gân": ["Horror", "Mystery"],
        "Hoạt hình & Gia đình": ["Animation", "Family"],
        "Chính kịch & Lịch sử": ["Drama", "History", "Biography", "War"],
        "Hài & Lãng mạn": ["Comedy", "Romance"],
        "Khác": ["Western", "Fantasy", "Music", "TV Movie"]
    };

    const genres = genreString.split(',').map(g => g.trim());

    for (const key in genreMapping) {
        if (genreMapping[key].some(g => genres.includes(g))) {
            return key;
        }
    }

    return "Khác";
}

// Hiển thị danh sách thể loại
function displayGenres() {
    const genreContainer = document.getElementById("genre-sections");
    if (!genreContainer) {
        console.error("Không tìm thấy phần tử #genre-sections");
        return;
    }

    const genreMap = new Map(); // Nhóm phim theo thể loại chính

    movies.forEach(movie => {
        if (!genreMap.has(movie.genre)) {
            genreMap.set(movie.genre, []);
        }
        genreMap.get(movie.genre).push(movie);
    });

    genreContainer.innerHTML = ""; // Xóa nội dung cũ

    genreMap.forEach((movieList, genre) => {
        const genreSection = document.createElement("section");
        genreSection.className = "genre-section";
        
        const genreTitle = document.createElement("h2");
        genreTitle.innerText = genre;

        // Tạo container chứa nút cuộn & danh sách phim
        const movieListContainer = document.createElement("div");
        movieListContainer.classList.add("movie-list-container");

        // Nút cuộn trái
        const leftButton = document.createElement("button");
        leftButton.classList.add("scroll-button", "left");
        leftButton.innerHTML = "&#10094;"; // Mũi tên trái

        // Danh sách phim
        const movieListDiv = document.createElement("div");
        movieListDiv.classList.add("movie-list");

        movieList.forEach((movie, index) => {
            const movieItem = document.createElement("div");
            movieItem.classList.add("movie-card");
            movieItem.setAttribute("data-index", index); // Gán index để click

            movieItem.innerHTML = `
                <img src="${movie.poster}" alt="${movie.name}">
                <p>${movie.name}</p>
            `;
            movieListDiv.appendChild(movieItem);
        });

        // Nút cuộn phải
        const rightButton = document.createElement("button");
        rightButton.classList.add("scroll-button", "right");
        rightButton.innerHTML = "&#10095;"; // Mũi tên phải

        // Thêm vào container
        movieListContainer.appendChild(leftButton);
        movieListContainer.appendChild(movieListDiv);
        movieListContainer.appendChild(rightButton);

        genreSection.appendChild(genreTitle);
        genreSection.appendChild(movieListContainer);
        genreContainer.appendChild(genreSection);
    });

    addClickEventToPosters();
    addScrollButtons();
}

// Hiển thị popup phim khi click vào poster
function addClickEventToPosters() {
    document.querySelectorAll(".movie-card").forEach(card => {
        card.addEventListener("click", function () {
            const genre = this.closest(".genre-section").querySelector("h2").innerText;
            const index = this.getAttribute("data-index");
            const movieList = movies.filter(m => m.genre === genre);

            if (index === null || isNaN(index)) {
                console.error("data-index không hợp lệ:", index);
                return;
            }

            const movie = movieList[parseInt(index)];

            if (!movie) {
                console.error("Không tìm thấy phim với index:", index);
                return;
            }

            console.log("Mở modal với phim:", movie);
            
            document.getElementById("modalPoster").src = movie.poster;
            document.getElementById("modalTitle").textContent = movie.name;
            document.getElementById("modalGenre").textContent = movie.genre;
            document.getElementById("modalOverview").textContent =  movie.overview;
            document.getElementById("modalRuntime").textContent =  movie.runtime;
            document.getElementById("modalDirector").textContent =  movie.director;
            document.getElementById("modalYear").textContent =  movie.year;
            document.getElementById("modalImdbRating").textContent =  movie.imdbRating;
            document.getElementById("modalRottenRating").textContent =  movie.rottenRating;
            
            document.getElementById("movieModal").style.display = "flex";
        });
    });
}

// Chức năng cuộn ngang
function addScrollButtons() {
    document.querySelectorAll(".movie-list-container").forEach(container => {
        const movieList = container.querySelector(".movie-list");
        const leftButton = container.querySelector(".scroll-button.left");
        const rightButton = container.querySelector(".scroll-button.right");

        leftButton.addEventListener("click", () => {
            movieList.scrollBy({ left: -200, behavior: "smooth" });
        });

        rightButton.addEventListener("click", () => {
            movieList.scrollBy({ left: 200, behavior: "smooth" });
        });
    });
}



///// Dùng để chuyển qua trailer 
async function getMovieId(movieTitle) {
    try {
        const response = await fetch(`${BASE_URL}search/movie?api_key=${API_KEY}&query=${encodeURIComponent(movieTitle)}`);
        const data = await response.json();

        if (data.results.length > 0) {
            return data.results[0].id; // Lấy ID của phim đầu tiên trong kết quả
        } else {
            console.warn("Không tìm thấy phim:", movieTitle);
            return null;
        }
    } catch (error) {
        console.error("Lỗi khi tìm movieId:", error);
        return null;
    }
}

async function fetchMovieTrailer(movieTitle) {
    const movieId = await getMovieId(movieTitle);  // Tìm ID phim trước

    if (!movieId) {
        alert("Không tìm thấy phim trên TMDB.");
        return;
    }

    try {
        const response = await fetch(`${BASE_URL}movie/${movieId}/videos?api_key=${API_KEY}`);
        const data = await response.json();

        const trailer = data.results.find(video => video.type === "Trailer" && video.site === "YouTube");

        if (trailer) {
            window.open(`https://www.youtube.com/watch?v=${trailer.key}`, "_blank");
        } else {
            alert("Không tìm thấy trailer.");
        }
    } catch (error) {
        console.error("Lỗi khi tải trailer:", error);
    }
}


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("trailer-btn").addEventListener("click", function () {
        const movieTitle = document.getElementById("modalTitle").textContent;
        if (movieTitle) {
            console.log("Tìm trailer cho:", movieTitle);
            fetchMovieTrailer(movieTitle);
        } else {
            alert("Không tìm thấy tên phim.");
        }
    });
});
