from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from main.models import Usuariomodel
from main import db

def role_required(required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            usuario = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
            
            if not usuario:
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            if usuario.rol not in required_roles:
                return jsonify({'error': 'No tiene permisos para esta operación'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


# Callback para agregar claims personalizados al token
def add_claims_to_access_token(identity):
    """
    Esta función se llama cuando se crea un token.
    El 'identity' es lo que pasamos en create_access_token(identity=...)
    """
    # Ahora el identity es solo un string (el id_usuario)
    # Necesitamos buscar el usuario en la BD para obtener sus datos
    usuario = db.session.query(Usuariomodel).filter_by(id_usuario=identity).first()
    
    if usuario:
        return {
            'rol': usuario.rol,
            'id': str(usuario.id_usuario),
            'email': usuario.email,
            'nombre': usuario.nombre
        }
    else:
        return {
            'rol': 'Cliente',
            'id': str(identity),
            'email': str(identity),
            'nombre': 'Desconocido'
        }


# Callback para determinar la identidad desde el token
def user_identity_lookup(usuario):
    """
    Esta función determina qué valor se guardará como 'identity' en el token.
    Si recibe un objeto Usuario, devuelve su id_usuario.
    Si recibe un string, lo devuelve tal cual.
    """
    if hasattr(usuario, 'id_usuario'):
        return usuario.id_usuario
    return usuario