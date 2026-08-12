import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Consultor de Stock", page_icon="📦", layout="centered")

# --- BLOQUE DE SEGURIDAD MANUAL ---
password_input = st.text_input("🔑 Introduce la contraseña de acceso:", type="password")

# 🔥 CAMBIA "mi_clave_123" por la contraseña secreta que tú quieras usar en tu iPhone
if password_input != "mi_clave_123":
    st.warning("⚠️ Acceso restringido. Por favor, introduce la clave correcta.")
    st.stop()  # Detiene el código si la clave es incorrecta
# ----------------------------------

st.title("📦 Control de Inventario en Tiempo Real")
st.subheader("Neon Database Link")

CONN_STR = "postgresql://neondb_owner:npg_cMOfPi6WmH4p@ep-flat-firefly-axqi8b73.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"


def buscar_producto(termino):
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
            WHERE p.code ILIKE %s OR p.name ILIKE %s;
        """
        cursor.execute(sql, (f"%{termino}%", f"%{termino}%"))
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(datos, columns=columnas)
    except Exception as e:
        st.error(f"Error de conexión con Neon: {e}")
        return pd.DataFrame()


busqueda = st.text_input("🔍 Escribe el nombre o código del producto:", "")

if busqueda:
    df = buscar_producto(busqueda)
    if not df.empty:
        st.success(f"Se encontraron {len(df)} coincidencias:")
        for index, fila in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"### **{fila['name']}**")
                    st.caption(f"Código: {fila['code']} | Esp: {fila['spec']}")
                with col2:
                    stock = int(fila['stock_actual'])
                    if stock <= 0:
                        st.markdown(f"## 🔴 **{stock}**\n*Sin stock*")
                    elif stock <= 5:
                        st.markdown(f"## 🟡 **{stock}**\n*Stock bajo*")
                    else:
                        st.markdown(f"## 🟢 **{stock}**\n*Disponible*")
                with col3:
                    st.markdown(f"## 💵 **${fila['sale_price']:.2f}**\n*Precio Venta*")
                st.markdown("---")
    else:
        st.warning("❌ No se encontró ningún producto con ese nombre o código.")
else:
    st.info("💡 Consejo: Puedes escribir solo una parte del nombre.")
