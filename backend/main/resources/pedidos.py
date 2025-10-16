from flask import request
from flask_restful import Resource
from main.models import Pedidomodel
from main.models.pedido_producto import Pedido_Producto
from main import db
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.auth.decorators import role_required

class Pedidos(Resource):
    @jwt_required()
    def get(self):
        """
        GET /pedidos
        - Si es Admin/Encargado: devuelve TODOS los pedidos (con paginación y filtros)
        - Si es Cliente: devuelve SOLO sus pedidos (filtrado por id_usuario)
        """
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        rol_usuario = claims.get('rol')
        
        page = 1
        per_page = 10
        
        if request.args.get('page'):
            page = int(request.args.get('page'))
        if request.args.get('per_page'):
            per_page = int(request.args.get('per_page'))

        # Iniciar query
        pedidos = db.session.query(Pedidomodel)

        # ✅ Si es CLIENTE, filtrar solo SUS pedidos
        if rol_usuario == 'Cliente':
            id_usuario = request.args.get('id_usuario')
            
            if not id_usuario:
                return {'error': 'Falta el parámetro id_usuario'}, 422
            
            print(f"🔍 Filtrando pedidos del cliente: {id_usuario}")
            pedidos = pedidos.filter(Pedidomodel.id_usuario == id_usuario)
        
        # ✅ Si es ADMIN/ENCARGADO, aplicar filtros opcionales
        else:
            print("🔍 Cargando TODOS los pedidos (Admin/Encargado)")
            
            ### FILTROS OPCIONALES PARA ADMIN ###
            if request.args.get('id_usuario'):
                pedidos = pedidos.filter(Pedidomodel.id_usuario == request.args.get('id_usuario'))
            
            if request.args.get('metodo_pago'):
                pedidos = pedidos.filter(Pedidomodel.metodo_pago == request.args.get('metodo_pago'))

            if request.args.get('fecha'):
                pedidos = pedidos.filter(Pedidomodel.fecha == request.args.get('fecha'))

            if request.args.get('estado'):
                pedidos = pedidos.filter(Pedidomodel.estado == request.args.get('estado'))
            ### FIN FILTROS ###

        # Ordenar por más reciente
        pedidos = pedidos.order_by(Pedidomodel.id_pedido.desc())

        # Paginación
        pedidos_paginados = pedidos.paginate(page=page, per_page=per_page, error_out=False)

        print(f"✅ Devolviendo {len(pedidos_paginados.items)} pedidos")

        # ✅ CORRECCIÓN: Sin jsonify(), Flask-RESTful lo maneja automáticamente
        return {
            'pedidos': [pedido.to_json() for pedido in pedidos_paginados.items],
            'total': pedidos_paginados.total,
            'pages': pedidos_paginados.pages,
            'page': page
        }, 200

    @jwt_required()
    @role_required(['Cliente'])  
    def post(self):
        """
        POST /pedidos
        Crear un nuevo pedido (solo Clientes)
        """
        try:
            data = request.get_json()
            print("📦 Datos recibidos:", data)
            
            # Validar campos requeridos
            if not data.get('id_usuario'):
                return {'error': 'Falta el id_usuario'}, 422
            if not data.get('items') or len(data.get('items')) == 0:
                return {'error': 'El pedido debe tener al menos un item'}, 422
            
            # Crear el pedido
            pedido = Pedidomodel.from_json(data)
            db.session.add(pedido)
            db.session.flush()  # Para obtener el id_pedido
            
            # Crear los items del pedido (Pedido_Producto)
            items = data.get('items', [])
            linea = 1
            for item in items:
                pedido_producto_item = Pedido_Producto(
                    id_pedido=pedido.id_pedido,
                    id_producto=item.get('id_producto'),
                    linea_pedido_producto=linea,
                    cantidad=item.get('cantidad')
                )
                db.session.add(pedido_producto_item)
                linea += 1
            
            db.session.commit()
            print("✅ Pedido creado exitosamente con ID:", pedido.id_pedido)
            
            return pedido.to_json(), 201
            
        except Exception as e:
            db.session.rollback()
            print("❌ Error al crear pedido:", str(e))
            return {'error': f'Error al crear el pedido: {str(e)}'}, 500