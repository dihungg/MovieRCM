// movieModal.js
function initializeMovieModal() {
    const modal = document.getElementById("movieModal");
    
    // Close modal khi click vào nút đóng
    modal.addEventListener('click', (e) => {
        if (e.target.classList.contains('close') || e.target === modal) {
            modal.style.display = "none";
        }
    });
}


function handleMovieClicks() {
    document.addEventListener('click', async (e) => {
        const card = e.target.closest('.movie-card');
        if (!card) return;

        console.log("Movie card clicked:", card); // Debug
        
        const movieTitle = card.dataset.movieTitle;
        console.log("Extracted title:", movieTitle); // Debug
        
        const modal = document.getElementById("movieModal");
        
        try {
            modal.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div>Loading movie info...</div>
                </div>`;
            modal.style.display = "flex";
            
            const response = await fetch(`http://localhost:5000/movie/${encodeURIComponent(movieTitle)}`, {
                mode: 'cors'
            });
            
            if (!response.ok) throw new Error(await response.text());
            
            const movie = await response.json();
            console.log("Full movie data:", movie); // Debug
            
            // Render modal content
            modal.innerHTML = `
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <img src="${movie.poster}" class="modal-poster"
                         onerror="this.src='images/fallback-poster.jpg'">
                    <div class="modal-info">
                        <h2 class="movie-title">${movie.title}</h2>
                        <p><span class="label">Genre:</span> 🎭 <span class="highlight">${movie.genre}</span></p>
                        <p><span class="label">Actors:</span> 👨 <span class="highlight">${movie.actors}</span></p>
                        <p><span class="label">Director:</span> 💼 <span class="highlight">${movie.director}</span></p>
                        <p><span class="label">Overview:</span> 🎬 <span class="highlight">${movie.overview}</span></p>
                        <p><span class="label">Duration:</span> ⏳ <span class="highlight">${movie.runtime}</span> minutes</p>
                        <p><span class="label">IMDb Rating:</span> ⭐ <span class="highlight">${movie.ratingIMDB?.toFixed(1)}</span></p>
                        <p><span class="label">Rotten Tomatoes:</span> 🍅 <span class="highlight">${movie.ratingRotten?.toFixed(1)}</span>%</p>
                        ${movie.trailer ? 
                            `<a href="${movie.trailer}" target="_blank" class="trailer-button">
                                ▶ Watch Trailer
                            </a>` : 
                            '<p class="no-trailer">Trailer not available</p>'
                        }
                    </div>
                </div>`;
                
            console.log("Modal content after render:", modal.innerHTML); // Debug
            
        } catch (error) {
            console.error("Error:", error);
            modal.innerHTML = `
                <div class="modal-content error">
                    <span class="close">&times;</span>
                    <p>Error loading movie: ${error.message}</p>
                </div>`;
        }
    });
}




// Khởi tạo khi trang load xong
document.addEventListener('DOMContentLoaded', () => {
    initializeMovieModal();
    handleMovieClicks();
});