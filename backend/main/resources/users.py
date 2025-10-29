from flask_restful import Resource
from flask import request, jsonify
from .. import db
from main.models import Usuariomodel
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request

class Users(Resource):
    def get(self):
        """Obtener todos los usuarios - Solo Admin y Encargado"""
        print("=" * 50)
        print("PETICIÓN GET /users")
        
        try:
            # Verificar JWT manualmente
            verify_jwt_in_request()
            claims = get_jwt()
            
            print(f"Claims del token: {claims}")
            
            user_email = claims.get('sub')  # 'sub' es el subject (identity)
            print(f"Email del usuario: {user_email}")
            
            auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_email).first()
            
            if not auth_user:
                print("Usuario no encontrado")
                return {'error': 'Usuario no encontrado'}, 404
            
            print(f"Rol del usuario: {auth_user.rol}")
            
            # Solo Admin y Encargado pueden ver todos los usuarios
            if auth_user.rol not in ['Administrador', 'Encargado']:
                print("Usuario sin permisos")
                return {'error': 'No tiene permisos para ver usuarios'}, 403
            
            usuarios = db.session.query(Usuariomodel).all()
            usuarios_json = [usuario.to_json() for usuario in usuarios]
            
            print(f"Usuarios encontrados: {len(usuarios_json)}")
            print("=" * 50)
            
            return {'usuarios': usuarios_json, 'total': len(usuarios_json)}, 200
            
        except Exception as e:
            print(f"EXCEPCIÓN: {str(e)}")
            import traceback
            traceback.print_exc()
            print("=" * 50)
            return {'error': str(e)}, 500

    def post(self):
        """Crear un nuevo usuario - Solo Admin"""
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_email = claims.get('sub')
            
            auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_email).first()
            
            if not auth_user or auth_user.rol != 'Administrador':
                return {'error': 'No tiene permisos para crear usuarios'}, 403
            
            usuario = Usuariomodel.from_json(request.get_json())
            
            exists = db.session.query(Usuariomodel).filter(
                Usuariomodel.email == usuario.email
            ).scalar() is not None
            
            if exists:
                return {'error': 'El email ya está registrado'}, 409
            
            db.session.add(usuario)
            db.session.commit()
            return usuario.to_json(), 201
            
        except Exception as error:
            db.session.rollback()
            return {'error': str(error)}, 409