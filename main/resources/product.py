from flask import request, jsonify
from flask_restful import Resource
from main.models import Productomodel, Usuariomodel
from main import db

PRODUCTS = {}

class Product(Resource):
    def get(self, product_id):
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        return {'producto': producto.to_json()}, 200

    def put(self, product_id):
        data = request.get_json()
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_id:
            return {'error': 'Falta el ID del usuario autenticado'}, 400
        auth_user = db.session.get(Usuariomodel, user_id)
        if not auth_user or auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar productos'}, 403
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        producto.nombre = data.get('nombre', producto.nombre)
        producto.precio = data.get('precio', producto.precio)
        producto.stock = data.get('stock', producto.stock)
        producto.descripcion = data.get('descripcion', producto.descripcion)
        db.session.commit()
        return {'mensaje': 'Producto actualizado correctamente', 'producto': producto.to_json()}, 200

    def delete(self, product_id):
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        if not auth_user or auth_user.rol != 'Administrador':
            return {'error': 'No tiene permisos para eliminar productos'}, 403
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        db.session.delete(producto)
        db.session.commit()
        return {'mensaje': 'Producto eliminado correctamente'}, 200