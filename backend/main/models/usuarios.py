from main import db
from sqlalchemy import Enum

class Usuarios(db.Model):
    __tablename__ = "Usuarios"
    
    id_usuario = db.Column(db.String(120), primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    
    # ENUM de roles
    rol = db.Column(
        Enum('Administrador', 'Cliente', 'Encargado', 'Empleado', name='rol_enum'),
        nullable=False,
        default='Cliente'
    )
    
    # Estado del usuario (para sistema de aprobación)
    estado = db.Column(
        Enum('Pendiente', 'Activo', 'Bloqueado', name='estado_enum'),
        nullable=False,
        default='Pendiente'
    )
    
    password = db.Column(db.String(255), nullable=False)
    
    # Relaciones con otras tablas
    usuario_pedido = db.relationship('Pedidos', back_populates='pedido_usuario')
    usuario_valoracion = db.relationship('Valoraciones', back_populates='valoracion_usuario')
    usuario_notificacion = db.relationship('Notificaciones', back_populates='notificacion_usuario')
    usuario_factura = db.relationship('Facturas', back_populates='factura_usuario')
    
    def to_json(self):
        return {
            'id': self.id_usuario,
            'id_usuario': self.id_usuario,
            'email': self.email,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'telefono': self.telefono,
            'rol': self.rol,
            'estado': self.estado
        }
    
    @staticmethod
    def from_json(user_json):
        email = user_json.get('email') or user_json.get('id_usuario')
        return Usuarios(
            id_usuario=email,
            email=email,
            nombre=user_json.get('nombre'),
            apellido=user_json.get('apellido'),
            telefono=user_json.get('telefono', ''),
            rol=user_json.get('rol', 'Cliente'),
            estado=user_json.get('estado', 'Pendiente'),
            password=user_json.get('password')
        )
    
    @property
    def plain_password(self):
        raise Exception('Password no es legible')
    
    @plain_password.setter
    def plain_password(self, plain_password):
        """Hashea la contraseña antes de guardar"""
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(plain_password)