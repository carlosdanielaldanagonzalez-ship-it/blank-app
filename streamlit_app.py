import streamlit as st
import psycopg2
import pandas as pd

st.set_page_config(page_title="Kartonage - Stock", page_icon="📦", layout="centered")

# --- SISTEMA DE MEMORIA DE SEGURIDAD (SESSION STATE) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Si el usuario aún no está autenticado, muestra la pantalla del candado
if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Restringido")
    password_input = st.text_input("Introduce la contraseña de acceso para tu iPhone:", type="password")
    
    # 🔑 CONTRASEÑA SECRETA DE ACCESO
    if st.button("Ingresar"):
        if password_input == "mi_clave_123": # <--- Cambia esto por la contraseña que tú quieras
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()

# =========================================================================
# --- SI LA CONTRASEÑA ES CORRECTA, SE MUESTRA EL BUSCADOR CON TU LOGO ---
# =========================================================================

# 🖼️ LOGOTIPO OFICIAL DE KARTONAGE (Extraído de tu Facebook)
URL_LOGO_EMPRESA = "https://fbcdn.net" 

# Mostramos el logo centrado en la aplicación móvil
st.image(URL_LOGO_EMPRESA, width=160)

st.title("📦 Control de Inventario")
st.caption("Kartonage Empaques y corrugados — Consulta en tiempo real")
st.markdown("---")

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
        columnas = [desc for desc in cursor.description]
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

# Botón para cerrar sesión en el menú del celular
if st.sidebar.button("Cerrar Sesión 🔒"):
    st.session_state["autenticado"] = False
    st.rerun()
