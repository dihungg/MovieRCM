import requests
import csv
import time

API_KEY = '738f8682fc5143163b145d03a2016b0b'
BASE_URL = 'https://api.themoviedb.org/3'

def get_top_rated_movies(pages=25):
    movies = []
    for page in range(1, pages + 1):
        url = f'{BASE_URL}/movie/top_rated?language=en-US&page={page}&api_key={API_KEY}'
        response = requests.get(url)
        if response.status_code == 200:
            movies += response.json().get('results', [])
        else:
            print(f'Error fetching page {page}: {response.status_code}')
        time.sleep(0.25)
    return movies

def get_movie_details(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}?language=en-US&api_key={API_KEY}'
    return requests.get(url).json()

def get_movie_credits(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}'
    return requests.get(url).json()

def get_movie_certification(movie_id):
    url = f'{BASE_URL}/movie/{movie_id}/release_dates?api_key={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        for country in results:
            if country.get("iso_3166_1") == "US":
                for release in country.get("release_dates", []):
                    cert = release.get("certification")
                    if cert:
                        return cert
    return ''

def save_to_csv(movies_data, filename='top_500_movies.csv'):
    fields = [
        'Poster_Link', 'Title', 'Overview', 'Certificate',
        'Runtime (min)', 'Genre', 'Actors', 'Director', 'Year', 'tmdbRating'
    ]
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for movie in movies_data:
            writer.writerow(movie)

def main():
    top_movies = get_top_rated_movies(pages=25)
    result = []

    for movie in top_movies[:500]:
        movie_id = movie['id']
        details = get_movie_details(movie_id)
        credits = get_movie_credits(movie_id)
        cert = get_movie_certification(movie_id)

        poster_path = details.get('poster_path', '')
        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}' if poster_path else ''

        actors = [cast['name'] for cast in credits.get('cast', [])[:5]]
        genres = [genre['name'] for genre in details.get('genres', [])]

        directors = [crew['name'] for crew in credits.get('crew', []) if crew['job'] == 'Director']

        movie_data = {
            'Poster_Link': poster_url,
            'Title': details.get('title', ''),
            'Overview': details.get('overview', ''),
            'Certificate': cert,
            'Runtime (min)': details.get('runtime', 0),
            'Genre': ', '.join(genres),
            'Actors': ', '.join(actors),
            'Director': ', '.join(directors),
            'Year': details.get('release_date', '')[:4],
            'tmdbRating': details.get('vote_average', 0)
        }

        result.append(movie_data)
        time.sleep(0.25)

    save_to_csv(result)
    print("✅ Saved top 500 movies to 'top_500_movies.csv'.")

if __name__ == '__main__':
    main()
