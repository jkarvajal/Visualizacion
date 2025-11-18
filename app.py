# =============================================================================
# app.py
# =============================================================================

# 1. IMPORTAR LIBRERÍAS
# =============================================================================
import os
import pandas as pd
import numpy as np

import dash
from dash import dcc, html
import plotly.express as px

# =============================================================================
# 2. CARGA DEL CONJUNTO DE DATOS
# =============================================================================
# Ruta relativa segura para Render
df_path = os.path.join(os.path.dirname(__file__), "data", "Student Mental health.csv")
df = pd.read_csv(df_path)

# =============================================================================
# 3. LIMPIEZA Y TRANSFORMACIÓN DE LOS DATOS
# =============================================================================

# 3.1 Estandarizar nombres de columnas
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# 3.2 Tratamiento de valores nulos
for col in df.columns:
    if df[col].dtype.name == "category":
        df[col] = df[col].cat.add_categories("Desconocido").fillna("Desconocido")
    elif df[col].dtype == "object":
        df[col] = df[col].fillna("Nulo")
    else:
        df[col] = df[col].fillna(df[col].median())

# 3.3 Eliminar duplicados
df = df.drop_duplicates()

# =============================================================================
# 4. NORMALIZACIÓN DE CAMPOS ESPECÍFICOS
# =============================================================================
course_map = {
    "bcs": "Computer Science",
    "bit": "Information Technology",
    "engine": "Engineering",
    "engin": "Engineering",
    "engineering": "Engineering",
    "mhsc": "Health Sciences",
    "biomedical science": "Biomedical Science",
    "koe": "Education",
    "koe ": "Education",
    "benl": "English",
    "ala": "Arts and Letters",
    "psychology": "Psychology",
    "irkhs": "Islamic Studies",
    "kirkhs": "Islamic Studies",
    "kirkhs ": "Islamic Studies",
    "islamic education": "Islamic Education",
    "pendidikan islam": "Islamic Education",
    "fiqh": "Islamic Jurisprudence",
    "fiqh fatwa": "Islamic Jurisprudence",
    "nursing": "Nursing",
    "diploma nursing": "Nursing",
    "marine science": "Marine Science",
    "banking studies": "Banking Studies",
    "mathemathics": "Mathematics",
    "communication": "Communication",
    "cts": "Computer Technology",
}

df["what_is_your_course?"] = (
    df["what_is_your_course?"]
    .astype(str)
    .str.strip()
    .str.lower()
    .replace(course_map)
)

df["your_current_year_of_study"] = (
    df["your_current_year_of_study"]
    .astype(str)
    .str.lower()
    .str.replace("year", "")
    .str.strip()
    .replace({"1": "Year 1", "2": "Year 2", "3": "Year 3", "4": "Year 4"})
)

df["what_is_your_cgpa?"] = df["what_is_your_cgpa?"].astype(str).str.strip()
df["what_is_your_cgpa?"] = df["what_is_your_cgpa?"].replace({
    "3.50 - 4.00": "3.50 - 4.00",
    "3.50-4.00": "3.50 - 4.00"
})

yn_cols = [
    "marital_status",
    "do_you_have_depression?",
    "do_you_have_anxiety?",
    "do_you_have_panic_attack?",
    "did_you_seek_any_specialist_for_a_treatment?"
]

for col in yn_cols:
    df[col] = df[col].map({"Yes": 1, "No": 0})

df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["age"] = df["age"].astype(float).astype(int)

# =============================================================================
# 5. TRADUCCIÓN DE NOMBRES DE COLUMNAS AL ESPAÑOL
# =============================================================================
column_translate = {
    "timestamp": "fecha_registro",
    "choose_your_gender": "genero",
    "age": "edad",
    "what_is_your_course?": "programa_academico",
    "your_current_year_of_study": "año_estudio",
    "what_is_your_cgpa?": "Promedio_de_calificaciones",
    "marital_status": "estado_civil",
    "do_you_have_depression?": "tiene_depresion",
    "do_you_have_anxiety?": "tiene_ansiedad",
    "do_you_have_panic_attack?": "tiene_ataques_panico",
    "did_you_seek_any_specialist_for_a_treatment?": "busco_tratamiento_especialista"
}

df = df.rename(columns=column_translate)

# =============================================================================
# 6. CREACIÓN DE FIGURAS (PLOTLY)
# =============================================================================
counts_dep = df["tiene_depresion"].value_counts().sort_index()
percent_dep = (counts_dep / counts_dep.sum() * 100).round(1)

fig_dep = px.bar(
    x=["No (0)", "Sí (1)"],
    y=counts_dep.values,
    labels={"x": "Respuesta", "y": "Cantidad de estudiantes"},
    title="Distribución de estudiantes con síntomas de depresión"
)
fig_dep.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_dep.values, percent_dep.values)],
    textposition="outside"
)
fig_dep.update_layout(yaxis=dict(title="Cantidad de estudiantes"))

