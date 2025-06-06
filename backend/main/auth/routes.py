from flask import request, jsonify, Blueprint
from .. import db
from main.models.usuarios import Usuarios
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
@jwt_required()
@role_required(['Administrador'])
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
