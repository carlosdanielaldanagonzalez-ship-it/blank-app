import streamlit as st
import pg8000.native

st.set_page_config(page_title="Kartonage - Stock", page_icon="📦", layout="centered")

# --- SISTEMA DE MEMORIA DE SEGURIDAD (SESSION STATE) ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Si el usuario aún no está autenticado, muestra la pantalla del candado
if not st.session_state["autenticado"]:
    st.title("🔒 Acceso Restringido")
    password_input = st.text_input("Introduce la contraseña de acceso para tu iPhone:", type="password")
    
    # 🔑 CONTRASEÑA CONFIGURADA A 123456
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

# 🖼️ LOGOTIPO OFICIAL DE KARTONAGE (Ruta CDN garantizada)
URL_LOGO_EMPRESA = "logo.png"

# Mostramos tu logotipo centrado en la aplicación móvil
st.image(URL_LOGO_EMPRESA, width=220)

st.title("📦 Control de Inventario")
st.caption("Kartonage Empaques y corrugados — Consulta en tiempo real")
st.markdown("---")

def buscar_producto(termino):
    try:
        conn = pg8000.native.connect(
            host="ep-flat-firefly-axqi8b73.c-4.us-east-2.aws.neon.tech",
            user="neondb_owner",
            password="npg_cMOfPi6WmH4p",
            database="neondb",
            ssl_context=True
        )
        
        # Consulta SQL limpia
        sql = """
            SELECT 
                p.code, 
                p.name, 
                p.spec,
                COALESCE((SELECT SUM(quantity) FROM purchases WHERE code = p.code), 0) - 
                COALESCE((SELECT SUM(quantity) FROM sales WHERE code = p.code), 0) AS stock_actual,
                p.sale_price
            FROM products p
            WHERE p.code ILIKE :termino OR p.name ILIKE :termino;
        """
        datos = conn.run(sql, termino=f"%{termino}%")
        conn.close()
        return datos
    except Exception as e:
        st.error(f"Error de conexión con Neon: {e}")
        return []

busqueda = st.text_input("🔍 Escribe el nombre o código del producto:", "")

if busqueda:
    resultados = buscar_producto(busqueda)
    
    if resultados:
        st.success(f"Se encontraron {len(resultados)} coincidencias:")
        
        # 🛠️ CORRECCIÓN CLAVE: Leemos los datos por posición fija de tu consulta SQL para evitar el TypeError
        for fila in resultados:
            codigo = fila[0]
            nombre = fila[1]
            especificacion = fila[2]
            stock = int(fila[3])
            precio = float(fila[4])
            
            with st.container():
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"### **{nombre}**")
                    st.caption(f"Código: {codigo} | Esp: {especificacion}")
                with col2:
                    if stock <= 0:
                        st.markdown(f"## 🔴 **{stock}**\n*Sin stock*")
                    elif stock <= 5:
                        st.markdown(f"## 🟡 **{stock}**\n*Stock bajo*")
                    else:
                        st.markdown(f"## 🟢 **{stock}**\n*Disponible*")
                with col3:
                    st.markdown(f"## 💵 **${precio:.2f}**\n*Precio Venta*")
                st.markdown("---")
    else:
        st.warning("❌ No se encontró ningún producto con ese nombre o código.")
else:
    st.info("💡 Consejo: Puedes escribir solo una parte del nombre.")

# Botón para cerrar sesión en el menú lateral
if st.sidebar.button("Cerrar Sesión 🔒"):
    st.session_state["autenticado"] = False
    st.rerun()
