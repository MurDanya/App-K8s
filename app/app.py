from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)

r = redis.Redis(
    host=os.getenv('REDIS_HOST', 'redis-service'),
    port=6379,
    decode_responses=True,
    db=0
)

def initialize_data():
    if not r.exists('anime:id'):
        initial_data = [
            {"title": "Attack on Titan", "genre": "Action", "year": "2013"},
            {"title": "Mushoku Tensei: Jobless Reincarnation", "genre": "Fantasy", "year": "2021"},
            {"title": "Vinland Saga", "genre": "Historical", "year": "2019"},
            {"title": "Hunter x Hunter", "genre": "Adventure", "year": "2011"}
        ]        
        for item in initial_data:
            anime_id = r.incr('anime:id')
            r.hset(f'anime:{anime_id}', mapping=item)

initialize_data()

@app.route('/add', methods=['POST'])
def add_anime():
    data = request.json
    required_fields = ['title', 'genre', 'year']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing one or more required fields: title, genre, year"}), 400

    anime_id = r.incr('anime:id')
    
    anime_data = {
        'title': data['title'],
        'genre': data['genre'],
        'year': data['year']
    }
    
    r.hset(f'anime:{anime_id}', mapping=anime_data)
    return jsonify({"status": "success", "id": anime_id})

@app.route('/list')
def list_anime():
    anime_list = []
    
    for key in r.scan_iter('anime:*'):
        if key == 'anime:id':
            continue
        
        if r.type(key) != 'hash':
            continue

        anime_data = r.hgetall(key)
        anime_list.append({
            'id': key.split(':')[1],
            **anime_data
        })
    
    return jsonify(anime_list)

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
