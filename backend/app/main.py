from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime


app = Flask(__name__)
CORS(app)

# Conexión a MongoDB local
client = MongoClient('mongodb://localhost:27017/')
db = client['sistema_alerta']
coleccion = db['mediciones']

@app.route('/api/mediciones', methods=['POST'])
def recibir_medicion():
    data = request.get_json()
    if not data or 'distancia' not in data:
        return jsonify({'error': 'Falta el campo distancia'}), 400

    # Guardar en MongoDB con timestamp
    medicion = {
        'distancia': data['distancia'],
        'fecha': datetime.utcnow()
    }
    coleccion.insert_one(medicion)

    return jsonify({'mensaje': 'Medición guardada', 'distancia': data['distancia']}), 201

@app.route('/api/mediciones', methods=['GET'])
def obtener_mediciones():
    # Obtener todas las mediciones, ordenadas por fecha descendente
    mediciones = list(coleccion.find().sort('fecha', -1))
    # Convertir ObjectId y fecha a string para JSON
    for m in mediciones:
        m['_id'] = str(m['_id'])
        m['fecha'] = m['fecha'].isoformat() + 'Z'
    return jsonify(mediciones), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
