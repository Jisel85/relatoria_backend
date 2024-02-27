import json
from flask import Flask, request, jsonify
from flask_cors import CORS

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, util
from finetunned_model import chatbot

# model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# embeddings
pc = Pinecone(api_key='683338d7-6863-4d59-9ba5-6f4d422bab9d')
index = pc.Index("relatoria-emebeddings")

# flash app
app = Flask(__name__)
CORS(app)


@app.route('/search')
def search_route():
    query = request.args['query']
    query_vector = model.encode(query).tolist()
    response = index.query(vector=query_vector, top_k = 3, include_metadata=True)
    return jsonify(list(map(
        lambda item: item._data_store,
        response['matches'],
    )))

@app.route('/chatbot')
def chatbot_route():
    query = request.args['query']
    return jsonify(dict(
        response=chatbot(query)
    ))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
