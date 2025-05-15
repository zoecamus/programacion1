from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Valoracionesmodel
from main import db
from sqlalchemy.exc import IntegrityError

VALORACIONES = {}

class Valoracion (Resource):
    def get(self, id_usuario, id_pedido):
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        return {'valoracion': valoracion.to_json()}, 200

    
    def delete(self, id_usuario, id_pedido):
        user_header = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400
        usuario = db.session.get(Usuariomodel, user_header)
        if not usuario or usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para eliminar valoraciones'}, 403
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        db.session.delete(valoracion)
        db.session.commit()
        return {'mensaje': 'Valoracion eliminada correctamente'}, 200
    
    def post(self, id_usuario, id_pedido):
        data = request.get_json() or {}
        user_header = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        usuario = db.session.get(Usuariomodel, user_header)
        if not usuario or usuario.rol.lower() != 'cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        try:
            nueva = Valoracionesmodel(
                id_usuario=id_usuario, id_pedido=id_pedido, mensaje=data.get('mensaje'), puntaje=data['puntaje'])
            db.session.add(nueva)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Ya has valorado este producto/pedido'}, 400
        return {'mensaje': 'Valoración enviada correctamente', 'valoracion': nueva.to_json()}, 201