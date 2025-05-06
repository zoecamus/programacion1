from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel
from main import db

USUARIOS = {}

class Users(Resource):
    def get(self):
        usuarios = db.session.query(Usuariomodel).all()
        return jsonify ([usuario.to_json() for usuario in usuarios])
    
    def post(self):
        usuario = Usuariomodel.from_json(request.get_json())
        db.session.add(usuario)
        db.session.commit()