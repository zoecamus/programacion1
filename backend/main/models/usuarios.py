from .. import db

class Usuarios(db.Model):
    __tablename__ = 'Usuarios'
    id_usuario = db.Column(db.String(60), primary_key=True, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    rol = db.Column(db.Enum('Administrador', 'Cliente', 'Encargado'), nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(8), nullable=False)
    usuario_pedido = db.relationship('Pedidos', back_populates = 'pedido_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_factura = db.relationship('Facturas', back_populates = 'factura_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_valoracion = db.relationship('Valoraciones', back_populates = 'valoracion_usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_notificacion = db.relationship('Notificaciones',back_populates = 'notificacion_usuario', cascade = "all, delete-orphan")#1 a N relacion
    def to_json(self):
        user_json = {'id_usuario': str(self.id_usuario), 'nombre': str(self.nombre), 'apellido': str(self.apellido), 'rol': (self.rol), 'telefono':str(self.telefono), 'password': str(self.password)}
        return user_json
    @staticmethod
    def from_json(usuario_json):
        id_usuario = usuario_json.get('id_usuario')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        rol = usuario_json.get('rol')
        telefono = usuario_json.get('telefono')
        password = usuario_json.get('password')
        return Usuarios(id_usuario=id_usuario, nombre=nombre, apellido=apellido, rol=rol, telefono=telefono, password=password)