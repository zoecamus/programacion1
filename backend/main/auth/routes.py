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
        # ❌ NO mostrar la contraseña en logs
        print(f"Email recibido: {data.get('email')}")
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        usuario = db.session.query(Usuarios).filter(
            db.func.lower(Usuarios.id_usuario) == email.lower()
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # Verificar contraseña
        from werkzeug.security import check_password_hash
        if not check_password_hash(usuario.password, password):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        # ✅ Crear token con claims adicionales (rol, email, nombre)
        additional_claims = {
            "rol": usuario.rol,
            "email": usuario.id_usuario,
            "nombre": usuario.nombre,
            "estado": usuario.estado
        }
        
        access_token = create_access_token(
            identity=usuario.id_usuario,
            additional_claims=additional_claims
        )
        
        # ✅ SOLO devolver token y email (mínima info)
        response_data = {
            'access_token': access_token,
            'email': usuario.id_usuario
        }
        
        print("✅ Login exitoso!")
        print(f"Token generado para: {usuario.id_usuario}")
        print(f"Rol: {usuario.rol} | Estado: {usuario.estado}")
        print("=" * 50)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ EXCEPCIÓN EN LOGIN: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error interno del servidor'}), 500


# Método de registro
@auth.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    print("=" * 50)
    print("PETICIÓN DE REGISTRO RECIBIDA")
    
    try:
        data = request.get_json()
        # ❌ NO mostrar la contraseña en logs
        print(f"Email a registrar: {data.get('email')}")
        
        # Crear usuario desde JSON
        usuario = Usuarios.from_json(data)
        usuario.plain_password = data.get("password")
        usuario.estado = 'Pendiente'
        
        print(f"Intentando registrar: {usuario.id_usuario}")
        print(f"Rol: {usuario.rol}, Estado: {usuario.estado}")
        
        # Verificar si ya existe
        exists = db.session.query(Usuarios).filter(
            Usuarios.id_usuario == usuario.id_usuario
        ).scalar() is not None
        
        if exists:
            print(f"❌ Usuario {usuario.id_usuario} ya existe")
            return jsonify({'error': 'El email ya está registrado'}), 409

        # Guardar en la base de datos
        db.session.add(usuario)
        db.session.commit()
        
        print(f"✅ Usuario {usuario.id_usuario} registrado exitosamente")
        print(f"Estado asignado: {usuario.estado}")
        print("=" * 50)
        
        return jsonify(usuario.to_json()), 201
        
    except Exception as error:
        print(f"❌ ERROR al registrar: {str(error)}")
        import traceback
        traceback.print_exc()
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


# ← AGREGAR ENDPOINT PARA OBTENER INFO DEL TOKEN
@auth.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Obtiene la información del usuario actual desde el token JWT
    """
    from flask_jwt_extended import get_jwt
    
    claims = get_jwt()
    user_id = get_jwt_identity()
    
    return jsonify({
        'email': user_id,
        'rol': claims.get('rol'),
        'nombre': claims.get('nombre'),
        'estado': claims.get('estado')
    }), 200


# ← ENDPOINT PARA VERIFICAR ESTADO (espera-confirmacion)
@auth.route('/user/<string:id_usuario>', methods=['GET'])
@jwt_required()
def obtener_usuario(id_usuario):
    """
    Obtiene información de un usuario por su ID
    Usado por espera-confirmacion para verificar el estado
    """
    try:
        usuario = db.session.query(Usuarios).filter(
            Usuarios.id_usuario == id_usuario
        ).first()
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'id': usuario.id_usuario,
            'nombre': usuario.nombre,
            'rol': usuario.rol,
            'estado': usuario.estado
        }), 200
        
    except Exception as e:
        print(f"Error al obtener usuario: {str(e)}")
        return jsonify({'error': 'Error al obtener usuario'}), 500