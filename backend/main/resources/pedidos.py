from flask import request
from flask_restful import Resource
from main.models import Pedidomodel
from main.models.pedido_producto import Pedido_Producto
from main.models.pedidos import Pedidos as PedidosModel
from main import db
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from main.auth.decorators import role_required

class PedidosResource(Resource):
    @jwt_required()
    def get(self):
        """Obtener pedidos según el rol del usuario"""
        # get_jwt_identity() devuelve solo el email (string)
        email = get_jwt_identity()
        
        # get_jwt() devuelve los claims adicionales (diccionario)
        claims = get_jwt()
        rol = claims.get("rol")

        print("🔥 PETICIÓN GET /pedidos")
        print(f"➡️ Usuario: {email} | Rol: {rol}")

        try:
            # Si es cliente, filtra solo sus pedidos
            if rol == "Cliente":
                pedidos = PedidosModel.query.filter_by(id_usuario=email).order_by(PedidosModel.id_pedido.desc()).all()
            else:
                # Admin o Empleado ven todos
                pedidos = PedidosModel.query.order_by(PedidosModel.id_pedido.desc()).all()

            print(f"📦 Pedidos encontrados: {len(pedidos)}")
            
            # Filtrar pedidos que puedan tener datos corruptos
            pedidos_validos = []
            for pedido in pedidos:
                try:
                    pedidos_validos.append(pedido.to_json())
                except Exception as e:
                    print(f"⚠️ Pedido {pedido.id_pedido} tiene datos corruptos: {e}")
            
            return pedidos_validos, 200
            
        except Exception as e:
            print(f"❌ Error al obtener pedidos: {e}")
            return {"error": "Error al obtener pedidos. Puede haber datos corruptos en la base de datos.", "detalle": str(e)}, 500



    @jwt_required()
    def post(self):
        """Crear un nuevo pedido"""
        # get_jwt_identity() devuelve el email
        email = get_jwt_identity()
        
        # get_jwt() devuelve los claims adicionales
        claims = get_jwt()
        rol = claims.get("rol")

        data = request.get_json()
        print("📦 Datos recibidos:", data)

        try:
            # Crear el pedido SIN el campo fecha
            nuevo_pedido = PedidosModel(
                id_usuario=email,  # se asigna automáticamente según el token
                total=data.get('total', 0),
                estado=data.get('estado', 'Recibido'),
                metodo_pago=data.get('metodo_pago', 'Efectivo')
            )

            db.session.add(nuevo_pedido)
            db.session.flush()  # para obtener el id_pedido

            # Guardar los productos asociados
            for item in data.get('items', []):
                pedido_producto = Pedido_Producto(
                    id_pedido=nuevo_pedido.id_pedido,
                    id_producto=item.get('id_producto'),
                    cantidad=item.get('cantidad', 1),
                    linea_pedido_producto=item.get('id_producto')  # o cualquier lógica que necesites
                )
                db.session.add(pedido_producto)

            db.session.commit()
            print("✅ Pedido creado correctamente")
            return {"mensaje": "Pedido creado exitosamente", "pedido": nuevo_pedido.to_json()}, 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al crear pedido: {e}")
            return {"error": str(e)}, 500