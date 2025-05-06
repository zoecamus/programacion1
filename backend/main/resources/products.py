from flask import request, jsonify
from flask_restful import Resource
from main.models import Productomodel
from main import db

PRODUCTS = {}

class Products(Resource):
    def get(self):
        productos = db.session.query(Productomodel).all()
        return jsonify([producto.to_json() for producto in productos])

    def post(self):
        producto = Productomodel.from_json(request.get_json())
        db.session.add(producto)
        db.session.commit()
        return {'mensaje': 'Producto creado correctamente'}, 201
