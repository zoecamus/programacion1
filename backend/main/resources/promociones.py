from flask_restful import Resource
from flask import request
from main import db
from main.models.promociones import Promociones as PromocionModel
from main.models.usuarios import Usuarios
from flask_jwt_extended import verify_jwt_in_request, get_jwt

class Promociones(Resource):
    """Recurso para la colección de promociones"""
    
    def get(self):
        """GET /promociones - Obtener todas las promociones (público)"""
        try:
            promociones = db.session.query(PromocionModel).all()
            return {'promociones': [p.to_json() for p in promociones]}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    def post(self):
        """POST /promociones - Crear una nueva promoción (solo Encargado/Admin)"""
        print("=" * 50)
        print("INTENTANDO CREAR PROMOCIÓN")
        try:
            print("Verificando JWT...")
            verify_jwt_in_request()
            claims = get_jwt()
            user_email = claims.get('sub')
            print(f"Usuario: {user_email}")
        
            auth_user = db.session.query(Usuarios).filter_by(id_usuario=user_email).first()

            if not auth_user or auth_user.rol not in ['Encargado', 'Administrador']:
                print("Sin permisos")
                return {'error': 'Sin permisos'}, 403

            print("Usuario tiene permisos")
            data = request.get_json()
            print(f"Datos recibidos: {data}")

            print("Creando promoción desde JSON...")
            promocion = PromocionModel.from_json(data)
            print(f"Promoción creada: {promocion.titulo}")

            # Verificar si el código ya existe
            exists = db.session.query(PromocionModel).filter_by(codigo=promocion.codigo).first()
            if exists:
                print("Código duplicado")
                return {'error': 'El código ya existe'}, 409

            print("Guardando en BD...")
            db.session.add(promocion)
            db.session.commit()
            db.session.refresh(promocion)

            print("✅ Promoción creada exitosamente")
            print("=" * 50)

            return {'mensaje': 'Promoción creada', 'promocion': promocion.to_json()}, 201
        
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            print("=" * 50)
            return {'error': str(e)}, 500