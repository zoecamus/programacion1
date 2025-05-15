from .. import db

class Pedido_Producto(db.Model):
    __tablename__ = 'Pedidos_Productos'
    id_pedido = db.Column(db.Integer, db.ForeignKey('Pedidos.id_pedido'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Productos.id_producto'), primary_key=True)
    linea_pedido_producto = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=True)
    pedido_producto_producto = db.relationship('Productos', uselist=False, back_populates='producto_pedido_producto', single_parent=True)
    pedido_producto_pedido = db.relationship('Pedidos', uselist=False, back_populates='pedido_pedido_producto', single_parent=True)
    def to_json(self):
        pedido_producto_json = {'id_pedido': int(self.id_pedido), 'id_producto': int(self.id_producto), 'linea-pedido-producto': int(self.linea_pedido_producto) , 'cantidad': int(self.cantidad)}
        return pedido_producto_json
    @staticmethod
    def from_json(pedido_producto_json):
        id_pedido = pedido_producto_json.get('id_pedido')
        id_producto = pedido_producto_json.get('id_producto')
        linea_pedido_producto = pedido_producto_json.get('linea-pedido-producto')
        cantidad = pedido_producto_json.get('cantidad')
        return Pedido_Producto(id_pedido=id_pedido, id_producto=id_producto, linea_pedido_producto=linea_pedido_producto, cantidad=cantidad)