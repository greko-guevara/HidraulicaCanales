import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

# ===============================
# Constantes
# ===============================
g = 9.81

# ===============================
# Configuración Streamlit
# ===============================
st.set_page_config(
    page_title="Canales y Alcantarillas – Flujo Nominal",
    layout="wide"
)

st.title("🌊 Diseño hidráulico en flujo nominal")
st.markdown(
    "**Canales trapezoidales y alcantarillas circulares**  \n"
    "Prof. Gregory Guevara — Riego & Drenaje / Universidad EARTH"
)




# ===============================
# Sidebar – Tipo de sección
# ===============================
st.sidebar.header("📐 Tipo de sección")
seccion = st.sidebar.selectbox(
    "Seleccione la sección hidráulica",
    ["Canal trapezoidal", "Alcantarilla circular"]
)



# ===============================
# Entradas comunes
# ===============================
st.sidebar.header("🔧 Parámetros hidráulicos")
Q = st.sidebar.number_input("Caudal Q (m³/s)", min_value=0.01, value=1.0, step=0.01)
S = st.sidebar.number_input("Pendiente S (%)", min_value=0.01, value=0.5, step=0.01)

# ===============================
# Material (con restricciones)
# ===============================
if seccion == "Canal trapezoidal":
    material = st.sidebar.selectbox(
        "Material del canal",
        ["Concreto 0.014", "Plástico (PVC / PEAD) 0.011","Tierra uniforme 0.025", "Suelo expuesto 0.032"]
    )
else:
    material = st.sidebar.selectbox(
        "Material de la alcantarilla",
        ["Concreto", "Plástico (PVC / PEAD)"]
    )

if material == "Concreto 0.014":
    n = 0.014
elif "Plástico (PVC / PEAD)" in material:
    n = 0.011
elif material == "Tierra uniforme 0.025":
    n = 0.025
else:
    n = 0.032


# ===============================
# Ayuda teórica
# ===============================
with st.expander("📘 Ayuda teórica"):
    st.markdown("### 🔹 Flujo uniforme (tirante normal)")
    st.markdown("""
    El **tirante normal** corresponde a una condición de **flujo uniforme**, donde:
    - La pendiente del fondo del canal es igual a la pendiente de la línea de energía.
    - La profundidad del flujo permanece constante a lo largo del canal.
    """)

    st.markdown("### 🔹 Ecuación de Manning")
    st.latex(r"""
    Q = \frac{1}{n} \, A \, R^{2/3} \, S^{1/2}
    """)
    st.markdown("""
    Donde:
    - **Q**: caudal (m³/s)  
    - **n**: coeficiente de rugosidad de Manning  
    - **A**: área hidráulica (m²)  
    - **R**: radio hidráulico (A/P)  
    - **S**: pendiente del canal (m/m)
    """)

    st.markdown("### 🔹 Geometría hidráulica")
    if seccion == "Canal trapezoidal":
        st.latex(r"""
        A = y (b + z y)
        """)
        st.latex(r"""
        P = b + 2y\sqrt{1+z^2}
        """)
        st.latex(r"""
        T = b + 2zy
        """)
        st.markdown("""
        Donde:
        - **b**: base del canal (m)  
        - **z**: talud lateral (H/V)  
        - **y**: tirante normal (m)
        """)
    else:
        st.latex(r"""
        A = \frac{D^2}{8}(\theta - \sin\theta)
        """)
        st.latex(r"""
        P = \frac{D}{2}\theta
        """)
        st.markdown("""
        Para alcantarillas circulares:
        - El cálculo se realiza para **flujo parcial**.
        - El ángulo central **θ** depende del tirante y el diámetro.
        """)

    st.markdown("### 🔹 Número de Froude")
    st.latex(r"""
    Fr = \frac{V}{\sqrt{g \cdot \frac{A}{T}}}
    """)
    st.markdown("""
    Interpretación:
    - **Fr < 1** → flujo subcrítico  
    - **Fr = 1** → flujo crítico  
    - **Fr > 1** → flujo supercrítico
    """)




# ===============================
# Funciones hidráulicas
# ===============================
def canal_trapezoidal(Q, b, z, S, n):
    dy = 0.001
    y = dy
    for _ in range(100000):
        A = (b + z*y) * y
        P = b + 2*y*np.sqrt(1 + z**2)
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5
        if A * V >= Q:
            break
        y += dy
    T = b + 2*z*y
    Fr = V / np.sqrt(g * A / T)
    return y, A, P, R, V, Fr

