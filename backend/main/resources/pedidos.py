from flask import request
from flask_restful import Resource
from main.models import Pedidomodel
from main.models.pedido_producto import Pedido_Producto
from main.models.pedidos import Pedidos as PedidosModel
from main import db
from sqlalchemy import func, or_, desc
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from main.auth.decorators import role_required

class PedidosResource(Resource):
    @jwt_required()
    def get(self):
        """
        Obtener pedidos con filtros y paginación
        Query params:
        - page: número de página (default: 1)
        - per_page: pedidos por página (default: 10)
        - busqueda: buscar por ID pedido o cliente
        - estado: filtrar por estado (Recibido, En preparación, etc.)
        - id_usuario: filtrar por usuario (automático para clientes)
        """
        # Obtener identidad del usuario
        email = get_jwt_identity()
        claims = get_jwt()
        rol = claims.get("rol")

        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        print("=" * 50)
        print(f"📡 GET /pedidos - Usuario: {email} | Rol: {rol}")
        print(f"Params: page={page}, per_page={per_page}")

        try:
            # ✅ QUERY BASE
            query = PedidosModel.query

            # ✅ FILTRO POR ROL
            if rol == "Cliente":
                # Clientes solo ven sus pedidos
                query = query.filter_by(id_usuario=email)
                print(f"🔒 Filtro: Solo pedidos de {email}")
            else:
                # Admin/Encargado ven todos
                print("👀 Mostrando TODOS los pedidos")

            # ✅ FILTRO POR ESTADO
            estado_filtro = request.args.get('estado', '').strip()
            if estado_filtro:
                query = query.filter(PedidosModel.estado == estado_filtro)
                print(f"📊 Filtro estado: {estado_filtro}")

            # ✅ FILTRO DE BÚSQUEDA (ID pedido o cliente)
            busqueda = request.args.get('busqueda', '').strip()
            if busqueda:
                # Intentar buscar por ID si es numérico
                if busqueda.isdigit():
                    query = query.filter(PedidosModel.id_pedido == int(busqueda))
                else:
                    # Buscar por email del usuario
                    search_pattern = f"%{busqueda}%"
                    query = query.filter(PedidosModel.id_usuario.ilike(search_pattern))
                print(f"🔍 Búsqueda: '{busqueda}'")

            # ✅ ORDENAMIENTO (más recientes primero)
            query = query.order_by(desc(PedidosModel.id_pedido))

            # ✅ CONTAR TOTAL (antes de paginar)
            total = query.count()

            # ✅ PAGINACIÓN
            pedidos = query.offset((page - 1) * per_page).limit(per_page).all()

            # ✅ CONVERTIR A JSON (filtrando corruptos)
            pedidos_validos = []
            for pedido in pedidos:
                try:
                    pedidos_validos.append(pedido.to_json())
                except Exception as e:
                    print(f"⚠️ Pedido {pedido.id_pedido} corrupto: {e}")

            # ✅ METADATA DE PAGINACIÓN
            total_pages = (total + per_page - 1) // per_page

            print(f"✅ Pedidos: {len(pedidos_validos)} de {total} total")
            print("=" * 50)

            return {
                'pedidos': pedidos_validos,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }, 200

        except Exception as e:
            print(f"❌ Error al obtener pedidos: {e}")
            print("=" * 50)
            return {
                "error": "Error al obtener pedidos", 
                "detalle": str(e)
            }, 500

    @jwt_required()
    def post(self):
        """Crear un nuevo pedido"""
        email = get_jwt_identity()
        claims = get_jwt()
        rol = claims.get("rol")

        data = request.get_json()
        print("📦 Creando pedido:", data)

        try:
            # Crear el pedido
            nuevo_pedido = PedidosModel(
                id_usuario=email,
                total=data.get('total', 0),
                estado=data.get('estado', 'Recibido'),
                metodo_pago=data.get('metodo_pago', 'Efectivo')
            )

            db.session.add(nuevo_pedido)
            db.session.flush()

            # Guardar productos asociados
            for item in data.get('items', []):
                pedido_producto = Pedido_Producto(
                    id_pedido=nuevo_pedido.id_pedido,
                    id_producto=item.get('id_producto'),
                    cantidad=item.get('cantidad', 1),
                    linea_pedido_producto=item.get('id_producto')
                )
                db.session.add(pedido_producto)

            db.session.commit()
            print("✅ Pedido creado correctamente")
            
            return {
                "mensaje": "Pedido creado exitosamente", 
                "pedido": nuevo_pedido.to_json()
            }, 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear pedido: {e}")
            return {"error": str(e)}, 500