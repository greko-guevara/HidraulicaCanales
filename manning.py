import streamlit as st
import numpy as np
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
    page_title="Canal Trapezoidal – Flujo Nominal",
    layout="wide"
)

st.title("🌊 Diseño de canal trapezoidal en flujo nominal")
st.markdown(
    "**Cálculo hidráulico de canal trapezoidal**  \n"
    "Prof. Gregory Guevara — Riego & Drenaje / Universidad EARTH"
)

# ===============================
# Sidebar - Entradas
# ===============================
st.sidebar.header("🔧 Parámetros de entrada")

Q = st.sidebar.number_input("Caudal (m³/s)", min_value=0.01, value=1.0, step=0.01)
S = st.sidebar.number_input("Pendiente del canal (%)", min_value=0.01, value=0.5, step=0.01)

b = st.sidebar.number_input("Base del canal (m)", min_value=0.1, value=0.5)
z = st.sidebar.number_input("Talud lateral (z = H/V)", min_value=0.0, value=1.0)

material = st.sidebar.selectbox(
    "Material del canal",
    ["Concreto", "Tierra uniforme", "Suelo expuesto"]
)
if material == "Concreto":
    n = 0.014
elif material == "Tierra uniforme":
    n = 0.025
else:
    n = 0.032

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
dy = 0.001
max_iter = 100000

def calcular_tirante(Q, b, z):
    y = dy
    for _ in range(max_iter):
        A = (b + z*y) * y
        P = b + 2*y*np.sqrt(1 + z**2)
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5  # Manning
        Q_calc = A * V
        if Q_calc >= Q:
            break
        y += dy
    T = b + 2*z*y
    Fr = V / np.sqrt(g * A / T)
    return y, A, P, R, V, Fr

y, A, P, R, V, Fr = calcular_tirante(Q, b, z)

# Velocidad crítica y pendiente crítica
Vc = np.sqrt(g*A/(b + 2*z*y))
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
st.header("📈 Perfil del canal trapezoidal")
fig, ax = plt.subplots(figsize=(8,4))
# Base
ax.plot([-b/2, b/2], [0,0], color='brown', linewidth=4, label="Base")
# Taludes
ax.plot([-b/2, -b/2 - z*y], [0, y], color='blue', linewidth=2, label="Taludes")
ax.plot([b/2, b/2 + z*y], [0, y], color='blue', linewidth=2)
# Tirante
ax.hlines(y, -b/2 - z*y, b/2 + z*y, color='green', linestyle='--', label="Tirante normal")
ax.set_xlabel("m")
ax.set_ylabel("m")
ax.set_title("Sección transversal – Canal trapezoidal")
ax.legend()
ax.grid(True, linestyle=":", alpha=0.7)
st.pyplot(fig)
fig.savefig("grafico_canal.png", dpi=150)

# ===============================
# PDF One Page
# ===============================
st.header("📄 Exportar memoria de cálculo (1 página)")
if st.button("📥 Generar PDF"):
    pdf = "Canal_Trapezoidal.pdf"
    doc = SimpleDocTemplate(pdf, pagesize=letter,
                            rightMargin=36, leftMargin=36,
                            topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    e = []
    
    e.append(Paragraph("<b>Diseño de Canal Trapezoidal – Flujo Nominal</b>", styles["Title"]))
    e.append(Paragraph(f"Material: {material}", styles["Normal"]))
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
    e.append(Image("grafico_canal.png", width=14*cm, height=7*cm))
    
    doc.build(e)
    st.success("📄 PDF generado correctamente")
    st.download_button("⬇️ Descargar PDF", open(pdf, "rb"), file_name=pdf)
