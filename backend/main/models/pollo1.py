from .. import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def to_json(self):
        user_json = {'id': self.id, 'nombre': str(self.nombre), 'apellido': str(self.apellido), 'rol': str(self.rol), 'password': str(self.password)}
        return user_json
    
    @staticmethod
    def from_json(usuario_json):
        id = usuario_json.get('id')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        rol = usuario_json.get('rol')
        password = usuario_json.get('password')
        return Usuario(id=id, nombre=nombre, apellido=apellido, rol=rol, password=password)
