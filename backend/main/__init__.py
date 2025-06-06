from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

#Inicializar restful
api = Api()

#Inicializar base de datos
db = SQLAlchemy()

#Inicializar autenticación
jwt = JWTManager()

def create_app():
    #inicializar flask
    app = Flask(__name__)
    #cargar varibales de entorno
    load_dotenv()

    #inicializar base de datos
    db_path = os.getenv('DATABASE_PATH')
    db_name = os.getenv('DATABASE_NAME')

# Verificar que las variables estén definidas
    if not db_path or not db_name:
        raise ValueError("DATABASE_PATH o DATABASE_NAME no están definidos en el archivo .env")

# Crear carpeta si no existe
    if not os.path.exists(db_path):
        os.makedirs(db_path)  # esta línea SÍ puede crear carpetas intermedias

#Configurar la URI completa
#Pregunta de final: ¿en que linea tengo que modificar el motor de datos y que va en esa linea?
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print ("base de datos creada en:", os.path.abspath(os.path.join(db_path, db_name)))
    db.init_app(app)
    with app.app_context():
        from main.models.usuarios import Usuarios
        from main.models.productos import Productos
        from main.models.pedidos import Pedidos
        from main.models.valoraciones import Valoraciones
        from main.models.notificaciones import Notificaciones
        from main.models.categorias import Categorias
        from main.models.facturas import Facturas
        from main.models.factura_producto import Factura_Producto
        from main.models.pedido_producto import Pedido_Producto
        db.create_all() 
# importá todos los modelos que necesites 

    import main.resources as resources
    #cargar recursos
    api.add_resource(resources.UserResource, '/user/<string:id_usuario>')
    api.add_resource(resources.UsersResource, '/users')
    api.add_resource(resources.NotificacionesResource, '/notificaciones')
    api.add_resource(resources.ValoracionesResource, '/valoraciones')
    api.add_resource(resources.PedidosResource, '/pedidos')
    api.add_resource(resources.PedidoResource, '/pedido/<pedido_id>')
    api.add_resource(resources.ProductsResource, '/products')
    api.add_resource(resources.ProductResource, '/product/<product_id>')
    api.add_resource(resources.LogInResource, '/login')
    api.add_resource (resources.LogOutResource, '/logout')
    api.add_resource(resources.CategoriasResource, '/categorias') 
    api.add_resource(resources.FacturasResource, '/facturas')
    api.add_resource(resources.FacturaResource, '/factura/<factura_id>')
    api.add_resource(resources.NotificacionResource, '/notificacion/<notificacion_id>')
    api.add_resource(resources.CategoriaResource, '/categoria/<categoria_id>')
    api.add_resource(resources.ValoracionResource, '/valoracion/<string:id_usuario>/<int:id_pedido>')
    api.init_app(app)   

    #cargar clave secreta
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    #cargar tiempo de expiracion de los tokens
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE'))
    jwt.init_app(app)

    from main.auth import routes

    #importar bluepoint
    app.register_blueprint(routes.auth)

    return app
