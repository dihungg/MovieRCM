from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.top5movie_service import recommend_movies

recommend_bp = Blueprint("recommend", __name__)

@recommend_bp.route("/recommend", methods=["POST"])
@cross_origin()
def recommend():
    data = request.get_json()
    user_input = data.get("query", "").strip()

    if not user_input:
        return jsonify({"error": "Query is required"}), 400

    recommended_movies = recommend_movies(user_input)

    return jsonify({"recommended_movies": recommended_movies})
