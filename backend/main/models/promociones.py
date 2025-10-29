from main import db
from datetime import datetime

class Promociones(db.Model):
    __tablename__ = "Promociones"
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(20), nullable=False, default="porcentaje")  # 'porcentaje' | 'monto' | etc.
    descuento = db.Column(db.Float, nullable=False, default=0)
    codigo = db.Column(db.String(50), index=True)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
    productos = db.Column(db.JSON, default=list)  # Se guarda como lista JSON

    
    def to_json(self):
        return {
        'id': self.id,
        'titulo': self.titulo,
        'descripcion': self.descripcion,
        'descuento': self.descuento,
        'tipo': self.tipo,
        'codigo': self.codigo,
        'fechaInicio': self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
        'fechaFin': self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else None,
        'activa': self.activa,
        'productos': self.productos.split(',') if self.productos else []
    }



    @staticmethod
    def from_json(promo_json):
        return Promociones(
            titulo=promo_json.get('titulo'),
            descripcion=promo_json.get('descripcion'),
            descuento=promo_json.get('descuento', 0),
            tipo=promo_json.get('tipo', 'porcentaje'),
            codigo=promo_json.get('codigo'),
            fecha_inicio=datetime.strptime(promo_json.get('fechaInicio'), '%Y-%m-%d').date() if promo_json.get('fechaInicio') else None,
            fecha_fin=datetime.strptime(promo_json.get('fechaFin'), '%Y-%m-%d').date() if promo_json.get('fechaFin') else None,
            activa=promo_json.get('activa', True),
            productos=promo_json.get('productos', [])
        )
