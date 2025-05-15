from .. import db

class Valoraciones(db.Model):
    __tablename__ = 'Valoraciones'
    id_usuario = db.Column(db.String(60), db.ForeignKey('Usuarios.id_usuario'), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('Pedidos.id_pedido'), primary_key=True)
    mensaje = db.Column(db.String(100), nullable=True)
    puntaje = db.Column(db.Enum('1', '2', '3', '4', '5'), nullable=False)
    valoracion_usuario = db.relationship('Usuarios', back_populates='usuario_valoracion',uselist=False, single_parent=True)
    #valoracion_pedido a confirmed
    def to_json(self):
        valoracion_json = {'id_usuario': str(self.id_usuario), 'id_pedido': int(self.id_pedido), 'mensaje': str(self.mensaje), 'puntaje': (self.puntaje)}
        return valoracion_json
    @staticmethod
    def from_json(valoracion_json):
        id_usuario = valoracion_json.get('id_usuario') or valoracion_json.get('user_id')  # acepta ambos
        id_pedido = valoracion_json.get('id_pedido')
        mensaje = valoracion_json.get('mensaje')
        puntaje = valoracion_json.get('puntaje')
        return Valoraciones(id_usuario=id_usuario,id_pedido=id_pedido,mensaje=mensaje,puntaje=puntaje)
