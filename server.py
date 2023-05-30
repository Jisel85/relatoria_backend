from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/mensaje")
def mensaje():
    return  'hola ucentral'

@app.route("/resultados")
def resultados():
    return [
        {
            'title': 'titulo 1 desde el backend',
            'description': 'descripcion 1 desde el backend',
        },
        {
            'title': 'titulo 2 desde el backend',
            'description': 'descripcion 2 desde el backend',
        },
        {
            'title': 'titulo 3 desde el backend',
            'description': 'descripcion 3 desde el backend',
        },
    ]


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

if __name__ == "__main__":
    app.run()