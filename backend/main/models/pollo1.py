from .. import db
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.String(60), primary_key=True, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    apellido = db.Column(db.String(30), nullable=False)
    rol = db.Column(db.Enum('Administrador', 'Cliente', 'Encargado'), nullable=False)
    telefono = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(8), nullable=False)
    usuario_pedido = db.relationship('Pedido', back_populates = 'usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_factura = db.relationship('Factura', back_populates = 'usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_valoracion = db.relationship('Valoraciones', back_populates = 'usuario', cascade = "all, delete-orphan")#1 a N relacion
    usuario_notificacion = db.relationship('Notificaciones',back_populates = 'usuario', cascade = "all, delete-orphan")#1 a N relacion
    def to_json(self):
        user_json = {'id_usuario': str(self.id_usuario), 'nombre': str(self.nombre), 'apellido': str(self.apellido), 'rol': (self.rol), 'telefono':str(self.telefono), 'password': str(self.password)}
        return user_json
    @staticmethod
    def from_json(usuario_json):
        id_usuario = usuario_json.get('id_usuario')
        nombre = usuario_json.get('nombre')
        apellido = usuario_json.get('apellido')
        rol = usuario_json.get('rol')
        telefono = usuario_json.get('telefono')
        password = usuario_json.get('password')
        return Usuario(id_usuario=id_usuario, nombre=nombre, apellido=apellido, rol=rol, telefono=telefono, password=password)
    
class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True, nullable = False)
    nombre = db.Column(db.String(30), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    stock = db.Column(db.Integer, nullable=False)
    producto_categoria = db.relationship('Categoria',back_populates='producto',uselist=False, single_parent=True) #
    producto_pedido_producto = db.relationship('Pedido_Producto',back_populates='producto', cascade = "all, delete-orphan")
    producto_factura_producto = db.relationship('Factura_Producto',back_populates='producto', cascade = "all, delete-orphan")
    def to_json(self):
        producto_json = {'id_producto': int(self.id_producto), 'nombre': str(self.nombre), 'id_categoria': int(self.id_categoria),'precio': float(self.precio), 'stock': int(self.stock), 'descripcion': str(self.descripcion)}
        return producto_json
    @staticmethod
    def from_json(producto_json):
        id_producto = producto_json.get('id_producto')
        nombre = producto_json.get('nombre')
        precio = producto_json.get('precio')
        stock  = producto_json.get('stock')
        descripcion = producto_json.get('descripcion')
        id_categoria = producto_json.get('id_categoria')
        return Producto(id_producto=id_producto, nombre=nombre, precio=precio, stock=stock, descripcion=descripcion, id_categoria=id_categoria)
    
class Notificaciones(db.Model):
    __tablename__ = 'notificaciones'
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'), primary_key=True)
    id_usuario = db.Column(db.String(60),db.ForeignKey('usuario.id_usuario'), primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    mensaje = db.Column(db.String(100), nullable=False)
    notificacion_usuario = db.relationship('Usuario',back_populates='notificacion', uselist=False, single_parent=True) #
    notificacion_pedido = db.relationship('Pedido',back_populates='notificacion', cascade = "all, delete-orphan") #
    def to_json(self):
        notificacion_json = {'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'fecha': (self.fecha), 'mensaje': str(self.mensaje)}
        return notificacion_json
    @staticmethod
    def from_json(notificacion_json):
        id_pedido = notificacion_json.get('id_pedido')
        id_usuario = notificacion_json.get('id_usuario')
        fecha = notificacion_json.get('fecha')
        mensaje = notificacion_json.get('mensaje')
        return Notificaciones(id_pedido=id_pedido, id_usuario=id_usuario, fecha=fecha, mensaje=mensaje)
    
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True, nullable=False)
    nombre = db.Column(db.String(30), nullable=False)
    categoria_producto = db.relationship('Producto',back_populates='categoria', cascade = "all, delete-orphan")
    def to_json(self):
        categoria_json = {'id_categoria': int(self.id_categoria), 'nombre': str(self.nombre)}
        return categoria_json
    @staticmethod
    def from_json(categoria_json):
        id_categoria = categoria_json.get('id_categoria')
        nombre = categoria_json.get('nombre')
        return Categoria(id_categoria=id_categoria, nombre=nombre)
    
class Factura(db.Model):
    __tablename__ = 'facturas'
    id_factura = db.Column(db.Integer, primary_key=True, nullable=False)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'), nullable=False)
    id_usuario = db.Column(db.String(60), db.ForeignKey('usuario.id_usuario'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    factura_factura_producto= db.relationship ('Factura_Producto',back_populates='factura', cascade = "all, delete-orphan")
    factura_pedido= db.relationship('Pedido',back_populates='factura',uselist=False, cascade = "all, delete-orphan", single_parent=True)
    factura_usuario= db.relationship('Usuario', back_populates='factura',uselist=False, single_parent=True)

    def to_json(self):
        factura_json = {'id_factura': int(self.id_factura), 'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'total': float(self.total), 'fecha': (self.fecha), 'metodo_pago': str(self.metodo_pago)}
        return factura_json
    @staticmethod
    def from_json(factura_json):
        id_factura = factura_json.get('id_factura')
        id_pedido = factura_json.get('id_pedido')
        id_usuario = factura_json.get('id_usuario')
        total = factura_json.get('total')
        fecha = factura_json.get('fecha')
        metodo_pago = factura_json.get('metodo_pago')
        return Factura(id_factura=id_factura, id_pedido=id_pedido, id_usuario=id_usuario, total=total, fecha=fecha, metodo_pago=metodo_pago)
       
class Pedido(db.Model):
    __tablename__ = 'pedido'
    id_pedido = db.Column(db.Integer, primary_key=True, nullable=False)
    id_usuario = db.Column(db.String(60), db.ForeignKey('usuario.id_usuario'), nullable=False)
    total = db.Column(db.Float)
    estado = db.Column(db.Enum('pendiente', 'en preparación', 'listo para retiro', 'entregado'))
    metodo_pago = db.Column(db.String(50))
    pedido_factura = db.relationship ('Factura',back_populates='pedido', cascade = "all, delete-orphan")
    pedido_pedido_producto = db.relationship('Pedido_Producto',back_populates='pedido', cascade = "all, delete-orphan")
    pedido_usuario = db.relationship ('Usuario', back_populates='pedido',uselist=False ,single_parent=True)
    pedido_notificacion = db.relationship('Notificaciones',back_populates='pedido',uselist=False, single_parent=True)
    def to_json(self):
        pedido_json = {'id_pedido': int(self.id_pedido), 'id_usuario': str(self.id_usuario), 'total': float(self.total), 'estado': (self.estado), 'metodo_pago': str(self.metodo_pago)}
        return pedido_json
    @staticmethod
    def from_json(pedido_json):
        id_pedido = pedido_json.get('id_pedido')
        id_usuario =pedido_json.get('id_usuario')
        total = pedido_json.get('total')
        estado = pedido_json.get('estado')
        metodo_pago = pedido_json.get('metodo_pago')
        return Pedido(id_pedido=id_pedido, id_usuario=id_usuario, total=total, estado=estado, metodo_pago=metodo_pago)

class Valoraciones(db.Model):
    __tablename__ = 'valoraciones'
    id_usuario = db.Column(db.String(60), db.ForeignKey('usuario.id_usuario'), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedido.id_pedido'), primary_key=True)
    mensaje = db.Column(db.String(100), nullable=True)
    puntaje = db.Column(db.Enum('1', '2', '3', '4', '5'), nullable=False)
    valoraciones_usuario = db.relationship('Usuario', back_populates='valoracion',uselist=False, single_parent=True)
    #valoracion_pedido a confirmed
    def to_json(self):
        valoracion_json = {'id_usuario': str(self.id_usuario), 'id_pedido': int(self.id_pedido), 'mensaje': str(self.mensaje), 'puntaje': (self.puntaje)}
        return valoracion_json
    @staticmethod
    def from_json(valoracion_json):
        id_usuario = valoracion_json.get('id_usuario')
        id_pedido = valoracion_json.get('id_pedido')
        mensaje = valoracion_json.get('mensaje')
        puntaje = valoracion_json.get('puntaje')
        return Valoraciones(id_usuario=id_usuario, id_pedido=id_pedido, mensaje=mensaje, puntaje=puntaje)
    
class Factura_Producto(db.Model):
    __tablename__ = 'facturas_productos'
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id_factura'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), primary_key=True)
    linea_factura_producto = db.Column(db.Integer, nullable=False)
    factura_producto_producto = db.relationship('Producto', uselist=False, back_populates='factura_producto', single_parent=True)
    factura_producto_factura = db.relationship('Factura', uselist=False, back_populates='factura_producto', single_parent=True)
    def to_json(self):
        factura_producto_json = {'id_factura': int(self.id_factura), 'id_producto': int(self.id_producto), 'linea-factura-producto': int(self.linea_factura_producto)}
        return factura_producto_json
    @staticmethod
    def from_json(factura_producto_json):
        id_factura = factura_producto_json.get('id_factura')
        id_producto = factura_producto_json.get('id_producto')
        linea_factura_producto = factura_producto_json.get('linea-factura-producto')        
        return Factura_Producto(id_factura=id_factura, id_producto=id_producto, linea_factura_producto=linea_factura_producto)

class Pedido_Producto(db.Model):
    __tablename__ = 'pedidos_productos'
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), primary_key=True)
    linea_pedido_producto = db.Column(db.Integer, nullable=False)
    pedido_producto_producto = db.relationship('Producto', uselist=False, back_populates='pedido_producto', single_parent=True)
    pedido_producto_pedido = db.relationship('Pedido', uselist=False, back_populates='pedido_producto', single_parent=True)
    def to_json(self):
        pedido_producto_json = {'id_pedido': int(self.id_pedido), 'id_producto': int(self.id_producto), 'linea-pedido-producto': int(self.linea_pedido_producto)}
        return pedido_producto_json
    @staticmethod    
    def from_json(pedido_producto_json):
        id_pedido = pedido_producto_json.get('id_pedido')
        id_producto = pedido_producto_json.get('id_producto')
        linea_pedido_producto = pedido_producto_json.get('linea-pedido-producto')        
        return Pedido_Producto(id_pedido=id_pedido, id_producto=id_producto, linea_pedido_producto=linea_pedido_producto)