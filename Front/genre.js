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
    const rows = data.split("\n").slice(1); // Bỏ dòng tiêu đề
    return rows.map(row => {
        const columns = row.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/); // Xử lý dấu phẩy trong dấu ngoặc kép
        if (columns.length < 8) return null; // Bỏ qua dòng lỗi

        return {
            poster: columns[0].replace(/"/g, '').trim(),
            name: columns[1].replace(/"/g, '').trim(),
            genre: getMainGenre(columns[4] ? columns[4].replace(/"/g, '').trim() : "Unknown"),
            year: columns[10] || "N/A",
            director: columns[7] || "N/A",
            runtime: columns[6] || "N/A",
            overview: columns[5] || "Không có mô tả.",
            imdbRating: parseFloat(columns[11]) || 0,
            rottenRating: parseFloat(columns[13]) || 0,
            metacriticRating: parseFloat(columns[14]) || 0
        };
    }).filter(movie => movie !== null); // Xóa phần tử null
}

// Xác định thể loại chính
function getMainGenre(genreString) {
    const genreMapping = {
        "Hành động & Phiêu lưu": ["Action", "Adventure", "Thriller"],
        "Khoa học viễn tưởng": ["Sci-Fi"],
        "Tội phạm & Hành động": ["Crime"],
        "Kinh dị & Giật gân": ["Horror", "Thriller"],
        "Hoạt hình & Gia đình": ["Animation", "Family"],
        "Chính kịch & Lịch sử": ["Drama", "History", "Biography"],
        "Hài & Lãng mạn": ["Comedy", "Romance"]
    };

    for (const key in genreMapping) {
        if (genreMapping[key].some(g => genreString.includes(g))) {
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
