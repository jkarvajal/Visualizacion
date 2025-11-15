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
    style={"maxWidth": "800px", "margin": "0 auto", "fontFamily": "Arial"},
    children=[
        html.H1("Prueba de servidor Dash + Plotly", style={"textAlign": "center"}),

        html.P(
            "Selecciona la función que quieres visualizar:",
            style={"marginTop": "20px"}
        ),

        dcc.Dropdown(
            id="funcion-dropdown",
            options=[
                {"label": "sin(x)", "value": "sin(x)"},
                {"label": "cos(x)", "value": "cos(x)"},
            ],
            value="sin(x)",      # valor inicial
            clearable=False,
            style={"width": "50%"}
        ),

        dcc.Graph(
            id="grafica-funcion",
            style={"marginTop": "30px"}
        ),
    ]
)

# =========================
# 4. Callback interactivo
# =========================
@app.callback(
    Output("grafica-funcion", "figure"),
    Input("funcion-dropdown", "value")
)
def actualizar_grafica(nombre_funcion):
    fig = px.line(
        df,
        x="x",
        y=nombre_funcion,
        title=f"Gráfica de {nombre_funcion}",
        labels={"x": "x", nombre_funcion: nombre_funcion}
    )
    fig.update_layout(template="plotly_white")
    return fig

# =========================
# 5. RUN para Render
# =========================
if __name__ == "__main__":
    # Render asigna el puerto en la variable de entorno PORT
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
