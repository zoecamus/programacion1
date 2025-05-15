from .. import db

class Pedidos(db.Model):
    __tablename__ = 'Pedidos'
    id_pedido = db.Column(db.Integer, primary_key=True, nullable=False)
    id_usuario = db.Column(db.String(60), db.ForeignKey('Usuarios.id_usuario'), nullable=False)
    total = db.Column(db.Float, default=0.0)
    estado = db.Column(db.Enum('Pendiente', 'En preparación', 'Listo para retiro', 'Entregado'))
    metodo_pago = db.Column(db.String(50))
    pedido_factura = db.relationship ('Facturas',back_populates='factura_pedido', cascade = "all, delete-orphan")
    pedido_pedido_producto = db.relationship('Pedido_Producto',back_populates='pedido_producto_pedido', cascade = "all, delete-orphan")
    pedido_usuario = db.relationship ('Usuarios', back_populates='usuario_pedido',uselist=False ,single_parent=True)
    pedido_notificacion = db.relationship('Notificaciones',back_populates='notificacion_pedido',uselist=False, single_parent=True)
    def to_json(self):
        pedido_json = {'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'total': float(self.total) if self.total is not None else 0.0 , 'estado': (self.estado), 'metodo_pago': str(self.metodo_pago)}
        return pedido_json
    @staticmethod
    def from_json(pedido_json):
        id_usuario =pedido_json.get('id_usuario')
        total = pedido_json.get('total')
        estado = pedido_json.get('estado')
        metodo_pago = pedido_json.get('metodo_pago')
        return Pedidos(id_usuario=id_usuario, total=total, estado=estado, metodo_pago=metodo_pago)
 