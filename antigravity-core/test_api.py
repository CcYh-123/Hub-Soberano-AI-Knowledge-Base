import httpx
import json
import sys

# Forzar salida UTF-8 en Windows para evitar errores de encoding con emojis
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_ingestion():
    tenant_id = "tenant_test_001"
    
    # 0. Registrar Webhook de prueba
    from notifier import register_webhook
    register_webhook(tenant_id, "https://httpbin.org/post")
    print(f"[PRE-TEST] Webhook registrado para {tenant_id}")

    # 1. OBTENER TOKEN JWT
    token_url = "http://127.0.0.1:8000/token"
    print(f"\n--- Solicitando Token para {tenant_id} ---")
    
    try:
        with httpx.Client() as client:
            token_resp = client.post(token_url, data={"username": tenant_id, "password": "password_dummy"})
            if token_resp.status_code != 200:
                print(f"❌ Error al obtener token: {token_resp.text}")
                return
            
            access_token = token_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print(f"✅ Token obtenido: {access_token[:20]}...")

            # 2. PROBAR INGESTA PROTEGIDA
            ingest_url = "http://127.0.0.1:8000/ingest"
            # Inyectamos datos que superen el umbral (leak > 20)
            payload = [
                {"product_id": "CRITICAL-SKU-01", "costo_viejo": 100.0, "costo_nuevo": 150.0},
                {"product_id": "CRITICAL-SKU-02", "costo_viejo": 100.0, "costo_nuevo": 160.0}
            ]
            
            print(f"\n--- Iniciando prueba de ingesta con GENERACION DE REPORTE ---")
            response = client.post(ingest_url, json=payload, headers=headers, timeout=10.0)
            
            print(f"Status Code: {response.status_code}")
            result = response.json()
            print("Response Payload:")
            print(json.dumps(result, indent=2))
            
            if response.status_code == 200:
                report_id = result.get("report_id")
                if report_id:
                    print(f"✅ Reporte generado exitosamente: {report_id}")
                    
                    # 3. PROBAR DESCARGA DE REPORTE
                    print(f"\n--- Probando descarga segura del reporte ---")
                    download_url = f"http://127.0.0.1:8000/download-audit/{report_id}"
                    dl_resp = client.get(download_url, headers=headers)
                    
                    if dl_resp.status_code == 200:
                        print(f"✅ Descarga exitosa. Tamaño: {len(dl_resp.content)} bytes")
                        # Opcional: Guardar localmente para inspección manual
                        with open("last_test_report.pdf", "wb") as f:
                            f.write(dl_resp.content)
                        print("📄 Reporte guardado como 'last_test_report.pdf' para revision.")
                    else:
                        print(f"❌ Error al descargar reporte: {dl_resp.status_code}")
                else:
                    print("⚠️ No se genero reporte (quizas el leak no supero el umbral).")
            else:
                print("\n[ERROR] Falla en la ingesta.")
                
    except Exception as e:
        print(f"\n[ERROR] Falla en la comunicacion: {e}")
        print("Asegurate de que el servidor este corriendo.")

if __name__ == "__main__":
    test_ingestion()
