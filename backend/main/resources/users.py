from flask import request, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Pedidomodel
from main import db
from sqlalchemy import desc, func
from main.models.usuarios import Usuarios
from flask_jwt_extended import jwt_required
from main.auth.decorators import role_required

USUARIOS = {}

class Users(Resource):
    @jwt_required()
    @role_required(['Administrador', 'Encargado'])
    def get(self):
        page = 1
        per_page = 10
        usuarios = db.session.query(Usuariomodel)
        if request.args.get('page'):
            page = int(request.args.get('page'))
        if request.args.get('per_page'):
            per_page = int(request.args.get('per_page'))


        if request.args.get('Pedidos'):
            usuarios = usuarios.outerjoin(Usuariomodel.usuario_pedido).group_by(Usuariomodel.id_usuario).having(func.count(Pedidomodel.id_pedido) >= int(request.args.get('Pedidos')))

        #Filtro por apellido
        if request.args.get('apellido'):
            usuarios = usuarios.filter(Usuariomodel.apellido.like("%"+request.args.get('apellido')+"%"))

        #Filtro por rol
        if request.args.get('rol'):
            usuarios = usuarios.filter(Usuariomodel.rol.like("%"+request.args.get('rol')+"%"))

        #Ordeno por apellido
        if request.args.get('sortby_apellido'):
            usuarios = usuarios.order_by(desc(Usuariomodel.apellido))
            

        usuarios = usuarios.paginate(page=page, per_page=per_page, error_out=False)
        return jsonify ({'usuarios': [usuario.to_json() for usuario in usuarios],
                        'total': usuarios.total,
                        'pages': usuarios.pages,
                        'page': usuarios.page})
    
    def post(self):
        pedidos_ids = request.get_json().get('pedidos')
        usuario = Usuariomodel.from_json(request.get_json())
        data = request.get_json()
        usuario = Usuarios.from_json(data)
        usuario.plain_password = data.get("password")  


        if pedidos_ids:
            pedidos = Pedidomodel.query.filter(Pedidomodel.id_pedido.in_(pedidos_ids)).all()
            usuario.usuario_pedido.extend(pedidos)

        db.session.add(usuario)
        db.session.commit()
        return usuario.to_json(), 201