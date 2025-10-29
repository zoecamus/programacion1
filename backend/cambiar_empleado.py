#!/usr/bin/env python3
"""
Script para cambiar rol 'Empleado' a 'Encargado' en la BD
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app, db
from main.models import Usuariomodel

def cambiar_empleado_a_encargado():
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("🔄 Cambiando 'Empleado' → 'Encargado'")
        print("=" * 50)
        
        # Buscar todos los usuarios con rol Empleado
        usuarios = db.session.query(Usuariomodel).all()
        
        empleados_encontrados = 0
        
        for usuario in usuarios:
            # SQLAlchemy puede tener problemas con el enum, accedemos directo
            try:
                if usuario.rol == 'Empleado':
                    print(f"📝 Cambiando: {usuario.nombre} {usuario.apellido} ({usuario.id_usuario})")
                    # Usar raw SQL para evitar problemas con el enum
                    db.session.execute(
                        "UPDATE Usuarios SET rol = 'Encargado' WHERE id_usuario = :id",
                        {'id': usuario.id_usuario}
                    )
                    empleados_encontrados += 1
            except:
                # Si hay error al leer el rol, probablemente es un Empleado
                print(f"⚠️  Usuario con rol inválido: {usuario.id_usuario}")
                db.session.execute(
                    "UPDATE Usuarios SET rol = 'Encargado' WHERE id_usuario = :id",
                    {'id': usuario.id_usuario}
                )
                empleados_encontrados += 1
        
        db.session.commit()
        
        if empleados_encontrados > 0:
            print(f"\n✅ {empleados_encontrados} usuario(s) actualizados")
        else:
            print("\n✅ No se encontraron usuarios con rol 'Empleado'")
        
        print("\n📊 Roles actuales en la BD:")
        result = db.session.execute("SELECT DISTINCT rol FROM Usuarios")
        for row in result:
            print(f"   - {row[0]}")
        
        print("=" * 50)

if __name__ == '__main__':
    cambiar_empleado_a_encargado()