from flask import Flask
from dotenv import load_dotenv

from flask_restful import Api
import main.resources as resources


#Inicializar restful
api = Api()

def create_app():
    #inicializar flask
    app = Flask(__name__)
    #cargar varibales de entorno
    load_dotenv()
    #cargar recursos
    api.add_resource(resources.UserResource, '/user/<int:user_id>')
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