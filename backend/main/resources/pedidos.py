from flask import request, jsonify
from flask_restful import Resource
from main.models import Pedidomodel
from main import db

PEDIDOS = {}

class Pedidos(Resource):
    def get(self):
        pedidos = db.session.query(Pedidomodel).all()
        return jsonify([pedido.to_json() for pedido in pedidos])

    def post(self):
        pedido = Pedidomodel.from_json(request.get_json())
        db.session.add(pedido)
        db.session.commit()
        return {'mensaje': 'Pedido creado correctamente'}, 201