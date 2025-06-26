from flask import request, jsonify
from flask_restful import Resource
from main.models import Pedidomodel  
from main import db
from sqlalchemy import func
from flask_jwt_extended import jwt_required  
from main.auth.decorators import role_required

class Pedidos(Resource):
    @jwt_required()  
    @role_required(['Administrador', 'Encargado'])
    def get(self):
        page = 1
        per_page = 10
        pedidos = db.session.query(Pedidomodel)

        if request.args.get('page'):
            page = int(request.args.get('page'))
        if request.args.get('per_page'):
            per_page = int(request.args.get('per_page'))

        ### FILTROS ###
        if request.args.get('metodo_pago'):
            pedidos = pedidos.filter(Pedidomodel.metodo_pago == request.args.get('metodo_pago'))

        if request.args.get('fecha'):
            pedidos = pedidos.filter(Pedidomodel.fecha == request.args.get('fecha'))

        if request.args.get('estado'):
            pedidos = pedidos.filter(Pedidomodel.estado == request.args.get('estado'))
        ### FIN FILTROS ###

        pedidos = pedidos.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'pedidos': [pedido.to_json() for pedido in pedidos.items],
            'total': pedidos.total,
            'pages': pedidos.pages,
            'page': page
        })

    @jwt_required()
    @role_required(['Cliente'])  
    def post(self):
        data = request.get_json()
        pedido = Pedidomodel.from_json(data)
        
        db.session.add(pedido)
        db.session.commit()
        
        return pedido.to_json(), 201
