import json
from flask import Flask, request, jsonify
from flask_cors import CORS

from models.semantic_search import search
#from models.finetunned_model import chatbot
from models.rag import chatbot

# flash app
app = Flask(__name__)
CORS(app)


@app.route('/search', methods=['POST'])
def search_route():    
    return jsonify(list(map(
        lambda item: item._data_store,
        search(request.json)['matches'],
    )))

@app.route('/chatbot')
def chatbot_route():
    query = request.args['query']
    return jsonify(dict(
        response=chatbot(query)
    ))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