def alcantarilla_circular(Q, D, S, n):
    dy = 0.001
    y = dy
    dy = 0.001
    y = dy
    max_iter = 100000
    for _ in range(max_iter):
        A = np.pi * (y/2)**2
        P = np.pi * y
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5  # Manning
        Q_calc = A * V
        if Q_calc >= Q:
            break
        y += dy
    Fr = V / np.sqrt(g*A/D)
 
    return y, A, P, R, V, Fr,

# ===============================
# Cálculo
# ===============================
if seccion == "Canal trapezoidal":
    b = st.sidebar.number_input("Base b (m)", min_value=0.1, value=0.5)
    z = st.sidebar.number_input("Talud z (H/V)", min_value=0.0, value=1.0)
    y, A, P, R, V, Fr = canal_trapezoidal(Q, b, z, S, n)

    fig, ax = plt.subplots(figsize=(6,6))
    ax.plot([-b/2, b/2], [0,0], linewidth=4, label="Base")
    ax.plot([-b/2, -b/2 - z*y], [0,y], label="Talud izquierdo")
    ax.plot([b/2, b/2 + z*y], [0,y], label="Talud derecho")
    ax.hlines(y, -b/2 - z*y, b/2 + z*y, linestyles="--", label="Tirante normal")
    ax.set_title("Sección transversal – Canal trapezoidal")
    ax.set_aspect("equal")
    ax.legend()
    ax.grid(True, linestyle=":")
else:
    D = st.sidebar.number_input("Diámetro D (m)", min_value=0.2, value=1.0)
    y, A, P, R, V, Fr = alcantarilla_circular(Q, D, S, n)

    fig, ax = plt.subplots(figsize=(4,4))
    circle = plt.Circle((D/2,D/2), D/2, fill=False, linewidth=2, label="Alcantarilla")
    ax.add_patch(circle)
    ax.hlines(y, 0, D, linestyles="--", label="Tirante normal")
    ax.set_title("Sección transversal – Alcantarilla circular")
    ax.set_aspect("equal")
    ax.legend()
    ax.grid(True, linestyle=":")

fig.savefig("seccion.png", dpi=150)
st.pyplot(fig)

# ===============================
# Resultados
# ===============================
st.header("📊 Resultados hidráulicos")

col1, col2 = st.columns(2)
with col1:
    st.metric("Tirante normal y (m)", round(y,3))
    st.metric("Área A (m²)", round(A,3))
with col2:
    st.metric("Velocidad V (m/s)", round(V,3))
    st.metric("Número de Froude", round(Fr,3))

st.write(f"**Perímetro mojado P:** {round(P,3)} m")
st.write(f"**Radio hidráulico R:** {round(R,3)} m")

if Fr < 1:
    regimen = "Subcrítico"
elif Fr == 1:
    regimen = "Crítico"
else:
    regimen = "Supercrítico"

st.info(f"🟢 Régimen del flujo: **{regimen}**")


if seccion == "Canal trapezoidal" and V > 2.5:
    st.warning("⚠️ Velocidad elevada: riesgo de erosión del canal.")

if seccion == "Alcantarilla circular" and y/D > 0.9:
    st.warning("⚠️ Alcantarilla trabajando casi llena.")


# ===============================
# PDF
# ===============================
st.header("📄 Exportar memoria de cálculo")

if st.button("📥 Generar PDF"):
    pdf = "Memoria_Hidraulica.pdf"
    doc = SimpleDocTemplate(pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    e = []

    e.append(Paragraph("<b>Memoria de cálculo hidráulico – Flujo nominal</b>", styles["Title"]))
    e.append(Paragraph("Universidad EARTH | Riego & Drenaje", styles["Heading4"]))
    e.append(Paragraph(f"Tipo de sección: {seccion}", styles["Normal"]))
    e.append(Paragraph(f"Material: {material}", styles["Normal"]))
    e.append(Paragraph(f"Caudal Q = {Q} m³/s | Pendiente S = {S} %", styles["Normal"]))
    if seccion == "Canal trapezoidal":
        e.append(Paragraph(f"Base b = {b} m | Taluz Z = {z} %", styles["Normal"]))    
    else:
        e.append(Paragraph(f"Diámetro D = {D} m" , styles["Normal"]))    

    e.append(Spacer(1,6))

    table = Table([
        ["y (m)", "A (m²)", "V (m/s)", "Fr", "P (m)", "R (m)"],
        [round(y,3), round(A,3), round(V,3), round(Fr,3), round(P,3), round(R,3)]
    ])
    e.append(table)
    e.append(Spacer(1,10))
    e.append(Image("seccion.png", width=14*cm, height=14*cm))

    doc.build(e)
    st.success("PDF generado correctamente")
    st.download_button("⬇️ Descargar PDF", open(pdf,"rb"), file_name=pdf)
