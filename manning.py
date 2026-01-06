import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

g = 9.81  # gravedad

# ===============================
# Configuración de página
# ===============================
st.set_page_config(
    page_title="Canales en Flujo Nominal",
    layout="wide"
)

st.title("🌊 Diseño de canales en flujo nominal")
st.markdown(
    "**Cálculo hidráulico de canales**  \n"
    "Prof. Gregory Guevara — Riego & Drenaje / Universidad EARTH"
)

# ===============================
# Sidebar - Entradas
# ===============================
st.sidebar.header("🔧 Parámetros de entrada")
canal_tipo = st.sidebar.selectbox(
    "Tipo de canal",
    ["Trapezoidal", "Alcantarilla redonda", "Surco rectangular"]
)

Q = st.sidebar.number_input("Caudal (m³/s)", min_value=0.01, value=0.2, step=0.01)
S = st.sidebar.number_input("Pendiente del canal (%)", min_value=0.001, value=0.5, step=0.01)

# Material rugosidad (coeficiente Manning)
material = st.sidebar.selectbox(
    "Material",
    ["Concreto", "Tierra uniforme", "Suelo expuesto"]
)
if material == "Concreto":
    n = 0.014
elif material == "Tierra uniforme":
    n = 0.025
else:
    n = 0.032

# Parámetros geométricos según tipo de canal
if canal_tipo == "Trapezoidal":
    b = st.sidebar.number_input("Base (m)", min_value=0.1, value=1.0)
    z = st.sidebar.number_input("Talud lateral (z = H/V)", min_value=0.0, value=1.0)
elif canal_tipo == "Alcantarilla redonda":
    D = st.sidebar.number_input("Diámetro (m)", min_value=0.1, value=0.5)
elif canal_tipo == "Surco rectangular":
    b = st.sidebar.number_input("Base (m)", min_value=0.1, value=0.5)
    h = st.sidebar.number_input("Altura (m)", min_value=0.1, value=0.3)

# ===============================
# Ayuda teórica
# ===============================
with st.expander("📘 Ayuda teórica"):
    st.markdown("### Fórmulas principales")
    st.latex(r"""
    Q = \frac{1}{n} A R^{2/3} S^{1/2} \quad ; \quad R = \frac{A}{P}
    """)
    st.latex(r"V = \frac{Q}{A} \quad ; \quad F_r = \frac{V}{\sqrt{g \cdot A / T}}")
    st.markdown("""
    **Donde:**  
    - Q: caudal (m³/s)  
    - A: área de sección transversal (m²)  
    - R: radio hidráulico (m)  
    - P: perímetro mojado (m)  
    - V: velocidad (m/s)  
    - Fr: número de Froude  
    - S: pendiente del canal (m/m)  
    """)

# ===============================
# Cálculos
# ===============================
y = 0.001  # tirante inicial
dy = 0.001
max_iter = 100000

# Función general para encontrar tirante normal
def calcular_tirante(Q, b=0, z=0, D=0, h=0, tipo="Trapezoidal"):
    y = dy
    for _ in range(max_iter):
        if tipo == "Trapezoidal":
            A = (b + z*y) * y
            P = b + 2*y*np.sqrt(1+z**2)
        elif tipo == "Alcantarilla redonda":
            # aproximación flujo completo circular
            A = np.pi*D**2/4
            P = np.pi*D
        elif tipo == "Surco rectangular":
            A = b*h
            P = b + 2*h
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5  # Manning
        Q_calc = A * V
        if Q_calc >= Q:
            break
        y += dy
    Fr = V / np.sqrt(g * A / (b + 2*z*y) if tipo=="Trapezoidal" else g*A/b)
    return y, A, P, R, V, Fr

if canal_tipo == "Trapezoidal":
    y, A, P, R, V, Fr = calcular_tirante(Q, b=b, z=z, tipo="Trapezoidal")
elif canal_tipo == "Alcantarilla redonda":
    y, A, P, R, V, Fr = calcular_tirante(Q, D=D, tipo="Alcantarilla redonda")
else:
    y, A, P, R, V, Fr = calcular_tirante(Q, b=b, h=h, tipo="Surco rectangular")

# Velocidad crítica y pendiente crítica
Vc = np.sqrt(g*A/(b + 2*z*y if canal_tipo=="Trapezoidal" else b))
Sc = ((Vc*n)/R**(2/3))**2
Qmax = A * Vc

# ===============================
# Resultados
# ===============================
st.header("🔹 Resultados principales")
col1, col2 = st.columns(2)
with col1:
    st.metric("Tirante normal (m)", round(y,3))
    st.metric("Área sección (m²)", round(A,3))
with col2:
    st.metric("Velocidad (m/s)", round(V,3))
    st.metric("Número Froude", round(Fr,3))

st.header("🔹 Resultados secundarios")
st.write(f"- Perímetro mojado (P): {round(P,3)} m")
st.write(f"- Radio hidráulico (R): {round(R,3)} m")
st.write(f"- Caudal máximo (Qmax): {round(Qmax,3)} m³/s")
st.write(f"- Pendiente crítica (Sc): {round(Sc*100,3)} %")
st.write(f"- Velocidad crítica (Vc): {round(Vc,3)} m/s")

# ===============================
# Gráfico
# ===============================
fig, ax = plt.subplots(figsize=(8,4))
ax.plot([0,y],[0,y], label="Tirante", color="#1f77b4")
ax.axhline(y, color="red", linestyle="--", label="Tirante normal")
ax.set_xlabel("Longitud (m)")
ax.set_ylabel("Tirante (m)")
ax.set_title("Tirante nominal")
ax.legend()
ax.grid(True, linestyle=":", alpha=0.7)
st.pyplot(fig)
fig.savefig("grafico_canales.png", dpi=300)

# ===============================
# PDF One Page
# ===============================
st.header("📄 Exportar memoria de cálculo (1 página)")

if st.button("📥 Generar PDF"):
    pdf = "Canales_FlujoNominal.pdf"
    doc = SimpleDocTemplate(pdf, pagesize=letter,
                            rightMargin=36, leftMargin=36,
                            topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    e = []
    
    e.append(Paragraph("<b>Diseño de Canales – Flujo Nominal</b>", styles["Title"]))
    e.append(Paragraph(f"Tipo de canal: {canal_tipo} | Material: {material}", styles["Normal"]))
    e.append(Paragraph(f"Caudal: {Q} m³/s | Pendiente: {S} %", styles["Normal"]))
    e.append(Spacer(1,6))
    
    # Principales
    e.append(Paragraph("<b>Resultados principales</b>", styles["Heading3"]))
    table_main = Table([
        ["Tirante (m)", "Área (m²)", "Velocidad (m/s)", "Froude"],
        [round(y,3), round(A,3), round(V,3), round(Fr,3)]
    ])
    e.append(table_main)
    
    # Secundarios
    e.append(Spacer(1,6))
    e.append(Paragraph("<b>Resultados secundarios</b>", styles["Heading3"]))
    table_sec = Table([
        ["P (m)", "R (m)", "Qmax (m³/s)", "Pendiente crítica (%)", "Vc (m/s)"],
        [round(P,3), round(R,3), round(Qmax,3), round(Sc*100,3), round(Vc,3)]
    ])
    e.append(table_sec)
    
    e.append(Spacer(1,8))
    e.append(Image("grafico_canales.png", width=14*cm, height=7*cm))
    
    doc.build(e)
    st.success("📄 PDF generado correctamente")
    st.download_button("⬇️ Descargar PDF", open(pdf, "rb"), file_name=pdf)
