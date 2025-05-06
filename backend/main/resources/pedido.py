from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Pedidomodel
from main import db

PEDIDO = {}

class Pedido(Resource):
    def get(self, pedido_id):
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        return {'pedido': pedido.to_json()}, 200

    def put(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario.rol == 'Cliente' and pedido.id_usuario != usuario.id_usuario:
            return {'error': 'No tiene permisos para modificar este pedido'}, 403
        pedido.total = data.get('total', pedido.total)
        pedido.estado = data.get('estado', pedido.estado)
        pedido.metodo_pago = data.get('metodo_pago', pedido.metodo_pago)
        db.session.commit()
        return {'mensaje': 'Pedido actualizado', 'pedido': pedido.to_json()}, 200


    def delete(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario.rol == 'Cliente' and pedido.id_usuario != usuario.id_usuario:
            return {'error': 'No tiene permisos para eliminar este pedido'}, 403
        db.session.delete(pedido)
        db.session.commit()
        return {'mensaje': 'Pedido eliminado'}, 200