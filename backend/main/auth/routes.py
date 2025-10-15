from flask import request, jsonify, Blueprint
from .. import db
from main.models.usuarios import Usuarios
from main.models.pedidos import Pedidos
from main.models.productos import Productos
from main.auth.decorators import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from main.mail.functions import sendMail

# Blueprint para acceder a los métodos de autenticación
auth = Blueprint('auth', __name__, url_prefix='/auth')

# Método de logueo
@auth.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("=" * 50)
    print("PETICIÓN DE LOGIN RECIBIDA")
    
    try:
        data = request.get_json()
        print("Data recibida:", data)
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        usuario = db.session.query(Usuarios).filter(
            db.func.lower(Usuarios.email) == email.lower()
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        if not usuario.validate_pass(password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # ← CAMBIO AQUÍ: Pasar solo el ID/email como identity
        access_token = create_access_token(identity=usuario.id_usuario)
        
        response_data = {
            'id': str(usuario.id_usuario),
            'email': usuario.email,
            'nombre': usuario.nombre,
            'rol': usuario.rol,
            'access_token': access_token
        }
        
        print("Login exitoso!")
        print("Token generado para:", usuario.id_usuario)
        print("=" * 50)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"EXCEPCIÓN EN LOGIN: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


# Método de registro
@auth.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    usuario = Usuarios.from_json(data)
    usuario.plain_password = data.get("password")

    exists = db.session.query(Usuarios).filter(Usuarios.email == usuario.email).scalar() is not None
    if exists:
        return jsonify({'error': 'El email ya está registrado'}), 409

    try:
        db.session.add(usuario)
        db.session.commit()
        return jsonify(usuario.to_json()), 201
    except Exception as error:
        db.session.rollback()
        return jsonify({'error': str(error)}), 409


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