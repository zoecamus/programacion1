from flask import request, session, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Facturamodel
from main import db
from datetime import datetime

FACTURAS = {}

class Factura(Resource):
    def get(self, factura_id):
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        return {'factura': factura.to_json()}, 200

    def put(self, factura_id): 
        data = request.get_json() or {}
        user_id = (data.get('user_id') or request.headers.get('User-Id') or request.headers.get('user_id') or request.headers.get('user id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar facturas'}, 403
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        fecha_str = data.get('fecha')
        if fecha_str:
            try:
                factura.fecha = datetime.fromisoformat(fecha_str)
            except ValueError:
                return {'error': 'Formato de fecha inválido. Debe ser YYYY-MM-DDTHH:MM:SS'}, 400
        factura.total = data.get('total', factura.total)
        db.session.commit()
        return {'mensaje': 'Factura actualizada correctamente', 'factura': factura.to_json()}, 200

    def delete(self, factura_id):
        data = request.get_json() or {}
        user_id = (data.get('user_id') or request.headers.get('User-Id') or request.headers.get('user_id') or request.headers.get('user id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permiso para eliminar esta factura'}, 403
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        db.session.delete(factura)
        db.session.commit()
        return {'mensaje': 'Factura eliminada correctamente'}, 200