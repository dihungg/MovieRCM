from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Cấu hình CORS
    CORS(app, resources={
        r"/movie/*": {
            "origins": ["http://127.0.0.1:5502", "http://localhost:5502"],
            "methods": ["GET"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Import các blueprint
    from app.routes.movie import movie_bp
    from app.routes.recommend import recommend_bp
    
    # Đăng ký blueprint
    app.register_blueprint(movie_bp)
    app.register_blueprint(recommend_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)