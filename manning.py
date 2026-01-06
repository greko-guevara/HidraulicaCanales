import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# ===============================
# CONFIGURACIÓN
# ===============================
st.set_page_config(
    page_title="Canal Normal – Flujo Nominal",
    layout="wide"
)

st.title("💧 Diseño de canal trapezoidal")
st.markdown(
    "**Cálculo de tirante normal, área, velocidad y número de Froude**  \n"
    "Prof. Gregory Guevara — Riego & Drenaje / Universidad EARTH"
)

# ===============================
# ENTRADAS
# ===============================
st.sidebar.header("🔧 Parámetros de entrada")

Q = st.sidebar.number_input("Caudal Q (m³/s)", min_value=0.001, value=1.0, step=0.01)
b = st.sidebar.number_input("Base del canal b (m)", min_value=0.1, value=1.0, step=0.1)
z = st.sidebar.number_input("Talud lateral z", min_value=0.0, value=1.0, step=0.1)
S = st.sidebar.number_input("Pendiente S (%)", min_value=0.001, value=1.0, step=0.1) / 100

material = st.sidebar.selectbox(
    "Material del canal",
    ["Concreto", "Tierra alineada y uniforme", "Suelo expuesto"]
)

# Coeficiente de Manning
n_dict = {"Concreto": 0.014, 
          "Tierra alineada y uniforme": 0.025, 
          "Suelo expuesto": 0.032}
n = n_dict[material]

st.sidebar.info(f"Material seleccionado: **{material}**, n={n}")

# ===============================
# AYUDA TEÓRICA
# ===============================
with st.expander("📘 Ayuda teórica"):
    st.markdown("### 📐 Ecuación de Manning para canales trapezoidales")
    st.latex(r"Q = \frac{1}{n} A R^{2/3} S^{1/2}")
    st.markdown("""
**Donde:**  
- Q = caudal (m³/s)  
- A = área del canal (m²)  
- R = radio hidráulico = A / P (m)  
- P = perímetro mojado (m)  
- S = pendiente del canal (m/m)  
- n = coeficiente de rugosidad de Manning  

**Criterios:**  
- Tirante normal positivo  
- Número de Froude calculado para análisis de régimen
""")

# ===============================
# CÁLCULOS
# ===============================
# Cálculo iterativo tirante normal
y = 0.0001
cte = Q * n / (S ** 0.5)
cte_2 = 0

while cte >= cte_2:
    A = (b + z * y) * y
    P = b + 2 * y * (1 + z**2)**0.5
    R = A / P
    cte_2 = A * R**(2/3)
    y += 0.0001

y = y  # Tirante normal
A = (b + z * y) * y
V = Q / A
Froude = V / np.sqrt(9.81 * A / (b + 2*z*y))

# ===============================
# SALIDAS
# ===============================
st.header("📊 Resultados")
st.metric("Tirante normal Y (m)", f"{y:.3f}")
st.metric("Área (m²)", f"{A:.3f}")
st.metric("Velocidad (m/s)", f"{V:.3f}")
st.metric("Número de Froude", f"{Froude:.3f}")

# ===============================
# GRÁFICO DEL CANAL
# ===============================
st.header("📈 Perfil del canal trapezoidal")

x = [-b/2, b/2]  # Base
y_left = [0, y]
y_right = [0, y]

fig, ax = plt.subplots(figsize=(8,4))
# Base
ax.plot([-b/2, b/2], [0,0], color='brown', linewidth=4)
# Taludes
ax.plot([-b/2, -b/2 - z*y], [0, y], color='blue', linewidth=2)
ax.plot([b/2, b/2 + z*y], [0, y], color='blue', linewidth=2)
# Tirante
ax.hlines(y, -b/2 - z*y, b/2 + z*y, color='green', linestyle='--')
ax.set_xlabel("m")
ax.set_ylabel("m")
ax.set_title("Sección transversal – Canal trapezoidal")
ax.grid(True)
st.pyplot(fig)
fig.savefig("grafico_canal.png", dpi=150)

# ===============================
# PDF
# ===============================
st.header("📄 Exportar memoria de cálculo (1 página)")

if st.button("📥 Generar PDF"):
    pdf_file = "Canal_Trapezoidal.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    styles = getSampleStyleSheet()
    e = []

    e.append(Paragraph("<b>Diseño de canal trapezoidal</b>", styles["Title"]))
    e.append(Spacer(1,12))
    e.append(Paragraph(f"Caudal Q: {Q} m³/s", styles["Normal"]))
    e.append(Paragraph(f"Base b: {b} m", styles["Normal"]))
    e.append(Paragraph(f"Talud z: {z}", styles["Normal"]))
    e.append(Paragraph(f"Pendiente S: {S*100:.2f}%", styles["Normal"]))
    e.append(Paragraph(f"Material: {material} | n = {n}", styles["Normal"]))
    e.append(Spacer(1,12))
    e.append(Paragraph(f"Tirante normal Y = {y:.3f} m", styles["Normal"]))
    e.append(Paragraph(f"Área A = {A:.3f} m²", styles["Normal"]))
    e.append(Paragraph(f"Velocidad V = {V:.3f} m/s", styles["Normal"]))
    e.append(Paragraph(f"Número de Froude = {Froude:.3f}", styles["Normal"]))
    e.append(Spacer(1,12))
    e.append(Image("grafico_canal.png", width=14*cm, height=7*cm))

    doc.build(e)
    st.success("📄 PDF generado correctamente")
    st.download_button("⬇️ Descargar PDF", open(pdf_file, "rb"), file_name=pdf_file)
