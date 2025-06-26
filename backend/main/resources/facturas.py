from flask import request, jsonify
from flask_restful import Resource
from main.models import Facturamodel
from main import db
from datetime import datetime
from flask_jwt_extended import jwt_required
from main.auth.decorators import role_required

FACTURAS = {}

class Facturas(Resource):
    @jwt_required()
    @role_required(['Administrador', 'Encargado'])
    def get(self):
        facturas = db.session.query(Facturamodel).all()
        return jsonify([factura.to_json() for factura in facturas])

    @jwt_required()
    @role_required(['Administrador', 'Encargado'])
    def post(self):
        factura = Facturamodel.from_json(request.get_json())
        data = request.get_json()
        try:
            data['fecha'] = datetime.fromisoformat(data['fecha'])
        except Exception as e:
            return {'error': 'Formato de fecha inválido. Usá YYYY-MM-DDTHH:MM:SS'}, 400

        factura = Facturamodel.from_json(data)
        db.session.add(factura)
        db.session.commit()

        return {'mensaje': 'Factura creada correctamente', 'factura': factura.to_json()}, 201
    