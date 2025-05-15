from .. import db

from datetime import datetime
class Notificaciones(db.Model):
    __tablename__ = 'Notificaciones'
    id_notificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)  # única PK
    id_pedido = db.Column(db.Integer, db.ForeignKey('Pedidos.id_pedido'), nullable=False)
    id_usuario = db.Column(db.String(60), db.ForeignKey('Usuarios.id_usuario'), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    mensaje = db.Column(db.String(100), nullable=False)
    notificacion_usuario = db.relationship('Usuarios',back_populates='usuario_notificacion', uselist=False, single_parent=True) 
    notificacion_pedido = db.relationship('Pedidos',back_populates='pedido_notificacion', single_parent=True) 
    def to_json(self):
        notificacion_json = {'id_notificacion': self.id_notificacion, 'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'fecha': str(self.fecha), 'mensaje': str(self.mensaje)}
        return notificacion_json
    @staticmethod
    def from_json(notificacion_json):
        id_notificacion = notificacion_json.get('id_notificacion')
        id_pedido = notificacion_json.get('id_pedido')
        id_usuario = notificacion_json.get('id_usuario')
        fecha_str = notificacion_json.get('fecha')
        mensaje = notificacion_json.get('mensaje')
        fecha = datetime.fromisoformat(fecha_str)
        return Notificaciones(id_notificacion=id_notificacion, id_pedido=id_pedido, id_usuario=id_usuario, fecha=fecha, mensaje=mensaje)
    