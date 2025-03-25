// Hàm thêm sự kiện cuộn cho từng danh sách phim
function addScrollButtons() {
    document.querySelectorAll(".movie-list-container").forEach(container => {
        const list = container.querySelector(".movie-list"); // Lấy danh sách phim cần cuộn
        const leftButton = container.querySelector(".scroll-button.left");
        const rightButton = container.querySelector(".scroll-button.right");

        if (!list || !leftButton || !rightButton) {
            console.error("Không tìm thấy danh sách phim hoặc nút cuộn!");
            return;
        }

        // Hàm kiểm tra để bật/tắt nút khi cuộn
        function updateButtons() {
            leftButton.style.opacity = list.scrollLeft > 0 ? "0.7" : "0";
            rightButton.style.opacity = list.scrollLeft + list.clientWidth < list.scrollWidth ? "0.7" : "0";
        }

        // Cuộn trái
        leftButton.addEventListener("click", function () {
            list.scrollBy({ left: -300, behavior: "smooth" });
        });

        // Cuộn phải
        rightButton.addEventListener("click", function () {
            list.scrollBy({ left: 300, behavior: "smooth" });
        });

        // Cập nhật trạng thái nút khi cuộn bằng chuột
        list.addEventListener("scroll", updateButtons);

        // Kiểm tra ban đầu
        updateButtons();
    });
}

// Gọi hàm khi DOM đã tải xong
document.addEventListener("DOMContentLoaded", addScrollButtons);



// Dành cho thanh tìm kiếm đầu header
// Hiệu ứng dropdown khi nhấn vào icon tìm kiếm
function toggleSearch() {
    let searchContainer = document.querySelector(".search-container");
    searchContainer.classList.toggle("active");
}

// Ẩn ô tìm kiếm khi nhấp ra ngoài
document.addEventListener("click", function (event) {
    let searchContainer = document.querySelector(".search-container");
    let searchBar = document.getElementById("searchBar"); // Có thể xóa nếu không dùng
    // Kiểm tra searchContainer tồn tại trước
    if (searchContainer && !searchContainer.contains(event.target)) {
        searchContainer.classList.remove("active");
    }
});

