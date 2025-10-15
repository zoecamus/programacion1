from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import Usuariomodel
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.auth.decorators import role_required

class Users(Resource):
    @jwt_required()
    def get(self):
        """Obtener todos los usuarios - Solo Admin y Encargado"""
        try:
            user_id = get_jwt_identity()
            print(f"Usuario solicitando lista de usuarios: {user_id}")
            
            auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
            
            if not auth_user:
                return {'error': 'Usuario no encontrado'}, 404
            
            print(f"Rol del usuario: {auth_user.rol}")
            
            # Solo Admin y Encargado pueden ver todos los usuarios
            if auth_user.rol not in ['Administrador', 'Encargado']:
                return {'error': 'No tiene permisos para ver usuarios'}, 403
            
            # Obtener parámetros de paginación (opcionales)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            usuarios = db.session.query(Usuariomodel).all()
            
            # Convertir a JSON
            usuarios_json = [usuario.to_json() for usuario in usuarios]
            
            return {
                'usuarios': usuarios_json,
                'total': len(usuarios_json)
            }, 200
            
        except Exception as e:
            print(f"Error al obtener usuarios: {str(e)}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}, 500

    @jwt_required()
    @role_required(['Administrador'])
    def post(self):
        """Crear un nuevo usuario - Solo Admin"""
        usuario = Usuariomodel.from_json(request.get_json())
        
        # Verificar si ya existe
        exists = db.session.query(Usuariomodel).filter(
            Usuariomodel.email == usuario.email
        ).scalar() is not None
        
        if exists:
            return {'error': 'El email ya está registrado'}, 409
        
        try:
            db.session.add(usuario)
            db.session.commit()
            return usuario.to_json(), 201
        except Exception as error:
            db.session.rollback()
            return {'error': str(error)}, 409