counts_symptoms = pd.Series({
    "Depresión (1)": df["tiene_depresion"].sum(),
    "Ansiedad (1)": df["tiene_ansiedad"].sum(),
    "Pánico (1)": df["tiene_ataques_panico"].sum()
})

fig_tendencia = px.line(
    x=counts_symptoms.index,
    y=counts_symptoms.values,
    markers=True,
    labels={"x": "Síntoma", "y": "Número de estudiantes"},
    title="Tendencia de síntomas emocionales en estudiantes"
)
fig_tendencia.update_layout(xaxis=dict(tickangle=15))

yn_cols_esp = [
    "tiene_depresion",
    "tiene_ansiedad",
    "tiene_ataques_panico",
    "busco_tratamiento_especialista"
]
numeric_cols = ["edad"] + yn_cols_esp
corr = df[numeric_cols].corr()

fig_corr = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="Oranges",
    title="Mapa de calor de correlaciones entre síntomas emocionales y edad"
)

program_counts = df.groupby("programa_academico")["tiene_depresion"].sum().sort_values(ascending=False)
fig_programa_dep = px.bar(
    x=program_counts.index,
    y=program_counts.values,
    labels={"x": "Programa académico", "y": "Estudiantes con depresión"},
    title="Relación entre Programa Académico y Síntoma de Depresión"
)
fig_programa_dep.update_layout(xaxis=dict(tickangle=75))

dep_por_cgpa = df.groupby("Promedio_de_calificaciones")["tiene_depresion"].sum()
fig_cgpa_dep = px.bar(
    x=dep_por_cgpa.index,
    y=dep_por_cgpa.values,
    labels={"x": "Promedio de calificaciones", "y": "Estudiantes con depresión"},
    title="Relación entre Promedio de Calificaciones y Depresión"
)

ans_por_estado_civil = df.groupby("estado_civil")["tiene_ansiedad"].sum()
fig_estado_ans = px.bar(
    x=ans_por_estado_civil.index,
    y=ans_por_estado_civil.values,
    labels={"x": "Estado civil", "y": "Estudiantes con ansiedad"},
    title="Relación entre Estado Civil y Ansiedad"
)

panic_por_genero = df.groupby("genero")["tiene_ataques_panico"].sum()
fig_genero_panic = px.bar(
    x=panic_por_genero.index,
    y=panic_por_genero.values,
    labels={"x": "Género", "y": "Estudiantes con ataques de pánico"},
    title="Relación entre Género y Ataques de pánico"
)

# =============================================================================
# 7. CONFIGURACIÓN DE LA APLICACIÓN DASH
# =============================================================================
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Visualización de Salud Mental en Estudiantes",
        style={"textAlign": "center", "marginBottom": "20px"}
    ),

    dcc.Tabs([
        dcc.Tab(label="Distribución de Depresión", children=[
            html.Br(),
            html.P("Esta gráfica muestra cuántos estudiantes reportan síntomas de depresión."),
            dcc.Graph(figure=fig_dep)
        ]),
        dcc.Tab(label="Tendencia de Síntomas Emocionales", children=[
            html.Br(),
            html.P("Comparación de la cantidad de estudiantes con depresión, ansiedad y ataques de pánico."),
            dcc.Graph(figure=fig_tendencia)
        ]),
        dcc.Tab(label="Correlaciones (Edad y Síntomas)", children=[
            html.Br(),
            html.P("Mapa de calor de correlaciones entre edad, síntomas emocionales y búsqueda de tratamiento."),
            dcc.Graph(figure=fig_corr)
        ]),
        dcc.Tab(label="Programa Académico vs Depresión", children=[
            html.Br(),
            html.P("Cantidad de estudiantes con depresión por programa académico."),
            dcc.Graph(figure=fig_programa_dep)
        ]),
        dcc.Tab(label="Calificaciones vs Depresión", children=[
            html.Br(),
            html.P("Relación entre el promedio de calificaciones y los síntomas de depresión."),
            dcc.Graph(figure=fig_cgpa_dep)
        ]),
        dcc.Tab(label="Estado Civil vs Ansiedad", children=[
            html.Br(),
            html.P("Relación entre estado civil y presencia de ansiedad."),
            dcc.Graph(figure=fig_estado_ans)
        ]),
        dcc.Tab(label="Género vs Ataques de Pánico", children=[
            html.Br(),
            html.P("Relación entre género y ataques de pánico."),
            dcc.Graph(figure=fig_genero_panic)
        ]),
    ])
])

# =============================================================================
# 8. EJECUCIÓN EN RENDER
# =============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

