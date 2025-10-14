from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel
from main import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.auth.decorators import role_required

class User(Resource):

    @jwt_required()
    def get(self, id_usuario):
        user_id = get_jwt_identity()
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        if auth_user.id_usuario != id_usuario and auth_user.rol not in ['Administrador', 'Encargado']:
            return {'error': 'No tiene permisos para ver este usuario'}, 403

        target_user = db.session.get(Usuariomodel, id_usuario)
        if not target_user:
            return {'error': 'Usuario no encontrado'}, 404

        return target_user.to_json(), 200

    @jwt_required()
    @role_required(['Administrador', 'Encargado'])
    def put(self, id_usuario):
        data = request.get_json()
        user_id = get_jwt_identity()
        
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        # Solo admin puede editar otros usuarios, encargado puede cambiar estados
        if auth_user.id_usuario != id_usuario and auth_user.rol not in ['Administrador', 'Encargado']:
            return {'error': 'No tiene permisos para editar este usuario'}, 403

        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario a editar no encontrado'}, 404

        # Encargado solo puede cambiar el estado
        if auth_user.rol == 'Encargado':
            if 'estado' in data:
                usuario.estado = data['estado']
        else:
            # Administrador puede cambiar todo
            usuario.nombre = data.get('nombre', usuario.nombre)
            usuario.apellido = data.get('apellido', usuario.apellido)
            usuario.rol = data.get('rol', usuario.rol)
            usuario.telefono = data.get('telefono', usuario.telefono)
            usuario.estado = data.get('estado', usuario.estado)
            
            if 'password' in data:
                usuario.plain_password = data['password']

        try:
            db.session.commit()
            return {'mensaje': 'Usuario actualizado correctamente', 'usuario': usuario.to_json()}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @jwt_required()
    @role_required(['Administrador'])
    def delete(self, id_usuario):
        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        
        try:
            db.session.delete(usuario)
            db.session.commit()
            return {'mensaje': 'Usuario eliminado correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500