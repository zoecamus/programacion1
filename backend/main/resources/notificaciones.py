from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Notificacionesmodel
from main import db

NOTIFICACION = {}

class Notificaciones(Resource):
    def get(self):
        notificaciones = db.session.query(Notificacionesmodel).all()
        return jsonify([n.to_json() for n in notificaciones])

    def post(self):
        data = request.get_json()
        user_id = data.get('id_usuario')
        pedido_id = data.get('id_pedido')

        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        notificacion = Notificacionesmodel.from_json(data)
        db.session.add(notificacion)
        db.session.commit()
        return {'mensaje': 'Notificación creada correctamente', 'notificacion': notificacion.to_json()}, 201
