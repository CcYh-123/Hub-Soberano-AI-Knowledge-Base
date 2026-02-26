
from core.database import SessionLocal, HistoricalData, Tenant
from datetime import datetime
import json

def get_baseline(tenant_slug):
    db = SessionLocal()
    tenant = db.query(Tenant).filter(Tenant.slug == tenant_slug).first()
    if not tenant:
        print(f"Error: Tenant {tenant_slug} not found")
        return None
    
    sectors = ["pharmacy", "fashion", "real_estate"]
    baseline = {}
    
    for sector in sectors:
        # Get latest data points
        latest = db.query(HistoricalData).filter(
            HistoricalData.tenant_id == tenant.id,
            HistoricalData.sector == sector
        ).order_by(HistoricalData.timestamp.desc()).limit(10).all()
        
        if latest:
            avg_price = sum(d.price for d in latest) / len(latest)
            baseline[sector] = {
                "avg_price": avg_price,
                "count": len(latest)
            }
        else:
            # Defaults if no data
            baseline[sector] = {"avg_price": 100, "count": 0}
            
    db.close()
    return baseline

if __name__ == "__main__":
    import sys
    slug = sys.argv[1] if len(sys.argv) > 1 else "demo-saas"
    data = get_baseline(slug)
    print(json.dumps(data, indent=2))
