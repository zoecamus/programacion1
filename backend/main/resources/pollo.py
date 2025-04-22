from flask import request, session, jsonify
from flask_restful import Resource
from main.models import Usuariomodel, Productomodel, Pedidomodel, Valoracionesmodel, Notificacionesmodel, Categoriamodel, Facturamodel
from main import db
from sqlalchemy.exc import IntegrityError

USUARIOS = {}
FACTURAS = {}
CATEGORIAS = {}
PRODUCTS = {}
PEDIDOS = {}
VALORACIONES = {}
NOTIFICACIONES = {}

class Users(Resource):
    def get(self):
        usuarios = db.session.query(Usuariomodel).all()
        return jsonify ([usuario.to_json() for usuario in usuarios])
    
    def post(self):
        usuario = Usuariomodel.from_json(request.get_json())
        db.session.add(usuario)
        db.session.commit()
      
class User(Resource):
    def get(self, id_usuario):
        user_header = (
            request.headers.get('user_id') or
            request.headers.get('User-Id') or
            request.headers.get('X-User-Id')
        )
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        auth_user = db.session.get(Usuariomodel, user_header)
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        if auth_user.id_usuario != id_usuario and auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para ver este usuario'}, 403

        target_user = db.session.get(Usuariomodel, id_usuario)
        if not target_user:
            return {'error': 'Usuario no encontrado'}, 404

        return {'usuario': target_user.to_json()}, 200

    def put(self, id_usuario):
        data = request.get_json()
        user_header = (
            request.headers.get('user_id') or
            request.headers.get('User-Id') or
            request.headers.get('X-User-Id')
        )
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        auth_user = db.session.get(Usuariomodel, user_header)
        if not auth_user:
            return {'error': 'Usuario autenticado no encontrado'}, 404

        if auth_user.id_usuario != id_usuario and auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar este usuario'}, 403

        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario a editar no encontrado'}, 404

        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.apellido = data.get('apellido', usuario.apellido)
        usuario.rol = data.get('rol', usuario.rol)
        usuario.password = data.get('password', usuario.password)

        db.session.commit()
        return {'mensaje': 'Usuario actualizado correctamente'}, 200

    def delete(self, id_usuario):
        usuario = db.session.get(Usuariomodel, id_usuario)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        db.session.delete(usuario)
        db.session.commit()
        return {'mensaje': 'Usuario eliminado correctamente'}, 200

    
class Products(Resource):
    def get(self):
        productos = db.session.query(Productomodel).all()
        return jsonify([producto.to_json() for producto in productos])

    def post(self):
        producto = Productomodel.from_json(request.get_json())
        db.session.add(producto)
        db.session.commit()
        return {'mensaje': 'Producto creado correctamente'}, 201

class Product(Resource):
    def get(self, product_id):
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        return {'producto': producto.to_json()}, 200

    def put(self, product_id):
        data = request.get_json()
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_id:
            return {'error': 'Falta el ID del usuario autenticado'}, 400
        auth_user = db.session.get(Usuariomodel, user_id)
        if not auth_user or auth_user.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar productos'}, 403
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        producto.nombre = data.get('nombre', producto.nombre)
        producto.precio = data.get('precio', producto.precio)
        producto.stock = data.get('stock', producto.stock)
        producto.descripcion = data.get('descripcion', producto.descripcion)
        db.session.commit()
        return {'mensaje': 'Producto actualizado correctamente', 'producto': producto.to_json()}, 200

    def delete(self, product_id):
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        auth_user = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        if not auth_user or auth_user.rol != 'Administrador':
            return {'error': 'No tiene permisos para eliminar productos'}, 403
        producto = db.session.get(Productomodel, product_id)
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        db.session.delete(producto)
        db.session.commit()
        return {'mensaje': 'Producto eliminado correctamente'}, 200

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

class LogOut(Resource):
    def put(self):
        session.pop('usuario', None)
        return {'message': 'Sesion cerrada correctamente'}, 200

class Pedidos(Resource):
    def get(self):
        pedidos = db.session.query(Pedidomodel).all()
        return jsonify([pedido.to_json() for pedido in pedidos])

    def post(self):
        pedido = Pedidomodel.from_json(request.get_json())
        db.session.add(pedido)
        db.session.commit()
        return {'mensaje': 'Pedido creado correctamente'}, 201

