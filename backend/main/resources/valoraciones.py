from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Valoracionesmodel
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from main.auth.decorators import role_required
from main import db

class Valoraciones(Resource):
    
    @jwt_required()
    def get(self):
        """Obtener todas las valoraciones"""
        valoraciones = db.session.query(Valoracionesmodel).all()
        return jsonify([valoracion.to_json() for valoracion in valoraciones])
    
    @jwt_required()
    @role_required(['Cliente'])
    def post(self):
        """Crear una nueva valoración"""
        data = request.get_json()
        email = get_jwt_identity()  # Email del usuario autenticado
        
        print(f"📝 Nueva valoración de: {email}")
        print(f"Datos: {data}")
        
        # Verificar que el usuario existe
        usuario = db.session.query(Usuariomodel).filter_by(id_usuario=email).first()
        if not usuario or usuario.rol != 'Cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        
        # Verificar si ya existe una valoración para este pedido
        valoracion_existente = db.session.query(Valoracionesmodel).filter_by(
            id_usuario=email,
            id_pedido=data.get('id_pedido')
        ).first()
        
        if valoracion_existente:
            print(f"⚠️ El usuario ya valoró el pedido #{data.get('id_pedido')}")
            return {'error': 'Ya has valorado este pedido'}, 400
        
        try:
            # Crear la valoración
            valoracion = Valoracionesmodel(
                id_usuario=email,
                id_pedido=data.get('id_pedido'),
                mensaje=data.get('mensaje', ''),
                puntaje=str(data.get('puntaje'))  # Convertir a string para el ENUM
            )
            
            db.session.add(valoracion)
            db.session.commit()
            
            print(f"✅ Valoración creada: Pedido #{data.get('id_pedido')} - {data.get('puntaje')} estrellas")
            return {'mensaje': 'Valoración enviada correctamente', 'valoracion': valoracion.to_json()}, 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear valoración: {e}")
            
            if 'UNIQUE constraint failed' in str(e) or 'Duplicate entry' in str(e):
                return {'error': 'Ya has valorado este pedido'}, 400
            
            return {'error': 'Error al crear la valoración', 'detalle': str(e)}, 500