import json
from flask import Flask, request, jsonify
from flask_cors import CORS

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer, util

# model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# embeddings
pc = Pinecone(api_key='683338d7-6863-4d59-9ba5-6f4d422bab9d')
index = pc.Index("relatoria-emebeddings")

# flash app
app = Flask(__name__)
CORS(app)


@app.route('/search')
def hello_world():
    query = request.args['query']
    query_vector = model.encode(query).tolist()
    response = index.query(vector=query_vector, top_k = 3, include_metadata=True)
    return jsonify(list(map(
        lambda item: item._data_store,
        response['matches'],
    )))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)