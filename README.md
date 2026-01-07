# 🌊 Diseño Hidráulico de Canales y Alcantarillas en Flujo Nominal

Aplicación interactiva desarrollada en **Python + Streamlit** para el **cálculo hidráulico de canales trapezoidales y alcantarillas circulares** bajo condiciones de **flujo uniforme (tirante normal)**, incorporando criterios del **método HEC-22** para alcantarillas.

---

## 🎯 Objetivo

Brindar una herramienta didáctica y práctica para:

- Diseño y verificación hidráulica de **canales abiertos trapezoidales**
- Análisis de **alcantarillas circulares parcialmente llenas**
- Evaluación del régimen de flujo mediante el **número de Froude**
- Generación automática de **memorias de cálculo en PDF**

Orientado a:
- Docencia universitaria  
- Diseño preliminar hidráulico  
- Apoyo a cursos de Riego, Drenaje e Hidráulica de Canales  

---

## 🧠 Fundamento teórico

El modelo se basa en:

- **Flujo uniforme**
- **Ecuación de Manning**
- Geometría hidráulica de:
  - Canales trapezoidales
  - Alcantarillas circulares parcialmente llenas
- **Número de Froude**
- Criterios de diseño del manual **FHWA – HEC-22**

---

## ⚙️ Funcionalidades

### ✔️ Canales trapezoidales
- Cálculo del tirante normal
- Área hidráulica, perímetro mojado y radio hidráulico
- Velocidad media y régimen de flujo
- Advertencias por velocidades elevadas (riesgo de erosión)

### ✔️ Alcantarillas circulares (HEC-22)
- Flujo parcial (no se fuerza flujo lleno)
- Geometría exacta mediante ángulo central
- Advertencia cuando la alcantarilla trabaja casi llena

### ✔️ Visualización
- Gráfico de sección transversal con:
  - Etiquetas claras
  - Tirante normal
  - Geometría correcta

### ✔️ Exportación
- **Generación automática de PDF**
  - Datos de entrada
  - Resultados hidráulicos
  - Gráfico de la sección

