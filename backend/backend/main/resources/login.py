from flask import request, session, jsonify
from flask_restful import Resource
from main import db

USUARIOS = {}

class LogIn(Resource):
    def post(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        usuario = USUARIOS.get(username)
        if usuario and usuario.get('password') == password:
            session['usuario'] = username
            return {'message': f'Sesion iniciada como {username}'}, 200
        return {'error': 'Usuario o contraseña incorrectos'}, 401

    def get(self):
        if 'usuario' in session:
            return {'message': f'Sesion iniciada como {session["usuario"]}'}, 200
        return {'error': 'No hay usuario logueado'}, 401