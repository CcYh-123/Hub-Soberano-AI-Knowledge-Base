from core.database import init_db, SessionLocal, Tenant
import sys

def bootstrap():
    print("🚀 Inicializando Base de Datos Antigravity...")
    try:
        init_db()
        print("✅ Tablas creadas correctamente.")
        
        db = SessionLocal()
        # Crear tenant por defecto si no existe
        default_tenant = db.query(Tenant).filter(Tenant.slug == 'default-client').first()
        if not default_tenant:
            new_tenant = Tenant(
                name="Cliente Predeterminado",
                slug="default-client"
            )
            db.add(new_tenant)
            db.commit()
            print(f"✅ Tenant creado: 'default-client' (ID: {new_tenant.id})")
        else:
            print("ℹ️ Tenant 'default-client' ya existe.")
            
        # Crear un tenant de prueba para validación de aislamiento
        demo_tenant = db.query(Tenant).filter(Tenant.slug == 'demo-saas').first()
        if not demo_tenant:
            new_demo = Tenant(
                name="Demo SaaS User",
                slug="demo-saas"
            )
            db.add(new_demo)
            db.commit()
            print(f"✅ Tenant creado: 'demo-saas' (ID: {new_demo.id})")
        
        db.close()
        print("\n✨ Sistema listo para operación Multi-Tenant.")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)

if __name__ == "__main__":
    bootstrap()
