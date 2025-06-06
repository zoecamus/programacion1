from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

class Usuarios(db.Model):
    __tablename__ = 'Usuarios'
    id_usuario = db.Column(db.String(60), primary_key=True, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    rol = db.Column(db.Enum('Administrador', 'Cliente', 'Encargado'), nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password = db.Column(db.String(255), nullable=False)
    usuario_pedido = db.relationship('Pedidos', back_populates = 'pedido_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_factura = db.relationship('Facturas', back_populates = 'factura_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_valoracion = db.relationship('Valoraciones', back_populates = 'valoracion_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_notificacion = db.relationship('Notificaciones',back_populates = 'notificacion_usuario', cascade = "all, delete-orphan")#1 a N relacion
    
    #no permite leerla
    @property
    def plain_password(self):
        raise AttributeError('Password cant be read')
    
    #toma un valor en texto plano
    #calcula el hash y lo guarda en el atributo password
    @plain_password.setter
    def plain_password(self, password):
        self.password = generate_password_hash(password)
    #Método que compara una contraseña en texto plano con el hash guardado en la db
    def validate_pass(self,password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return '<Usuario: %r >' % (self.rol)
    #Convertir objeto en JSON
    def to_json(self):
        user_json = {
            'id': self.id_usuario,
            'nombre': str(self.nombre),
            'apellido': str(self.apellido),
            'rol': str(self.rol),
            'telefono': str(self.telefono),
            'email': str(self.email)
        }
        return user_json

    @staticmethod
    def from_json(usuario_json):
        id_usuario = usuario_json.get('id_usuario')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        rol = usuario_json.get('rol')
        telefono = usuario_json.get('telefono')
        email = usuario_json.get('email')
    # No obtengas ni devuelvas el password acá
        return Usuarios(id_usuario=id_usuario, nombre=nombre, apellido=apellido,rol=rol, telefono=telefono, email=email)
