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
    
    # 🔑 CONTRASEÑA SECRETA
    if st.button("Ingresar"):
        if password_input == "123456":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Inténtalo de nuevo.")
    st.stop()

# =========================================================================
# --- SI LA CONTRASEÑA ES CORRECTA, SE MUESTRA EL BUSCADOR CON TU LOGO ---
# =========================================================================

# 🖼️ LOGOTIPO OFICIAL DE KARTONAGE COMPRIMIDO EN TEXTO INTEGRADO (BASE64)
LOGO_BASE64 = (
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/4QA6RXhpZgAATU0AKgAAAAgAAwESAAMAAA"
    "ABAAEAAIdpAAQAAAABAAAAIgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAK6ADAAQAAAABAAAALQAA"
    "AAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoKCgoKBg"
    "sLDAsKDAkKCgr/2wBDAQICAgICAgUDAwUKBwYHCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoK"
    "CgoKCgoKCgoKCgoKCgoKCgr/wAARCAAtACsDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAw"
    "QFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAk"
    "M2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4"
    "iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP0"
    "9fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AA"
    "ECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZH"
    "SElKU1RVVldYWVpjZGVmZ2hpanN0dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5us"
    "LDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD98fFXivwv4E0C"
    "68V+NPEdho+lWMXmXt/qd5Hb29un96SSQhUHuxArzT9nz9uD9lb9qy68SWfwD+Nuj+IpvCOsf2Zr0VuZI"
    "ZLa42hgwSdEaWFv4Zow0T9FY4OPhj/gvj+yn8dvGPhnxR+0n4S/wCEI8X+EvA/ge8vdf8ADvjnWNZVfCc"
    "NrBJJNquiafaP/Z97fSLuUvqIDReXGYtwLK3xf8A8EyP+CKH7TfxZ8DeD/26fDfxM+HXwrTwp4Xbxdoni"
    "fwpbaxe+KPEMX2eScaVfWcl5FaXEUwVreaP/AFAVpGEUigArD8058bLMlgvZe7u5X+Xby38lrzJe9X6I/f"
    "7Uv27f2M9E+L9j+z9rf7SPhWx8aalcNBp/h+61MRTXE69bdS4CmdScGAHzM/wAFeuV/I7+xbpX7Mv7fn9"
    "ofAr47ePPAfgr4geJvFlvf/F7XPiTpt7ea7fW1w0skNvoepXlrcWuk20W8rOtsIpy27/VqG8z+pr9nv4ba"
    "D8HPgN4M+FPha91K50vw34WsdN0+51m6868lhhhVEed+N0mByQAvoAOK0yvHfWpTjKNpRttrvvfbs79Vs9"
    "2ViMO6VnfRnYV+Of8AwW7/AG4Pj5+yp+2fB4N8PfEbVPCel3vwoGqfC7xZqHiXULHwZZ+KFmuBLbeIbXT"
    "w888FwqxIpdRFG0kRLRsFdf2Mrw79rr/glx+wd+3brUfiX9qb9mzRfFOrxaZ/ZsWtC5urC/S1ySsIurO"
    "WGfygWbCbyoySBycsfRxeIwzhhKijK/2k2vuW9t7fPVIeHqUqVXmrRcl2Tsfgx/wU+/bU+Pv7Xf7C3wN"
    "+Ofx8vvhN4kOvw3994e/sfxTfv4s8NaxA8UWo6RcaWyNaTWUfyywyM8UpZo9ylmJX9v/wDglF+y/dfse"
    "/sBeAfhXffFnxB4u1C/wBHTXtX1XX9da/H22+jWeZLVmYrDah2IjiXjksclmYw+Av+CHX/AASh+Gnhi1"
    "8F+HP2DPAt9YWe/yrjxNYy61etvYsc3N+807ck4zIdowBgAAfS/hvRPCHgHwtZeEvDOmado+jaPZR2un2"
    "FlClvbWdtGoVYo0UBI0VQAFUAAADFcuU5ZisJiatfEzUnPRWu2ldOzdvNbaKz1fM7a4vF069KNOnFpJ3b"
    "b3dt0tbdHvfW2m70/wp/wAE0/8AgoXpPgP4EaB4Nuv2iPhvpvxF0HULuPxtofinxt9rvL6VriWST7L4n"
    "1W2lktIURomWxms0iiPmhdwKsPvrwnF4Xg8K6bB4IjsU0VLCFdHTS/L+zLarGBEIfL+Tytm3bt4xjHGK/"
    "mG8K/wDBMv8A4KHfG/wbB+0T8NfA/wAGPH/haW+mkt/HGi+OLG+1G9vBvkmh/wCEmutLuZ7O6jYtGwt"
    "YwYmDKvAVj+4P/AARE/Zf+Lv7IX/BO7wj8H/jZpMOm+IDqWpardaPFf/AGptJiubmSSGzkkDuDKseHkO"
    "9v3srjJwGIcsZisRjZ0MRCUYpXTabV3aybve+tt3fVqyVpGJpUqWHVSnJNtrW97X6LS2mraVt1fW6PrS"
    "iiivXOIKKKKAP/Z"
)

# Mostramos el logo decodificado directamente desde el código
st.image(LOGO_BASE64, width=170)

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

# Botón para cerrar sesión en el menú lateral del celular
if st.sidebar.button("Cerrar Sesión 🔒"):
    st.session_state["autenticado"] = False
    st.rerun()
