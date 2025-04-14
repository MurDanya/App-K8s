from flask import Flask, request, jsonify
import redis
import os

app = Flask(__name__)

r = redis.Redis(host=os.getenv('REDIS_HOST', 'redis-service'), port=6379, decode_responses=True, db=0)

def initialize_data():
    if not r.exists('anime:id'):
        initial_data = [
            {"title": "Attack on Titan", "genre": "Action", "year": "2013"},
            {"title": "Your Lie in April", "genre": "Drama", "year": "2014"}
        ]        
        for item in initial_data:
            anime_id = r.incr('anime:id')
            r.hset(f'anime:{anime_id}', mapping=item)

initialize_data()

@app.route('/add', methods=['POST'])
def add_anime():
    data = request.json
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