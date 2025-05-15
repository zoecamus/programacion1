from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Categoriamodel
from main import db

CATEGORIAS = {} 

class Categoria(Resource):
    def get(self, categoria_id):
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        return {'categoria': categoria.to_json()}, 200

    def put(self, categoria_id):
        data = request.get_json()
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario or usuario.rol.lower() != 'Administrador':
            return {'error': 'No tiene permisos para modificar categorías'}, 403
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        categoria.nombre = data.get('nombre', categoria.nombre)
        db.session.commit()
        return {'mensaje': 'Categoría actualizada correctamente', 'categoria': categoria.to_json()}, 200

    def delete(self, categoria_id):
        user_id = request.headers.get('User-Id')
        if not user_id:
            return {'error': 'Falta el ID del usuario en el header'}, 400
        usuario = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'Administrador':
            return {'error': 'No tiene permisos para eliminar categorías'}, 403
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        db.session.delete(categoria)
        db.session.commit()
        return {'mensaje': 'Categoría eliminada correctamente'}, 200