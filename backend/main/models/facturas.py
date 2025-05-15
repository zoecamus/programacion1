from .. import db

class Facturas(db.Model):
    __tablename__ = 'Facturas'
    id_factura = db.Column(db.Integer, primary_key=True, nullable=False)
    id_pedido = db.Column(db.Integer, db.ForeignKey('Pedidos.id_pedido'), nullable=False)
    id_usuario = db.Column(db.String(60), db.ForeignKey('Usuarios.id_usuario'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    factura_factura_producto= db.relationship ('Factura_Producto',back_populates='factura_producto_factura', cascade = "all, delete-orphan")
    factura_pedido= db.relationship('Pedidos',back_populates='pedido_factura',uselist=False, cascade = "all, delete-orphan", single_parent=True)
    factura_usuario= db.relationship('Usuarios', back_populates='usuario_factura',uselist=False, single_parent=True)    
    def to_json(self):
        factura_json = {'id_factura': int(self.id_factura), 'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'total': float(self.total), 'fecha': self.fecha.isoformat() if self.fecha else None, 'metodo_pago': str(self.metodo_pago)}
        return factura_json
    @staticmethod
    def from_json(factura_json):
        id_factura = factura_json.get('id_factura')
        id_pedido = factura_json.get('id_pedido')
        id_usuario = factura_json.get('id_usuario')
        total = factura_json.get('total')
        fecha = factura_json.get('fecha')
        metodo_pago = factura_json.get('metodo_pago')
        return Facturas(id_factura=id_factura, id_pedido=id_pedido, id_usuario=id_usuario, total=total, fecha=fecha, metodo_pago=metodo_pago)
 