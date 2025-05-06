const API_KEY = '738f8682fc5143163b145d03a2016b0b'; // Thay bằng key bảo mật
const BASE_URL = 'https://api.themoviedb.org/3/';

document.addEventListener("DOMContentLoaded", function () {
    fetchAndProcessCSV();
    setInterval(changePoster, 8000);
    
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
let currentPosterIndex = 0;

function fetchAndProcessCSV() {
    fetch("movie.csv")
        .then(response => response.text())
        .then(data => {
            console.log("Dữ liệu CSV tải về thành công");
            movies = parseCSV(data);
            console.log("Danh sách movies sau khi xử lý:", movies);
            
            if (movies.length > 0) {
                changePoster();
                displayGenres();
                displayTopMoviesByRatings();
                addClickEventToPosters();
            } else {
                console.error("Không có dữ liệu phim để hiển thị!");
            }
        })
        .catch(error => console.error("Lỗi tải file CSV:", error));
}

function parseCSV(data) {
    const rows = data.split("\n").slice(1); // Bỏ dòng tiêu đề
    return rows.map(row => {
        const columns = row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/); // Tách theo dấu phẩy ngoài dấu ngoặc kép

        if (!columns || columns.length < 12) return null; // Đảm bảo có đủ 12 cột

        return {
            poster: columns[0].replace(/"/g, '').trim(),
            name: columns[1].replace(/"/g, '').trim(),
            genre: columns[5] ? columns[5].replace(/"/g, '').trim() : "Unknown",
            year: columns[8] || "N/A",
            director: columns[7] || "N/A",
            runtime: columns[4] ? columns[4].replace(/"/g, '').trim() + " min" : "N/A",
            overview: columns[3] || "Không có mô tả.",
            imdbRating: parseFloat(columns[9]) || 0,
            rottenRating: parseFloat(columns[10]) || 0,
            metacriticRating: parseFloat(columns[11]) || 0
        };
    }).filter(movie => movie !== null);
}


function changePoster() {
    if (movies.length === 0) return;
    const poster = document.getElementById("poster");
    if (!poster) return;

    poster.src = movies[currentPosterIndex].poster;
    console.log("Đổi poster:", movies[currentPosterIndex].poster);
    currentPosterIndex = (currentPosterIndex + 1) % movies.length;
}

function displayGenres() {
    const genreSet = new Set(movies.map(movie => movie.genre).filter(genre => genre));
    const genreList = document.getElementById("genre-list");
    genreList.innerHTML = "";
    genreSet.forEach(genre => {
        const div = document.createElement("div");
        div.className = "genre";
        div.innerText = genre;
        genreList.appendChild(div);
    });
}

function sortMoviesByRating(ratingType, topN = 30) {
    return movies
        .filter(movie => movie[ratingType] > 0)
        .sort((a, b) => b[ratingType] - a[ratingType])
        .slice(0, topN);
}

function displayTopMoviesByRatings() {
    displayTopMovies("top-imdb", sortMoviesByRating("imdbRating"));
    displayTopMovies("top-rotten", sortMoviesByRating("rottenRating"));
    displayTopMovies("top-metacritic", sortMoviesByRating("metacriticRating"));
}

//////////////////////////////////////////////////
////////////2
//////////////////////////////////////////////////
function addClickEventToPosters() {
    document.querySelectorAll(".movie-card").forEach(card => {
        card.addEventListener("click", function () {
            const index = this.getAttribute("data-index");

            if (index === null || isNaN(index)) {
                console.error("data-index không hợp lệ:", index);
                return;
            }

            const movie = movies[parseInt(index)]; // Đảm bảo lấy đúng index trong movies

            if (!movie) {
                console.error("Không tìm thấy phim với index:", index);
                return;
            }

            console.log("Mở modal với phim:", movie);
            
            document.getElementById("modalPoster").src = movie.poster;
            document.getElementById("modalTitle").textContent = movie.name;
            document.getElementById("modalGenre").textContent = movie.genre;
            document.getElementById("modalOverview").textContent =  movie.overview;
            document.getElementById("modalRuntime").textContent =  movie.runtime ;
            document.getElementById("modalDirector").textContent =  movie.director;
            document.getElementById("modalYear").textContent =  movie.year;
            document.getElementById("modalImdbRating").textContent =  movie.imdbRating;
            document.getElementById("modalRottenRating").textContent =  movie.rottenRating ;
            // document.getElementById("modalMetacriticRating").textContent = "Metacritic: " + movie.metacriticRating + "/100  ";
            document.getElementById("movieModal").style.display = "flex";
        });
    });
}



function displayTopMovies(sectionId, movieList) {
    const container = document.getElementById(sectionId);
    container.innerHTML = movieList.map(movie => {
        const index = movies.indexOf(movie); // Lấy index thực trong `movies`
        return `
            <div class="movie-card" data-index="${index}">
                <img src="${movie.poster}" alt="${movie.name}">
                <p>${movie.name}</p>
            </div>
        `;
    }).join('');

    addClickEventToPosters();
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


