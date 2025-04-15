from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
import os
from flask_sqlalchemy import SQLAlchemy

#Inicializar restful
api = Api()

#Inicializar base de datos
db = SQLAlchemy()

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
        from main.models.pollo1 import Usuario
        db.create_all() 
# importá todos los modelos que necesites

    import main.resources as resources
    #cargar recursos
    api.add_resource(resources.UserResource, '/user/<id>')
    api.add_resource(resources.UsersResource, '/users')
    api.add_resource(resources.NotificacionesResource, '/notificaciones')
    api.add_resource(resources.ValoracionResource, '/valoracion')
    api.add_resource(resources.PedidosResource, '/pedidos')
    api.add_resource(resources.PedidoResource, '/pedidos/<pedido_id>')
    api.add_resource(resources.ProductsResource, '/products')
    api.add_resource(resources.ProductResource, '/products/<product_id>')
    api.add_resource(resources.LogInResource, '/login')
    api.add_resource (resources.LogOutResource, '/logout')   

    api.init_app(app)    
    return app
