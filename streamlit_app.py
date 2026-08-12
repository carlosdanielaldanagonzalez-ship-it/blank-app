import streamlit as st
import pandas as pd
import requests
import os

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

# URL del backend (cambiar a tu URL de Render)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# DATOS DE PRUEBA como fallback
PRODUCTOS_MOCK = [
    {"code": "K001", "name": "Caja Cartón A", "spec": "20x20x20", "stock": 150, "price": 2.50},
    {"code": "K002", "name": "Caja Cartón B", "spec": "30x30x30", "stock": 3, "price": 4.75},
    {"code": "K003", "name": "Papel Kraft", "spec": "Rollo", "stock": 0, "price": 15.00},
    {"code": "K004", "name": "Cinta Adhesiva", "spec": "50mm", "stock": 200, "price": 1.25},
]

def buscar_producto(termino):
    """Busca productos via API del backend, usa mock como fallback"""
    try:
        # Intentar conectar al backend
        response = requests.get(f"{BACKEND_URL}/search/{termino}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("productos", [])
    except:
        pass
    
    # Fallback a datos mock si el backend no responde
    st.warning("⚠️ Usando datos de prueba (backend no disponible)")
    termino_lower = termino.lower()
    return [p for p in PRODUCTOS_MOCK 
            if termino_lower in p["code"].lower() or termino_lower in p["name"].lower()]

busqueda = st.text_input("🔍 Escribe el nombre o código del producto:", "")

if busqueda:
    resultados = buscar_producto(busqueda)
    
    if resultados:
        st.success(f"Se encontraron {len(resultados)} coincidencias:")
        
        for producto in resultados:
            codigo = producto["code"]
            nombre = producto["name"]
            especificacion = producto["spec"]
            stock = producto["stock"]
            precio = producto["price"]
            
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
