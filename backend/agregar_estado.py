"""
Script para agregar campo estado a la tabla Usuarios
"""

import sqlite3
import shutil
from datetime import datetime

def agregar_estado():
    print("=" * 60)
    print("AGREGANDO CAMPO ESTADO")
    print("=" * 60)
    
    db_path = 'DB/pollo2.db'  # ← CAMBIAR AQUÍ
    
    # 1. Hacer backup
    backup_path = f'DB/pollo2.db.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'  # ← CAMBIAR AQUÍ
    print(f"\n📦 Creando backup: {backup_path}")
    shutil.copy(db_path, backup_path)
    print("✅ Backup creado")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 2. Ver columnas actuales
        cursor.execute("PRAGMA table_info(Usuarios)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\n📋 Columnas actuales: {columns}")
        
        # 3. Verificar si ya existe
        if 'estado' in columns:
            print("\n✅ La columna 'estado' ya existe")
            return
        
        # 4. Agregar columna estado
        print("\n➕ Agregando columna 'estado'...")
        cursor.execute("""
            ALTER TABLE Usuarios 
            ADD COLUMN estado VARCHAR(20) DEFAULT 'Activo'
        """)
        
        # 5. Establecer estado 'Activo' para usuarios existentes
        print("📝 Estableciendo estado 'Activo' para usuarios existentes...")
        cursor.execute("""
            UPDATE Usuarios 
            SET estado = 'Activo' 
            WHERE estado IS NULL OR estado = ''
        """)
        
        # 6. Guardar
        conn.commit()
        
        # 7. Verificar
        cursor.execute("PRAGMA table_info(Usuarios)")
        columns_after = [col[1] for col in cursor.fetchall()]
        print(f"\n📋 Columnas después: {columns_after}")
        
        # 8. Mostrar usuarios
        cursor.execute("SELECT id_usuario, nombre, rol, estado FROM Usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        print("\n👥 Usuarios en la BD:")
        for u in usuarios:
            print(f"  - {u[0]} | {u[1]} | {u[2]} | {u[3]}")
        
        print("\n" + "=" * 60)
        print("✅ CAMPO ESTADO AGREGADO EXITOSAMENTE")
        print(f"✅ Backup guardado en: {backup_path}")
        print("=" * 60)
        print("\n⚠️  Ahora debes:")
        print("   1. Reemplazar main/models/usuarios.py con usuarios_final.py")
        print("   2. Reiniciar el servidor: python app.py")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        conn.rollback()
        print(f"\n🔄 Puedes restaurar el backup:")
        print(f"   cp {backup_path} {db_path}")
        raise
    
    finally:
        conn.close()

if __name__ == "__main__":
    agregar_estado()