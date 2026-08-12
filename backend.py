"""
Backend API simple para consultar base de datos Neon
Puede correrse localmente o en Render
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from typing import List

app = FastAPI()

# Permitir CORS para que Streamlit Cloud pueda llamar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONN_STR = "postgresql://neondb_owner:npg_cMOfPi6WmH4p@ep-flat-firefly-axqi8b73.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

@app.get("/")
def root():
    return {"status": "Backend Kartonage activo"}

@app.get("/search/{termino}")
def buscar_producto(termino: str):
    """Busca productos en la base de datos Neon"""
    try:
        conn = psycopg2.connect(CONN_STR)
        cursor = conn.cursor()
        
        sql = """
            SELECT 
                p.code, 
                p.name, 
                p.spec,
                COALESCE((SELECT SUM(quantity) FROM purchases WHERE code = p.code), 0) - 
                COALESCE((SELECT SUM(quantity) FROM sales WHERE code = p.code), 0) AS stock_actual,
                p.sale_price
            FROM products p
            WHERE p.code ILIKE %s OR p.name ILIKE %s
            LIMIT 50;
        """
        cursor.execute(sql, (f"%{termino}%", f"%{termino}%"))
        datos = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convertir a diccionarios
        productos = []
        for fila in datos:
            productos.append({
                "code": fila[0],
                "name": fila[1],
                "spec": fila[2],
                "stock": int(fila[3]) if fila[3] else 0,
                "price": float(fila[4]) if fila[4] else 0.0
            })
        
        return {"success": True, "productos": productos}
    except Exception as e:
        return {"success": False, "error": str(e), "productos": []}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
