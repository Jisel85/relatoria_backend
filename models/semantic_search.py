from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
pc = Pinecone(api_key='683338d7-6863-4d59-9ba5-6f4d422bab9d')
index = pc.Index("relatoria-emebeddings")

def search(json):
    query_vector = model.encode(json['text']).tolist()
    filter = []
    if json.get('tipo'):
        filter.append({
            'Tipo': {'$eq': json['tipo']}
        })
    if json.get('anio'):
        filter.append({
            'anio': {'$eq': int(json['anio'])}
        })
    if json.get('fecha_inicio'):
        filter.append({
            'fecha_number': {'$gte': int(json['fecha_inicio'].replace('-', ''))}
        })
    if json.get('fecha_fin'):
        filter.append({
            'fecha_number': {'$lte': int(json['fecha_fin'].replace('-', ''))}
        })
    if len(filter) == 0:
        filter = None
    else:
        filter = {'$and': filter}
    print('filtros: ', filter)

    return index.query(vector=query_vector, top_k = json['top_k'], include_metadata=True, filter=filter)
