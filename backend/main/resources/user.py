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
    def put(self, id_usuario):
        """Actualizar datos de un usuario"""
        try:
            user_email = get_jwt_identity()
            auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_email).first()

            if not auth_user:
                return {'error': 'Usuario no autenticado'}, 401

            usuario = db.session.query(Usuariomodel).filter_by(id_usuario=id_usuario).first()
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404

            # Verificar permisos: Cliente solo puede editar su propio perfil
            if auth_user.rol == 'Cliente' and auth_user.id_usuario != id_usuario:
                return {'error': 'No tienes permisos para editar este usuario'}, 403

            data = request.get_json()

            # Cambiar estado (Admin y Encargado)
            if 'estado' in data:
                if auth_user.rol not in ['Administrador', 'Encargado']:
                    return {'error': 'Sin permisos para cambiar estado'}, 403
                usuario.estado = data['estado']

            # Cambiar rol (SOLO Admin)
            if 'rol' in data:
                if auth_user.rol != 'Administrador':
                    return {'error': 'Solo el administrador puede cambiar roles'}, 403
                usuario.rol = data['rol']

            # Otros campos editables por todos
            if 'nombre' in data:
                usuario.nombre = data['nombre']
            if 'apellido' in data:
                usuario.apellido = data['apellido']
            if 'telefono' in data:
                usuario.telefono = data['telefono']

            db.session.commit()
            print(f"✅ Usuario actualizado: {id_usuario}")
            return {'mensaje': 'Usuario actualizado', 'usuario': usuario.to_json()}, 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar: {e}")
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