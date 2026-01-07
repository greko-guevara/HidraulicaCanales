import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Constantes
# ===============================
g = 9.81  # gravedad

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

# ===============================
# FUNCIONES HIDRÁULICAS
# ===============================
def canal_trapezoidal(Q, b, z, S, n):
    dy = 0.001
    y = dy
    for _ in range(100000):
        A = (b + z*y) * y
        P = b + 2*y*np.sqrt(1 + z**2)
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5
        Q_calc = A * V
        if Q_calc >= Q:
            break
        y += dy
    T = b + 2*z*y
    Fr = V / np.sqrt(g * A / T)
    return y, A, P, R, V, Fr

def alcantarilla_circular(Q, D, S, n):
    dy = 0.001
    y = dy
    for _ in range(100000):
        if y >= D:
            y = D
            break
        theta = 2 * np.arccos(1 - 2*y/D)
        A = (D**2 / 8) * (theta - np.sin(theta))
        P = (D / 2) * theta
        R = A / P
        V = (1/n) * R**(2/3) * (S/100)**0.5
        Q_calc = A * V
        if Q_calc >= Q:
            break
        y += dy
    T = D * np.sin(theta/2)
    Fr = V / np.sqrt(g * A / T)
    return y, A, P, R, V, Fr

# ===============================
# CÁLCULO SEGÚN SECCIÓN
# ===============================
if seccion == "Canal trapezoidal":

    st.sidebar.header("📏 Geometría del canal")
    b = st.sidebar.number_input("Base b (m)", min_value=0.1, value=0.5)
    z = st.sidebar.number_input("Talud z (H/V)", min_value=0.0, value=1.0)

    y, A, P, R, V, Fr = canal_trapezoidal(Q, b, z, S, n)

    # Gráfico
    fig, ax = plt.subplots(figsize=(7,4))
    ax.plot([-b/2, b/2], [0,0], color='brown', linewidth=4)
    ax.plot([-b/2, -b/2 - z*y], [0, y], 'b')
    ax.plot([b/2, b/2 + z*y], [0, y], 'b')
    ax.hlines(y, -b/2 - z*y, b/2 + z*y, colors='green', linestyles='--')
    ax.set_aspect('equal')
    ax.set_title("Sección trapezoidal")
    ax.grid(True, linestyle=":")

else:

    st.sidebar.header("📏 Geometría de la alcantarilla")
    D = st.sidebar.number_input("Diámetro D (m)", min_value=0.2, value=1.0)

    y, A, P, R, V, Fr = alcantarilla_circular(Q, D, S, n)

    # Gráfico
    fig, ax = plt.subplots(figsize=(6,4))
    circle = plt.Circle((D/2, D/2), D/2, fill=False, linewidth=2)
    ax.add_patch(circle)
    ax.hlines(y, 0, D, colors='green', linestyles='--')
    ax.set_aspect('equal')
    ax.set_title("Sección circular")
    ax.grid(True, linestyle=":")

# ===============================
# RESULTADOS
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

st.pyplot(fig)
