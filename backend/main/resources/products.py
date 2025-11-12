from flask import request, jsonify
from flask_restful import Resource
from main.models import Productomodel, Categoriamodel
from main.models.valoraciones import Valoraciones as ValoracionesModel
from main.models.pedido_producto import Pedido_Producto
from main import db
from sqlalchemy import asc, desc, or_, func
from flask_jwt_extended import jwt_required
from main.auth.decorators import role_required

class Products(Resource):
    def get(self):
        """
        Obtener productos con filtros y paginación
        """
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 12))
        
        print(f"📡 GET /products - page={page}, per_page={per_page}")

        # ✅ QUERY BASE
        query = db.session.query(Productomodel)

        # ✅ FILTRO DE BÚSQUEDA (nombre y descripción)
        busqueda = request.args.get('busqueda', '').strip()
        if busqueda:
            search_pattern = f"%{busqueda}%"
            query = query.filter(
                or_(
                    Productomodel.nombre.ilike(search_pattern),
                    Productomodel.descripcion.ilike(search_pattern)
                )
            )
            print(f"🔍 Búsqueda: '{busqueda}'")

        # ✅ FILTRO POR CATEGORÍA
        id_categoria = request.args.get('id_categoria')
        if id_categoria:
            query = query.filter(Productomodel.id_categoria == int(id_categoria))
            print(f"📂 Categoría: {id_categoria}")

        # ✅ FILTRO POR NOMBRE DE CATEGORÍA
        nombre_categoria = request.args.get('sortby_category')
        if nombre_categoria:
            categoria = db.session.query(Categoriamodel).filter_by(nombre=nombre_categoria).first()
            if categoria:
                query = query.filter(Productomodel.id_categoria == categoria.id_categoria)
            else:
                return jsonify({
                    'productos': [],
                    'pagination': {
                        'total': 0,
                        'page': page,
                        'per_page': per_page,
                        'total_pages': 0,
                        'has_next': False,
                        'has_prev': False
                    }
                })

        # ✅ PRODUCTOS MÁS VENDIDOS (JOIN con pedido_producto)
        if request.args.get('mas_vendidos') == 'true':
            print("🔥 Filtro: Más vendidos")
            
            # Subquery para contar cantidad total pedida de cada producto
            subquery = db.session.query(
                Pedido_Producto.id_producto,
                func.sum(Pedido_Producto.cantidad).label('total_vendido')
            ).group_by(Pedido_Producto.id_producto).subquery()
            
            # LEFT JOIN para incluir productos aunque no tengan pedidos
            query = query.outerjoin(
                subquery,
                Productomodel.id_producto == subquery.c.id_producto
            ).order_by(desc(func.coalesce(subquery.c.total_vendido, 0)))
            
            print(f"✅ Query más vendidos ejecutada")

        # ✅ PRODUCTOS MEJOR VALORADOS (JOIN con valoraciones)
        elif request.args.get('mejor_valorados') == 'true':
            print("⭐ Filtro: Mejor valorados")
            
            # Subquery para calcular promedio de valoraciones por producto
            # Primero obtenemos el id_producto desde pedido_producto
            subquery = db.session.query(
                Pedido_Producto.id_producto,
                func.avg(func.cast(ValoracionesModel.puntaje, db.Integer)).label('promedio_valoracion'),
                func.count(ValoracionesModel.puntaje).label('cantidad_valoraciones')
            ).join(
                ValoracionesModel,
                Pedido_Producto.id_pedido == ValoracionesModel.id_pedido
            ).group_by(Pedido_Producto.id_producto).subquery()
            
            # LEFT JOIN para incluir productos aunque no tengan valoraciones
            query = query.outerjoin(
                subquery,
                Productomodel.id_producto == subquery.c.id_producto
            ).order_by(
                desc(func.coalesce(subquery.c.promedio_valoracion, 0)),
                desc(func.coalesce(subquery.c.cantidad_valoraciones, 0))
            )
            
            print(f"✅ Query mejor valorados ejecutada")

        # ✅ ORDENAMIENTO NORMAL
        else:
            orden = request.args.get('orden', '')
            if orden == 'precio_asc':
                query = query.order_by(asc(Productomodel.precio))
            elif orden == 'precio_desc':
                query = query.order_by(desc(Productomodel.precio))
            elif orden == 'nombre':
                query = query.order_by(asc(Productomodel.nombre))
            elif orden == 'stock':
                query = query.order_by(desc(Productomodel.stock))
            else:
                # Default: ordenar por id (más recientes primero)
                query = query.order_by(desc(Productomodel.id_producto))

        # ✅ CONTAR TOTAL (antes de paginar)
        total = query.count()

        # ✅ PAGINACIÓN
        productos = query.offset((page - 1) * per_page).limit(per_page).all()
        
        # ✅ METADATA DE PAGINACIÓN
        total_pages = (total + per_page - 1) // per_page
        
        print(f"✅ Productos: {len(productos)} de {total} total")
        if len(productos) > 0:
            print(f"   Primer producto: {productos[0].nombre}")
            print(f"   Último producto: {productos[-1].nombre}")

        return jsonify({
            'productos': [producto.to_json() for producto in productos],
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })

    @jwt_required()
    @role_required(['Administrador'])
    def post(self):
        """Crear un nuevo producto (solo Admin)"""
        producto = Productomodel.from_json(request.get_json())
        db.session.add(producto)
        db.session.commit()
        return {'mensaje': 'Producto creado correctamente'}, 201