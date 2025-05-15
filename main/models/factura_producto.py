from .. import db

class Factura_Producto(db.Model):
    __tablename__ = 'Facturas_Productos'
    id_factura = db.Column(db.Integer, db.ForeignKey('Facturas.id_factura'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Productos.id_producto'), primary_key=True)
    linea_factura_producto = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=True)
    factura_producto_producto = db.relationship('Productos', uselist=False, back_populates='producto_factura_producto', single_parent=True)
    factura_producto_factura = db.relationship('Facturas', uselist=False, back_populates='factura_factura_producto', single_parent=True)
    def to_json(self):
        factura_producto_json = {'id_factura': int(self.id_factura), 'id_producto': int(self.id_producto), 'linea-factura-producto': int(self.linea_factura_producto), 'cantidad': int(self.cantidad)  }
        return factura_producto_json
    @staticmethod
    def from_json(factura_producto_json):
        id_factura = factura_producto_json.get('id_factura')
        id_producto = factura_producto_json.get('id_producto')
        linea_factura_producto = factura_producto_json.get('linea-factura-producto')
        cantidad = factura_producto_json.get('cantidad')
        return Factura_Producto(id_factura=id_factura, id_producto=id_producto, linea_factura_producto=linea_factura_producto, cantidad=cantidad)
   