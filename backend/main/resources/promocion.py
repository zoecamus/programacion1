from flask_restful import Resource
from flask import request
from .. import db
from main.models.promociones import Promociones as PromocionModel
from main.models.usuarios import Usuarios
from flask_jwt_extended import verify_jwt_in_request, get_jwt

class Promocion(Resource):
    """Recurso para una promoción individual"""
    
    def get(self, id_promocion):
        """GET /promocion/<id> - Obtener una promoción específica"""
        promocion = db.session.get(PromocionModel, id_promocion)
        if not promocion:
            return {'error': 'Promoción no encontrada'}, 404
        return promocion.to_json(), 200

    def put(self, id_promocion):
        """PUT /promocion/<id> - Actualizar una promoción (Encargado/Admin)"""
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_email = claims.get('sub')
            
            auth_user = db.session.query(Usuarios).filter_by(id_usuario=user_email).first()
            
            if not auth_user or auth_user.rol not in ['Encargado', 'Administrador']:
                return {'error': 'Sin permisos'}, 403
            
            promocion = db.session.get(PromocionModel, id_promocion)
            if not promocion:
                return {'error': 'Promoción no encontrada'}, 404
            
            data = request.get_json()
            
            # Campos que tanto Encargado como Admin pueden editar
            if 'titulo' in data:
                promocion.titulo = data['titulo']
            if 'descripcion' in data:
                promocion.descripcion = data['descripcion']
            if 'descuento' in data:
                promocion.descuento = data['descuento']
            if 'tipo' in data:
                promocion.tipo = data['tipo']
            if 'codigo' in data:
                promocion.codigo = data['codigo']
            if 'fechaInicio' in data:
                from datetime import datetime
                promocion.fecha_inicio = datetime.strptime(data['fechaInicio'], '%Y-%m-%d').date()
            if 'fechaFin' in data:
                from datetime import datetime
                promocion.fecha_fin = datetime.strptime(data['fechaFin'], '%Y-%m-%d').date()
            if 'productos' in data:
                productos_list = data['productos']
                promocion.productos = ','.join(productos_list) if isinstance(productos_list, list) else productos_list
            
            # SOLO Admin puede cambiar el estado activa/inactiva
            if 'activa' in data:
                if auth_user.rol != 'Administrador':
                    return {'error': 'Solo el administrador puede activar/desactivar promociones'}, 403
                promocion.activa = data['activa']
            
            db.session.commit()
            print(f"✅ Promoción actualizada por {auth_user.rol}: {promocion.titulo}")
            return {'mensaje': 'Promoción actualizada', 'promocion': promocion.to_json()}, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al actualizar: {e}")
            return {'error': str(e)}, 500

    def delete(self, id_promocion):
        """DELETE /promocion/<id> - Eliminar una promoción (solo Encargado/Admin)"""
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_email = claims.get('sub')
            
            auth_user = db.session.query(Usuarios).filter_by(id_usuario=user_email).first()
            
            if not auth_user or auth_user.rol not in ['Encargado', 'Administrador']:
                return {'error': 'Sin permisos'}, 403
            
            promocion = db.session.get(PromocionModel, id_promocion)
            if not promocion:
                return {'error': 'Promoción no encontrada'}, 404
            
            db.session.delete(promocion)
            db.session.commit()
            
            return {'mensaje': 'Promoción eliminada'}, 200
            
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500