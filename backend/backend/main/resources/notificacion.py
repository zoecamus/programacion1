from flask import jsonify
from flask_restful import Resource
from main.models import  Notificacionesmodel
from main import db

NOTIFICACION = {}

class Notificacion(Resource):
    def get(self, notificacion_id):
        notificacion = db.session.get(Notificacionesmodel, notificacion_id)
        if not notificacion:
            return {'error': 'Notificación no encontrada'}, 404
        return {'notificacion': notificacion.to_json()}, 200