from .. import db

class Productos(db.Model):
    __tablename__ = 'Productos'
    id_producto = db.Column(db.Integer, primary_key=True, nullable = False)
    nombre = db.Column(db.String(30), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('Categorias.id_categoria'))
    stock = db.Column(db.Integer, nullable=False)
    producto_categoria = db.relationship('Categorias',back_populates='categoria_producto',uselist=False, single_parent=True) #
    producto_pedido_producto = db.relationship('Pedido_Producto',back_populates='pedido_producto_producto', cascade = "all, delete-orphan")
    producto_factura_producto = db.relationship('Factura_Producto',back_populates='factura_producto_producto', cascade = "all, delete-orphan")
    def to_json(self):
        producto_json = {
        'id_producto': int(self.id_producto),
        'nombre': str(self.nombre),
        'id_categoria': int(self.id_categoria) if self.id_categoria is not None else None,
        'precio': float(self.precio) if self.precio not in [None, ''] else 0.0,
        'stock': int(self.stock) if self.stock is not None else 0,
        'descripcion': str(self.descripcion) if self.descripcion else ""}
        return producto_json
    @staticmethod
    def from_json(producto_json):
        id_producto = producto_json.get('id_producto')
        nombre = producto_json.get('nombre')
        precio = producto_json.get('precio')
        stock  = producto_json.get('stock')
        descripcion = producto_json.get('descripcion')
        id_categoria = producto_json.get('id_categoria')
        return Productos(id_producto=id_producto, nombre=nombre, precio=precio, stock=stock, descripcion=descripcion, id_categoria=id_categoria)
    