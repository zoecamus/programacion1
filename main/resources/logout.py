from flask import session, jsonify
from flask_restful import Resource
from main import db

USUARIOS = {}

class LogOut(Resource):
    def put(self):
        session.pop('usuario', None)
        return {'message': 'Sesion cerrada correctamente'}, 200