from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route("/resultados")
def resultados():
    connection_str = os.getenv('CREDENCIALES_BD')
    client = MongoClient(connection_str)
    db = client['proyecto']
    coleccion = db['sentencias']

    pipeline = [
        {
            '$group': {
                '_id': '$AnoPublicacion',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    resultados = coleccion.aggregate(pipeline)
    result_array = []
    for resultado in resultados:
        result_array.append({
            'title': 'Año: ' + str(resultado['_id']),
            'description': 'Total Providencias: ' + str(resultado['count'])
        })

    return (result_array)


@app.route("/search", methods=['POST'])
def search():
    # me conecto a la base de datos
    connection_str = os.getenv('CREDENCIALES_BD')
    client = MongoClient(connection_str)
    db = client["proyecto"]
    collection = db["sentencias"]

    # recibo los datos enviados vía POST desde el frontend
    text = request.json['text']
    tipo = request.json['tipo']
    anio = request.json['anio']
    fecha_inicio = request.json['fecha_inicio']
    fecha_fin = request.json['fecha_fin']

    # construyo la lista de condiciones dinámicamente
    conditions = []
    if text:
        conditions.append({'$or': [
            {'Texto': {'$regex': text, '$options': 'i'}},
            {'Providencia': {'$regex': text, '$options': 'i'}}
        ]})
    if tipo:
        conditions.append({'Tipo': {'$regex': tipo, '$options': 'i'}})
    if anio:
        conditions.append({'AnoPublicacion': {'$regex': anio, '$options': 'i'}})
    if fecha_inicio:
        conditions.append({'FechaPublicacion': {'$gte': fecha_inicio}})
    if fecha_fin:
        conditions.append({'FechaPublicacion': {'$lte': fecha_fin}})

    # hago la consulta a la base de datos mongo enviando los datos que recibí del frontend
    data = collection.find({'$and': conditions})

    resultado = []
    for item in data:
        resultado.append({
            'title': item['Providencia'],
            'description': item['Texto'][:400],
        })

    # mapeo los datos a una lista como lo requiere el frontend
    return jsonify(resultado)

@app.route("/count", methods=['POST'])
def scount():
    # me conecto a la base de datos
    connection_str = os.getenv('CREDENCIALES_BD')
    client = MongoClient(connection_str)
    db = client["proyecto"]
    collection = db["sentencias"]

    # recibo los datos enviados vía POST desde el frontend
    anio = request.json['anio']

    pipeline = [
        {
            '$match': {'AnoPublicacion': anio}
        },
        {
            '$group': {
                '_id': '$Tipo',
                'count': {'$sum': 1}
            }
        }
    ]

    resultados = collection.aggregate(pipeline)
    data = []
    for resultado in resultados:
        print(resultado)
        data.append({
            'tipo_providencia': resultado['_id'],
            'count': resultado['count']
        })
    return data

if __name__ == "__main__":
    app.run()