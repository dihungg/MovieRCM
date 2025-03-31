from flask import Flask
from app.routes.recommend import recommend_bp
from app.routes.movie import movie_bp

def create_app():
    app = Flask(__name__)
    
    # Đăng ký route
    app.register_blueprint(recommend_bp)
    app.register_blueprint(movie_bp)

    return app
