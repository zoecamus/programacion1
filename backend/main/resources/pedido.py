from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Pedidomodel
from main.models.pedidos import Pedidos as PedidosModel
from main import db
from flask_jwt_extended import jwt_required

class Pedido(Resource):
    @jwt_required()
    def get(self, pedido_id):
        """Obtener un pedido específico"""
        pedido = PedidosModel.query.get_or_404(pedido_id)
        return pedido.to_json(), 200

    @jwt_required()
    def put(self, pedido_id):
        """Actualizar el estado de un pedido"""
        data = request.get_json()
        pedido = PedidosModel.query.get_or_404(pedido_id)

        print(f"📝 Actualizando pedido {pedido_id}")
        print(f"Datos recibidos: {data}")

        nuevo_estado = data.get('estado')
        if nuevo_estado:
            # Corrección automática de estados para que coincidan con el ENUM
            estados_correccion = {
                'Listo para retiro': 'Listo para retirar',
                'En preparacion': 'En preparación',
                'Preparación': 'En preparación'
            }
            
            estado_corregido = estados_correccion.get(nuevo_estado, nuevo_estado)
            
            if estado_corregido != nuevo_estado:
                print(f"⚠️ Estado corregido: '{nuevo_estado}' -> '{estado_corregido}'")
            
            pedido.estado = estado_corregido
            print(f"Nuevo estado: {estado_corregido}")

        db.session.commit()
        return {"mensaje": "Pedido actualizado", "pedido": pedido.to_json()}, 200

    @jwt_required()
    def delete(self, pedido_id):
        """Eliminar un pedido"""
        pedido = PedidosModel.query.get_or_404(pedido_id)
        db.session.delete(pedido)
        db.session.commit()
        return {"mensaje": "Pedido eliminado correctamente"}, 200