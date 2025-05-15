from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Valoracionesmodel
from main import db

VALORACION = {}

class Valoraciones(Resource):
    def get(self):
        valoraciones = db.session.query(Valoracionesmodel).all()
        return jsonify([valoracion.to_json() for valoracion in valoraciones])
    
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario or usuario.rol != 'Cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        valoracion = Valoracionesmodel.from_json(data)
        db.session.add(valoracion)
        db.session.commit()
        return {'mensaje': 'Valoración enviada correctamente', 'valoracion': valoracion.to_json()}, 201