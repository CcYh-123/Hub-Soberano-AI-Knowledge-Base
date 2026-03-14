import polars as pl
from typing import List, Dict, Any

def process_vendor_list(data: List[Dict[str, Any]], tenant_id: str) -> pl.DataFrame:
    """
    Procesa una lista de datos de proveedores usando Polars.
    Inyecta el tenant_id y calcula la columna delta_erosion.
    """
    if not data:
        # Retornar un dataframe vacío con el esquema esperado si no hay datos
        return pl.DataFrame(schema={
            "product_id": pl.String,
            "costo_viejo": pl.Float64,
            "costo_nuevo": pl.Float64,
            "tenant_id": pl.String,
            "delta_erosion": pl.Float64
        })

    # Convertir a DataFrame de Polars
    df = pl.DataFrame(data)

    # Inyectar tenant_id
    df = df.with_columns(pl.lit(tenant_id).alias("tenant_id"))

    # Calcular delta_erosion (costo_nuevo - costo_viejo)
    # Asumimos que las columnas costo_viejo y costo_nuevo existen en la data
    df = df.with_columns(
        (pl.col("costo_nuevo") - pl.col("costo_viejo")).alias("delta_erosion")
    )

    return df

if __name__ == "__main__":
    # Prueba rápida
    test_data = [
        {"product_id": "P001", "costo_viejo": 100.0, "costo_nuevo": 110.0},
        {"product_id": "P002", "costo_viejo": 50.0, "costo_nuevo": 45.0},
    ]
    result = process_vendor_list(test_data, "tenant_alpha")
    print(result)
