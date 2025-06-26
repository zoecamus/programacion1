from flask import request, jsonify
from flask_restful import Resource
from main.models import Productomodel, Categoriamodel
from main import db
from sqlalchemy import asc, desc
from flask_jwt_extended import jwt_required
from main.auth.decorators import role_required

class Products(Resource):
    def get(self):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        productos = db.session.query(Productomodel)

        # Ordenar por stock (de menor a mayor)
        if request.args.get('stock'):
            productos = productos.order_by(asc(Productomodel.stock))

        # Ordenar por precio descendente
        if request.args.get('orden_precio') == 'desc':
            productos = productos.order_by(desc(Productomodel.precio))

        # Filtro por ID de categoría
        id_categoria = request.args.get('id_categoria')
        if id_categoria:
            productos = productos.filter(Productomodel.id_categoria == int(id_categoria))

        # Filtro por nombre de categoría
        nombre_categoria = request.args.get('sortby_category')
        if nombre_categoria:
            categoria = db.session.query(Categoriamodel).filter_by(nombre=nombre_categoria).first()
            if categoria:
                productos = productos.filter(Productomodel.id_categoria == categoria.id)
            else:
                return jsonify({
                    'productos': [],
                    'total': 0,
                    'pages': 0,
                    'page': page
                })

        productos = productos.paginate(page=page, per_page=per_page, error_out=False)


        return jsonify({
            'productos': [producto.to_json() for producto in productos],
            'total': productos.total,
            'pages': productos.pages,
            'page': page
        })
    @jwt_required()
    @role_required(['Administrador'])
    def post(self):
        producto = Productomodel.from_json(request.get_json())
        db.session.add(producto)
        db.session.commit()
        return {'mensaje': 'Producto creado correctamente'}, 201