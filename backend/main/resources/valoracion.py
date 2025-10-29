from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Valoracionesmodel
from main import db
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError

class Valoracion(Resource):
    @jwt_required()
    def get(self, id_usuario, id_pedido):
        """Obtener una valoración específica"""
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        return {'valoracion': valoracion.to_json()}, 200

    @jwt_required()
    def delete(self, id_usuario, id_pedido):
        """Eliminar una valoración (solo admin)"""
        email = get_jwt_identity()
        claims = get_jwt()
        rol = claims.get('rol')
        
        # Solo administradores pueden eliminar valoraciones
        if rol != 'Administrador':
            return {'error': 'No tiene permisos para eliminar valoraciones'}, 403
        
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        
        db.session.delete(valoracion)
        db.session.commit()
        
        print(f"🗑️ Valoración eliminada: Usuario {id_usuario}, Pedido {id_pedido}")
        return {'mensaje': 'Valoración eliminada correctamente'}, 200
    
    @jwt_required()
    def post(self, id_usuario, id_pedido):
        """Crear una valoración (alternativa a POST en /valoraciones)"""
        data = request.get_json() or {}
        email = get_jwt_identity()
        claims = get_jwt()
        rol = claims.get('rol')
        
        # Solo clientes pueden crear valoraciones
        if rol != 'Cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        
        # Verificar que el usuario está valorando su propio pedido
        if email != id_usuario:
            return {'error': 'Solo puedes valorar tus propios pedidos'}, 403
        
        try:
            nueva = Valoracionesmodel(
                id_usuario=id_usuario,
                id_pedido=id_pedido,
                mensaje=data.get('mensaje', ''),
                puntaje=str(data.get('puntaje'))  # Convertir a string
            )
            db.session.add(nueva)
            db.session.commit()
            
            print(f"✅ Valoración creada: {id_usuario} valoró pedido #{id_pedido} con {data.get('puntaje')} estrellas")
            return {'mensaje': 'Valoración enviada correctamente', 'valoracion': nueva.to_json()}, 201
            
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Ya has valorado este pedido'}, 400
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            return {'error': 'Error al crear la valoración', 'detalle': str(e)}, 500