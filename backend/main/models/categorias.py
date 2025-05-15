from .. import db

class Categorias(db.Model):
    __tablename__ = 'Categorias'
    id_categoria = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    categoria_producto = db.relationship('Productos',back_populates='producto_categoria', cascade = "all, delete-orphan")
    def to_json(self):
        categoria_json = {'id_categoria': int(self.id_categoria) if self.id_categoria is not None else None, 'nombre': str(self.nombre)}
        return categoria_json
    @staticmethod
    def from_json(categoria_json):
        id_categoria = categoria_json.get('id_categoria')
        nombre = categoria_json.get('nombre')
        return Categorias(id_categoria=id_categoria, nombre=nombre)
 