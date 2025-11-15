import os
import numpy as np
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# =========================
# 1. Datos de ejemplo
# =========================
x = np.linspace(0, 10, 200)
df = pd.DataFrame({
    "x": x,
    "sin(x)": np.sin(x),
    "cos(x)": np.cos(x),
})

# =========================
# 2. Inicializar la app
# =========================
app = dash.Dash(__name__)
server = app.server  # útil para algunos hostings, no estorba en Render

# =========================
# 3. Layout (interfaz)
# =========================
app.layout = html.Div(
