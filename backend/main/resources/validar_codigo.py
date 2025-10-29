from flask_restful import Resource
from flask import request
from main import db
from main.models.promociones import Promociones as PromocionModel
from datetime import date

class ValidarCodigo(Resource):
    """Validar y aplicar código promocional"""
    
    def post(self):
        """POST /validar-codigo - Validar código y calcular descuento"""
        print("=" * 50)
        print("🎟️ VALIDANDO CÓDIGO PROMOCIONAL")
        try:
            data = request.get_json()
            print(f"Datos recibidos: {data}")
            
            codigo = data.get('codigo', '').upper().strip()
            productos = data.get('productos', [])
            total = data.get('total', 0)
            
            print(f"Código: {codigo}")
            print(f"Total: ${total}")
            
            if not codigo:
                print("❌ Código vacío")
                return {'valido': False, 'mensaje': 'Código vacío'}, 400
            
            # Buscar promoción por código
            promocion = db.session.query(PromocionModel).filter_by(codigo=codigo).first()
            
            if not promocion:
                print(f"❌ Código '{codigo}' no encontrado")
                return {
                    'valido': False,
                    'mensaje': 'Código no válido'
                }, 404
            
            print(f"✅ Promoción encontrada: {promocion.titulo}")
            
            # Validar que esté activa
            if not promocion.activa:
                print("❌ Promoción inactiva")
                return {
                    'valido': False,
                    'mensaje': 'Esta promoción no está disponible'
                }, 400
            
            # Validar fechas
            hoy = date.today()
            if promocion.fecha_inicio and hoy < promocion.fecha_inicio:
                print(f"❌ Promoción no iniciada (inicia: {promocion.fecha_inicio})")
                return {
                    'valido': False,
                    'mensaje': f'Esta promoción comienza el {promocion.fecha_inicio}'
                }, 400
            
            if promocion.fecha_fin and hoy > promocion.fecha_fin:
                print(f"❌ Promoción vencida (venció: {promocion.fecha_fin})")
                return {
                    'valido': False,
                    'mensaje': 'Esta promoción ya venció'
                }, 400
            
            # Validar productos aplicables
            if promocion.productos:
                productos_promo = promocion.productos.split(',') if isinstance(promocion.productos, str) else []
                
                if productos_promo:
                    productos_carrito = [p.get('nombre', '') for p in productos]
                    aplica = any(prod_cart in productos_promo for prod_cart in productos_carrito)
                    
                    if not aplica:
                        print(f"❌ Productos del carrito no aplican: {productos_carrito}")
                        return {
                            'valido': False,
                            'mensaje': 'Esta promoción no aplica para los productos seleccionados'
                        }, 400
            
            # Calcular descuento según tipo
            descuento_calculado = 0
            
            if promocion.tipo == 'porcentaje':
                descuento_calculado = total * (promocion.descuento / 100)
                print(f"💰 Descuento por porcentaje: {promocion.descuento}% = ${descuento_calculado}")
            elif promocion.tipo == 'monto':
                descuento_calculado = promocion.descuento
                print(f"💰 Descuento fijo: ${descuento_calculado}")
            elif promocion.tipo == '2x1':
                descuento_calculado = total * 0.5
                print(f"💰 Descuento 2x1: 50% = ${descuento_calculado}")
            elif promocion.tipo == 'combo':
                descuento_calculado = promocion.descuento
                print(f"💰 Descuento combo: ${descuento_calculado}")
            
            # No puede ser mayor al total
            if descuento_calculado > total:
                descuento_calculado = total
            
            nuevo_total = total - descuento_calculado
            
            print(f"✅ Código válido!")
            print(f"   Total original: ${total}")
            print(f"   Descuento: -${descuento_calculado}")
            print(f"   Nuevo total: ${nuevo_total}")
            print("=" * 50)
            
            return {
                'valido': True,
                'mensaje': f'¡Código {codigo} aplicado!',
                'promocion': {
                    'id': promocion.id,
                    'titulo': promocion.titulo,
                    'descripcion': promocion.descripcion,
                    'tipo': promocion.tipo,
                    'codigo': promocion.codigo
                },
                'descuento': round(descuento_calculado, 2),
                'nuevoTotal': round(nuevo_total, 2)
            }, 200
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            print("=" * 50)
            return {'valido': False, 'mensaje': 'Error al validar código', 'error': str(e)}, 500