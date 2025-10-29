from flask import Flask
from dotenv import load_dotenv
from flask_restful import Api
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS

api = Api()
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mailsender = Mail()

def create_app():
    app = Flask(__name__)
    load_dotenv()
    
    # ← CONFIGURAR CORS DE FORMA MÁS EXPLÍCITA
    CORS(app, 
         origins=["http://localhost:4200"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
         supports_credentials=True,
         expose_headers=["Content-Type", "Authorization"],
         max_age=3600)

    db_path = os.getenv('DATABASE_PATH')
    db_name = os.getenv('DATABASE_NAME')

    if not db_path or not db_name:
        raise ValueError("DATABASE_PATH o DATABASE_NAME no están definidos en el archivo .env")

    if not os.path.exists(db_path):
        os.makedirs(db_path)  

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(db_path, db_name)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    print("base de datos creada en:", os.path.abspath(os.path.join(db_path, db_name)))
    
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
        from main.models.promociones import Promociones
        db.create_all() 

    import main.resources as resources
    api.add_resource(resources.UserResource, '/user/<string:id_usuario>')
    api.add_resource(resources.UsersResource, '/users')
    api.add_resource(resources.NotificacionesResource, '/notificaciones')
    api.add_resource(resources.ValoracionesResource, '/valoraciones')
    api.add_resource(resources.PedidosResource, '/pedidos')
    api.add_resource(resources.PedidoResource, '/pedido/<pedido_id>')
    api.add_resource(resources.ProductsResource, '/products')
    api.add_resource(resources.ProductResource, '/product/<product_id>')
    api.add_resource(resources.LogInResource, '/login')
    api.add_resource(resources.LogOutResource, '/logout')
    api.add_resource(resources.CategoriasResource, '/categorias') 
    api.add_resource(resources.FacturasResource, '/facturas')
    api.add_resource(resources.FacturaResource, '/factura/<factura_id>')
    api.add_resource(resources.NotificacionResource, '/notificacion/<notificacion_id>')
    api.add_resource(resources.CategoriaResource, '/categoria/<categoria_id>')
    api.add_resource(resources.ValoracionResource, '/valoracion/<string:id_usuario>/<int:id_pedido>')
    api.add_resource(resources.PromocionesResource, "/promociones")           # GET, POST (colección)
    api.add_resource(resources.PromocionResource,  "/promocion/<int:id_promocion>")  
    api.add_resource(resources.ValidarCodigoResource, "/validar-codigo")  # POST
    api.init_app(app)   

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE'))
    jwt.init_app(app)
    
    from main.auth.decorators import add_claims_to_access_token, user_identity_lookup
    jwt.additional_claims_loader(add_claims_to_access_token)
    jwt.user_identity_loader(user_identity_lookup)

    from main.auth import routes
    app.register_blueprint(routes.auth)

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_HOSTNAME'] = os.getenv('MAIL_HOSTNAME')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['FLASKY_MAIL_SENDER'] = os.getenv('FLASKY_MAIL_SENDER')
    mailsender.init_app(app)

    return app