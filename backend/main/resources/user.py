from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel
from main import db

USUARIOS = {}

class User(Resource):
    def get(self, id_usuario):
        user_header = (
            request.headers.get('user_id') or
            request.headers.get('User-Id') or
            request.headers.get('X-User-Id')
        )
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        auth_user = db.session.get(Usuariomodel, user_header)
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        if auth_user.id_usuario != id_usuario and auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para ver este usuario'}, 403

        target_user = db.session.get(Usuariomodel, id_usuario)
        if not target_user:
            return {'error': 'Usuario no encontrado'}, 404

        return {'usuario': target_user.to_json()}, 200

    def put(self, id_usuario):
        data = request.get_json()
        user_header = (
            request.headers.get('user_id') or
            request.headers.get('User-Id') or
            request.headers.get('X-User-Id')
        )
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        auth_user = db.session.get(Usuariomodel, user_header)
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        if auth_user.id_usuario != id_usuario and auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar este usuario'}, 403

        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario a editar no encontrado'}, 404

        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.rol = data.get('rol', usuario.rol)
        usuario.password = data.get('password', usuario.password)

        db.session.commit()
        return {'mensaje': 'Usuario actualizado correctamente'}, 200

    def delete(self, id_usuario):
        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        db.session.delete(usuario)
        db.session.commit()
        return {'mensaje': 'Usuario eliminado correctamente'}, 200