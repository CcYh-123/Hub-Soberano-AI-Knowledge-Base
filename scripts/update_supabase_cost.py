import os

from dotenv import load_dotenv
from supabase import create_client


TARGET_SKU = "PRODUCTO_TEST_AGRO"
NEW_INTERNAL_PRICE = 850


def main():
    """
    
    Actualiza el costo real (precio_interno) en Supabase
    para el SKU de prueba en la tabla `dashboard_agro`.
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("[update_supabase_cost] ❌ Falta SUPABASE_URL o SUPABASE_KEY en el entorno/.env")
        return

    supabase = create_client(url, key)

    print(f"[update_supabase_cost] Conectando a Supabase → dashboard_agro")
    try:
        # 1) Intentar UPDATE
        response = (
            supabase
            .table("dashboard_agro")
            .update({"precio_interno": NEW_INTERNAL_PRICE})
            .eq("producto_sku", TARGET_SKU)
            .execute()
        )
        updated_rows = response.data or []

        if updated_rows:
            print(f"[update_supabase_cost] ✅ Actualizado precio_interno={NEW_INTERNAL_PRICE} para SKU '{TARGET_SKU}'.")
            return

        print(f"[update_supabase_cost] ⚠️ No se encontraron filas para SKU '{TARGET_SKU}'. Intentando INSERT...")

        # 2) Si no existía, hacemos INSERT con los campos mínimos necesarios
        insert_payload = {
            "producto_sku":   TARGET_SKU,
            "precio_interno": NEW_INTERNAL_PRICE,
            "precio_mercado": 1200,
        }
        insert_resp = (
            supabase
            .table("dashboard_agro")
            .insert(insert_payload)
            .execute()
        )
        inserted = insert_resp.data or []
        if inserted:
            print(f"[update_supabase_cost] ✅ Insertado nuevo registro para SKU '{TARGET_SKU}' con precio_interno={NEW_INTERNAL_PRICE}.")
        else:
            print(f"[update_supabase_cost] ⚠️ El INSERT no devolvió filas para SKU '{TARGET_SKU}'.")

    except Exception as e:
        print(f"[update_supabase_cost] ❌ Error al actualizar/insertar en Supabase: {repr(e)}")
        return


if __name__ == "__main__":
    main()

