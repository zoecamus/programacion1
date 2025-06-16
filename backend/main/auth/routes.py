from flask import request, jsonify, Blueprint
from .. import db
from main.models.usuarios import Usuarios
from main.models.pedidos import Pedidos
from main.models.productos import Productos
from main.auth.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from main.mail.functions import sendMail

#Blueprint para acceder a los métodos de autenticación
auth = Blueprint('auth', __name__, url_prefix='/auth')

#Método de logueo
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("Data recibida:", data)

    usuario = db.session.query(Usuarios).filter(Usuarios.email == data.get("email")).first()
    print("Usuario encontrado:", usuario)

    if usuario:
        print("Hash guardado:", usuario.password)
        print("Contraseña enviada:", data.get("password"))
        print("Validación:", usuario.validate_pass(data.get("password")))

    if (usuario is None) or not (usuario.validate_pass(data.get("password"))):
        print("Login fallido")
        return 'Invalid user or password', 401

    access_token = create_access_token(identity=usuario)
    data = {
        'id': str(usuario.id_usuario),
        'email': usuario.email,
        'access_token': access_token
    }    
    return data, 200


#Método de registro
@auth.route('/register', methods=['POST'])
#@jwt_required()
#@role_required(['Administrador'])
def register():
    data = request.get_json()

    # Crear el usuario desde JSON
    usuario = Usuarios.from_json(data)
    usuario.plain_password = data.get("password")

    # Verificá si ya existe
    exists = db.session.query(Usuarios).filter(Usuarios.email == usuario.email).scalar() is not None
    if exists:
        return 'Duplicated mail', 409

    try:
        db.session.add(usuario)
        db.session.commit()
        send = sendMail([usuario.email], "¡Bienvenido/a!", 'register', usuario=usuario)
    except Exception as error:
        db.session.rollback()
        return str(error), 409

    return usuario.to_json(), 201

@auth.route('/comprar', methods=['POST'])
@jwt_required()
def comprar():
    user_id = get_jwt_identity()
    usuario = Usuarios.query.get(user_id)

    if not usuario.puede_comprar():
        return jsonify({'msg': 'No autorizado para comprar'}), 403

    data = request.get_json()
    pedido = Pedidos.from_json({**data, "id_usuario": user_id})

    try:
        db.session.add(pedido)
        db.session.commit()
        return jsonify({'msg': 'Pedido realizado correctamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Error al procesar el pedido', 'error': str(e)}), 500
    
@auth.route('/crear_producto', methods=['POST'])
@jwt_required()
def crear_producto():
    user_id = get_jwt_identity()
    usuario = Usuarios.query.get(user_id)
    print("ROL DEL USUARIO:", usuario.rol)

    if not usuario.puede_cargar_producto():
        return jsonify({'msg': 'No autorizado para crear productos'}), 403

    data = request.get_json()
    producto = Productos.from_json(data)

    try:
        db.session.add(producto)
        db.session.commit()
        return jsonify(producto.to_json()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Error al crear el producto', 'error': str(e)}), 500

@auth.route('/ver_productos', methods=['GET'])
def ver_productos():
    productos = Productos.query.all()
    return jsonify([p.to_json() for p in productos]), 200


