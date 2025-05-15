from flask import request, jsonify
from flask_restful import Resource
from main.models import Categoriamodel
from main import db

CATEGORIAS = {}

class Categorias(Resource):
    def get(self):
        categorias = db.session.query(Categoriamodel).all()
        return jsonify([categoria.to_json() for categoria in categorias])

    def post(self):
        categoria = Categoriamodel.from_json(request.get_json())
        db.session.add(categoria)
        db.session.commit()
        return {'mensaje': 'Categoría creada correctamente'}, 201