class Pedido(Resource):
    def get(self, pedido_id):
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        return {'pedido': pedido.to_json()}, 200

    def put(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario.rol == 'Cliente' and pedido.id_usuario != usuario.id_usuario:
            return {'error': 'No tiene permisos para modificar este pedido'}, 403
        pedido.total = data.get('total', pedido.total)
        pedido.estado = data.get('estado', pedido.estado)
        pedido.metodo_pago = data.get('metodo_pago', pedido.metodo_pago)
        db.session.commit()
        return {'mensaje': 'Pedido actualizado', 'pedido': pedido.to_json()}, 200


    def delete(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        pedido = db.session.get(Pedidomodel, pedido_id)
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario.rol == 'Cliente' and pedido.id_usuario != usuario.id_usuario:
            return {'error': 'No tiene permisos para eliminar este pedido'}, 403
        db.session.delete(pedido)
        db.session.commit()
        return {'mensaje': 'Pedido eliminado'}, 200


class Valoracion (Resource):
    def get(self, id_usuario, id_pedido):
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        return {'valoracion': valoracion.to_json()}, 200

    
    def delete(self, id_usuario, id_pedido):
        user_header = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400
        usuario = db.session.get(Usuariomodel, user_header)
        if not usuario or usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para eliminar valoraciones'}, 403
        valoracion = db.session.get(Valoracionesmodel, (id_usuario, id_pedido))
        if not valoracion:
            return {'error': 'Valoración no encontrada'}, 404
        db.session.delete(valoracion)
        db.session.commit()
        return {'mensaje': 'Valoracion eliminada correctamente'}, 200
    
    def post(self, id_usuario, id_pedido):
        data = request.get_json() or {}
        user_header = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        if not user_header:
            return {'error': 'Falta el ID del usuario autenticado'}, 400

        usuario = db.session.get(Usuariomodel, user_header)
        if not usuario or usuario.rol.lower() != 'cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        try:
            nueva = Valoracionesmodel(
                id_usuario=id_usuario, id_pedido=id_pedido, mensaje=data.get('mensaje'), puntaje=data['puntaje'])
            db.session.add(nueva)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {'error': 'Ya has valorado este producto/pedido'}, 400
        return {'mensaje': 'Valoración enviada correctamente', 'valoracion': nueva.to_json()}, 201


class Valoraciones(Resource):
    def get(self):
        valoraciones = db.session.query(Valoracionesmodel).all()
        return jsonify([valoracion.to_json() for valoracion in valoraciones])
    
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario or usuario.rol != 'Cliente':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        valoracion = Valoracionesmodel.from_json(data)
        db.session.add(valoracion)
        db.session.commit()
        return {'mensaje': 'Valoración enviada correctamente', 'valoracion': valoracion.to_json()}, 201

class Categorias(Resource):
    def get(self):
        categorias = db.session.query(Categoriamodel).all()
        return jsonify([categoria.to_json() for categoria in categorias])

    def post(self):
        categoria = Categoriamodel.from_json(request.get_json())
        db.session.add(categoria)
        db.session.commit()
        return {'mensaje': 'Categoría creada correctamente'}, 201

class Categoria(Resource):
    def get(self, categoria_id):
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        return {'categoria': categoria.to_json()}, 200

    def put(self, categoria_id):
        data = request.get_json()
        user_id = (request.headers.get('user_id') or request.headers.get('User-Id') or request.headers.get('X-User-Id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario or usuario.rol.lower() != 'Administrador':
            return {'error': 'No tiene permisos para modificar categorías'}, 403
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        categoria.nombre = data.get('nombre', categoria.nombre)
        db.session.commit()
        return {'mensaje': 'Categoría actualizada correctamente', 'categoria': categoria.to_json()}, 200

    def delete(self, categoria_id):
        user_id = request.headers.get('User-Id')
        if not user_id:
            return {'error': 'Falta el ID del usuario en el header'}, 400
        usuario = db.session.query(Usuariomodel).filter_by(id_usuario=user_id).first()
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'Administrador':
            return {'error': 'No tiene permisos para eliminar categorías'}, 403
        categoria = db.session.get(Categoriamodel, categoria_id)
        if not categoria:
            return {'error': 'Categoría no encontrada'}, 404
        db.session.delete(categoria)
        db.session.commit()
        return {'mensaje': 'Categoría eliminada correctamente'}, 200

from datetime import datetime
class Facturas(Resource):
    def get(self):
        facturas = db.session.query(Facturamodel).all()
        return jsonify([factura.to_json() for factura in facturas])

    def post(self):
        factura = Facturamodel.from_json(request.get_json())
        data = request.get_json()
        try:
            data['fecha'] = datetime.fromisoformat(data['fecha'])
        except Exception as e:
            return {'error': 'Formato de fecha inválido. Usá YYYY-MM-DDTHH:MM:SS'}, 400

        factura = Facturamodel.from_json(data)
        db.session.add(factura)
        db.session.commit()

        return {'mensaje': 'Factura creada correctamente', 'factura': factura.to_json()}, 201
    
from datetime import datetime
class Factura(Resource):
    def get(self, factura_id):
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        return {'factura': factura.to_json()}, 200

    def put(self, factura_id): 
        data = request.get_json() or {}
        user_id = (data.get('user_id') or request.headers.get('User-Id') or request.headers.get('user_id') or request.headers.get('user id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permisos para editar facturas'}, 403
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        fecha_str = data.get('fecha')
        if fecha_str:
            try:
                factura.fecha = datetime.fromisoformat(fecha_str)
            except ValueError:
                return {'error': 'Formato de fecha inválido. Debe ser YYYY-MM-DDTHH:MM:SS'}, 400
        factura.total = data.get('total', factura.total)
        db.session.commit()
        return {'mensaje': 'Factura actualizada correctamente', 'factura': factura.to_json()}, 200

    def delete(self, factura_id):
        data = request.get_json() or {}
        user_id = (data.get('user_id') or request.headers.get('User-Id') or request.headers.get('user_id') or request.headers.get('user id'))
        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario.rol.lower() != 'administrador':
            return {'error': 'No tiene permiso para eliminar esta factura'}, 403
        factura = db.session.get(Facturamodel, factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        db.session.delete(factura)
        db.session.commit()
        return {'mensaje': 'Factura eliminada correctamente'}, 200


class Notificacion(Resource):
    def get(self, notificacion_id):
        notificacion = db.session.get(Notificacionesmodel, notificacion_id)
        if not notificacion:
            return {'error': 'Notificación no encontrada'}, 404
        return {'notificacion': notificacion.to_json()}, 200


class Notificaciones(Resource):
    def get(self):
        notificaciones = db.session.query(Notificacionesmodel).all()
        return jsonify([n.to_json() for n in notificaciones])

    def post(self):
        data = request.get_json()
        user_id = data.get('id_usuario')
        pedido_id = data.get('id_pedido')

        usuario = db.session.get(Usuariomodel, user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404

        notificacion = Notificacionesmodel.from_json(data)
        db.session.add(notificacion)
        db.session.commit()
        return {'mensaje': 'Notificación creada correctamente', 'notificacion': notificacion.to_json()}, 201
