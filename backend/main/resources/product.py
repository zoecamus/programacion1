from flask import request, jsonify
from flask_restful import Resource
from main.models import Productomodel, Usuariomodel
from main import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.auth.decorators import role_required

class Product(Resource):
    def get(self, product_id):
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        return {'producto': producto.to_json()}, 200

    @jwt_required()
    def put(self, product_id):
        """Actualizar producto - Solo Admin y Encargado"""
        user_id = get_jwt_identity()
        print(f"Usuario intentando editar: {user_id}")
        
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        
        if not auth_user:
            print("Usuario no encontrado")
            return {'error': 'Usuario no encontrado'}, 404
        
        print(f"Rol del usuario: {auth_user.rol}")
        
        # Solo Administrador y Encargado pueden editar productos
        if auth_user.rol not in ['Administrador', 'Encargado']:
            print("Rol sin permisos")
            return {'error': 'No tiene permisos para editar productos'}, 403
        
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        
        data = request.get_json()
        print(f"Datos recibidos: {data}")
        
        # Actualizar campos
        producto.nombre = data.get('nombre', producto.nombre)
        producto.precio = data.get('precio', producto.precio)
        producto.stock = data.get('stock', producto.stock)
        producto.descripcion = data.get('descripcion', producto.descripcion)
        producto.id_categoria = data.get('id_categoria', producto.id_categoria)
        
        try:
            db.session.commit()
            print("Producto actualizado exitosamente")
            return {'mensaje': 'Producto actualizado correctamente', 'producto': producto.to_json()}, 200
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar: {str(e)}")
            return {'error': str(e)}, 500

    @jwt_required()
    @role_required(['Administrador'])
    def delete(self, product_id):
        """Eliminar producto - Solo Admin"""
        user_id = get_jwt_identity()
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        
        if not auth_user or auth_user.rol != 'Administrador':
            return {'error': 'No tiene permisos para eliminar productos'}, 403
        
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        
        try:
            db.session.delete(producto)
            db.session.commit()
            return {'mensaje': 'Producto eliminado correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500