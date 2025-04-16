from flask import request, session, jsonify
from flask_restful import Resource
from main.models import Usuariosmodel
from main import db


USUARIOS = {}
PRODUCTS = {}
PEDIDOS = {}
VALORACIONES = {}
CATEGORIAS = {}
FACTURAS = {}
FACTURAS_PRODUCTOS = {}
PEDIDOS_PRODUCTOS = {}

class Users(Resource):
    def get(self):
        usuarios = db.session.query(Usuariosmodel).all()
        return jsonify ([usuario.to_json() for usuario in usuarios])

    def post(self):
        usuario = Usuariosmodel.from_json(request.get_json())
        db.session.add(usuario)
        db.session.commit()
        return 'OK', 201

class User(Resource):
    def get(self, id):
        user_header = (request.headers.get('user_id') or 
                       request.headers.get('User-Id') or 
                       request.headers.get('X-User-Id'))
        if not user_header:
            return {"error": "Falta el ID del usuario autenticado"}, 400
        try:
            auth_user_id = int(user_header)
        except ValueError:
            return {"error": "ID inválido"}, 400
        auth_user = USUARIOS.get(auth_user_id)
        if not auth_user:
            return {"error": "Usuario no encontrado"}, 404
        if auth_user.get('rol', '').lower() != 'admin':
            return {"error": "No tiene permisos para ver usuarios"}, 403
        try:
            target_id = int(id)
        except ValueError:
            return {"error": "ID inválido"}, 400
        target_user = USUARIOS.get(target_id)
        if not target_user:
            return {"error": "Usuario no encontrado"}, 404
        return {"usuario": target_user}, 200
       


    def put(self, id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para editar usuarios'}, 400
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        rol = data.get('rol')
        password = data.get('password')
        if not nombre or not apellido or not rol or not password:
            return {'error': 'Faltan datos'}, 400
        USUARIOS[int(id)] = {'nombre': nombre, 'apellido': apellido, 'rol': rol, 'password': password}
        return {'message': 'Usuario actualizado'}, 200

    def delete(self, id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] not in ['admin', 'encargado']:
            return {'error': 'No tiene permisos para eliminar usuarios'}, 400
        if usuario['rol'] == 'admin':
            del USUARIOS[int(id)]
            return {'message': 'Usuario eliminado'}, 200
        else:
            USUARIOS[int(id)]['rol'] = 'encargado'
            return {'message': 'Usuario eliminado'}, 200

class Products(Resource):
    def get(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        return {'productos': list(PRODUCTS.values())}

    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para agregar productos'}, 403
        nuevo_id = max(PRODUCTS.keys(), default=0) + 1
        nombre = data.get('nombre')
        precio = data.get('precio')
        stock = data.get('stock')
        if not nombre or precio is None or stock is None:
            return {'error': 'Faltan datos'}, 400
        PRODUCTS[nuevo_id] = {
            'nombre': nombre,
            'precio': precio,
            'stock': stock
        }
        return {'mensaje': 'Producto agregado', 'producto': PRODUCTS[nuevo_id]}, 201

class Product(Resource):
    def get(self, product_id):
        producto = PRODUCTS.get(int(product_id))
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        return producto

    def put(self, product_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario or usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para editar productos'}, 403
        producto = PRODUCTS.get(int(product_id))
        if not producto:
            return {'error': 'Producto no encontrado'}, 404
        producto.update({k: v for k, v in data.items() if k in ['nombre', 'precio', 'stock']})
        return {'mensaje': 'Producto actualizado', 'producto': producto}

    def delete(self, product_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario or usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para eliminar productos'}, 403
        if int(product_id) not in PRODUCTS:
            return {'error': 'Producto no encontrado'}, 404
        del PRODUCTS[int(product_id)]
        return {'mensaje': 'Producto eliminado'}

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
        if not request.is_json:
            return {'error': 'Se esperaba contenido JSON'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] not in ['admin', 'encargado']:
            return {'error': 'No tiene permisos para ver pedidos'}, 403
        return {'pedidos': PEDIDOS}, 200

    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        producto = data.get('producto')
        cantidad = data.get('cantidad')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if not producto or not cantidad:
            return {'error': 'Faltan datos'}, 400
        pedido = {
            'id': len(PEDIDOS) + 1,
            'producto': producto,
            'cantidad': cantidad,
            'usuario': usuario['nombre']
        }
        PEDIDOS.append(pedido)
        return {'message': 'Pedido creado', 'pedido': pedido}, 201

class Pedido(Resource):
    def get(self, pedido_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        pedido = next((p for p in PEDIDOS if p['id'] == int(pedido_id)), None)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        return {'pedido': pedido}, 200

    def put(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        pedido = next((p for p in PEDIDOS if p['id'] == int(pedido_id)), None)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario['rol'] == 'usuario' and pedido['usuario'] != usuario['nombre']:
            return {'error': 'No tiene permisos para modificar este pedido'}, 403
        if 'producto' in data:
            pedido['producto'] = data['producto']
        if 'cantidad' in data:
            pedido['cantidad'] = data['cantidad']
        return {'message': 'Pedido actualizado', 'pedido': pedido}, 200

    def delete(self, pedido_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        pedido = next((p for p in PEDIDOS if p['id'] == int(pedido_id)), None)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if not pedido:
            return {'error': 'Pedido no encontrado'}, 404
        if usuario['rol'] == 'usuario' and pedido['usuario'] != usuario['nombre']:
            return {'error': 'No tiene permisos para eliminar este pedido'}, 403
        PEDIDOS.remove(pedido)
        return {'message': 'Pedido eliminado'}, 200

class Notificaciones(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        tipo = data.get('type')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] not in ['admin', 'encargado']:
            return {'error': 'No tiene permisos para enviar notificaciones'}, 403
        if tipo == 'notificacion':
            return {'message': 'Notificacion enviada'}, 200
        else:
            return {'error': 'Tipo de notificacion no reconocido'}, 400

class Valoracion(Resource):
    def post(self):
        data = request.get_json()
        user_id = data.get('user_id')
        tipo = data.get('type')
        valor = data.get('valor')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'usuario':
            return {'error': 'No tiene permisos para enviar valoraciones'}, 403
        if tipo == 'valoracion' and valor:
            VALORACIONES.append({'usuario': usuario['nombre'], 'valor': valor})
            return {'message': 'Valoracion enviada'}, 200
        else:
            return {'error': 'Tipo de valoracion no reconocido'}, 400

    def get(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido '}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para ver valoraciones'}, 403
        return {'valoraciones': VALORACIONES}, 200
    
class Categorias(Resource):
    def get(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')        
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para ver categorias'}, 403
        return {'categorias': list(CATEGORIAS.values())}, 200    

    def delete(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para eliminar categorias'}, 403
        CATEGORIAS.clear()
class Categoria(Resource):
    def get(self, categoria_id):
        categoria = CATEGORIAS.get(int(categoria_id))
        if not categoria:
            return {'error': 'Categoria no encontrada'}, 404
        return categoria
    def post(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para agregar categorias'}, 403
        nuevo_id = max(CATEGORIAS.keys(), default=0) + 1
        nombre = data.get('nombre')
        precio = data.get('precio')
        stock = data.get('stock')
        if not nombre or precio is None or stock is None:
            return {'error': 'Faltan datos'}, 400
        CATEGORIAS[nuevo_id] = {
            'nombre': nombre,
            'precio': precio,
            'stock': stock
        }
        return {'mensaje': 'Categoria agregada', 'categoria': CATEGORIAS[nuevo_id]}, 201
    
    def put(self, categoria_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':
            return {'error': 'No tiene permisos para editar categorias'}, 403
        categoria = CATEGORIAS.get(int(categoria_id))
        if not categoria:
            return {'error': 'Categoria no encontrada'}, 404
        categoria.update({k: v for k, v in data.items() if k in ['nombre', 'precio', 'stock']})        
        return {'mensaje': 'Categoria actualizada', 'categoria': categoria}, 200
    def delete(self, categoria_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para eliminar categorias'}, 403
        if int(categoria_id) not in CATEGORIAS:
            return {'error': 'Categoria no encontrada'}, 404
        del CATEGORIAS[int(categoria_id)]
        return {'mensaje': 'Categoria eliminada'}, 200
class Factura(Resource):
    def get(self, id_factura):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')                           
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para ver facturas'}, 403
        factura = FACTURAS.get(int(id_factura))
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
    
        return factura
    def put (self, id_factura):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404  
       ####### 
    def delete(self, factura_id):
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)

        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        factura = FACTURAS.get(factura_id)
        if not factura:
            return {'error': 'Factura no encontrada'}, 404
        if factura.usuario_id != usuario.id:            
            return {'error': 'No tiene permiso para eliminar esta factura'}, 401
        FACTURAS.pop(factura_id)            

class Facturas(Resource):
    def get(self):
        return FACTURAS
    def post(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para crear facturas'}, 403
        nuevo_id = max(FACTURAS.keys(), default=0) + 1
        fecha = data.get('fecha')
        total = data.get('total')   

class Facturas_Productos(Resource):
    def get(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para ver facturas'}, 403
        return FACTURAS_PRODUCTOS
    def post(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para crear facturas'}, 403
        nuevo_id = max(FACTURAS_PRODUCTOS.keys(), default=0) + 1
        id_factura = data.get('id_factura')
        id_producto = data.get('id_producto')
        linea_factura_producto = data.get('linea_factura_producto')
        FACTURAS_PRODUCTOS[nuevo_id] = {
            'id_factura': id_factura,
            'id_producto': id_producto,
            'linea_factura_producto': linea_factura_producto
        }
        return {'mensaje': 'Factura creada', 'factura': FACTURAS_PRODUCTOS[nuevo_id]}, 201
    def put(self, factura_producto_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para editar facturas'}, 403
        factura_producto = FACTURAS_PRODUCTOS.get(int(factura_producto_id))
        if not factura_producto:
            return {'error': 'Factura no encontrada'}, 404
        factura_producto.update({k: v for k, v in data.items() if k in ['id_factura', 'id_producto', 'linea_factura_producto']})
        return {'mensaje': 'Factura actualizada', 'factura': factura_producto}, 200
    def delete(self, factura_producto_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para eliminar facturas'}, 403
        if int(factura_producto_id) not in FACTURAS_PRODUCTOS:
            return {'error': 'Factura no encontrada'}, 404
        del FACTURAS_PRODUCTOS[int(factura_producto_id)]    

class Pedidos_Productos(Resource):
    def get(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para ver pedidos'}, 403
        return PEDIDOS_PRODUCTOS
    def post(self):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para crear pedidos'}, 403
        nuevo_id = max(PEDIDOS_PRODUCTOS.keys(), default=0) + 1
        id_pedido = data.get('id_pedido')
        id_producto = data.get('id_producto')
        linea_pedido_producto = data.get('linea_pedido_producto')
        PEDIDOS_PRODUCTOS[nuevo_id] = {
            'id_pedido': id_pedido,
            'id_producto': id_producto,
            'linea_pedido_producto': linea_pedido_producto
        }
        return {'mensaje': 'Pedido creado', 'pedido': PEDIDOS_PRODUCTOS[nuevo_id]}, 201
    def put(self, pedido_producto_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para editar pedidos'}, 403
        pedido_producto = PEDIDOS_PRODUCTOS.get(int(pedido_producto_id))
        if not pedido_producto:
            return {'error': 'Pedido no encontrado'}, 404   
        pedido_producto.update({k: v for k, v in data.items() if k in ['id_pedido', 'id_producto', 'linea_pedido_producto']})
        return {'mensaje': 'Pedido actualizado', 'pedido': pedido_producto}, 200
    def delete(self, pedido_producto_id):
        if not request.is_json:
            return {'error': 'Se esperaba otro tipo de contenido'}, 400
        data = request.get_json()
        user_id = data.get('user_id')
        usuario = USUARIOS.get(user_id)
        if not usuario:
            return {'error': 'Usuario no encontrado'}, 404
        if usuario['rol'] != 'admin':            
            return {'error': 'No tiene permisos para eliminar pedidos'}, 403
        if int(pedido_producto_id) not in PEDIDOS_PRODUCTOS:
            return {'error': 'Pedido no encontrado'}, 404    
        del PEDIDOS_PRODUCTOS[int(pedido_producto_id)]
        return {'mensaje': 'Pedido eliminado'}, 200