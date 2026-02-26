
import sqlite3
from pathlib import Path

DB_PATH = Path("data/antigravity.db")

def migrate():
    if not DB_PATH.exists():
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(tenants)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'subscription_tier' not in columns:
            print("Adding 'subscription_tier' column to 'tenants' table...")
            cursor.execute("ALTER TABLE tenants ADD COLUMN subscription_tier TEXT DEFAULT 'free'")
            
            # Set 'demo-saas' to 'pro' for testing
            print("Setting 'demo-saas' to 'pro' tier...")
            cursor.execute("UPDATE tenants SET subscription_tier = 'pro' WHERE slug = 'demo-saas'")
            
            conn.commit()
            print("✅ Migration successful.")
        else:
            print("ℹ️ 'subscription_tier' column already exists.")
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
