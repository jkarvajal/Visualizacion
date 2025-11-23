# %% [markdown]
# # Bloque 1 – Importar librerías, cargar y preparar datos

# %%
# 0. Cargar librerías
import os
import pandas as pd
import numpy as np
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
# 1. Carga del conjunto de datos
# Asegurarse de que el archivo este en la ruta dada/
df = pd.read_csv("data/Student_Mental_health.csv")
print("\nDimensión Df:", df.shape)

# %%
# 2. Estandarizar nombres de columnas cambiar _ por espacios y pasar a minúsculas
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)
print("\nTipos de datos:")
df.info()

print("\nValores nulos por columna:")
print(df.isnull().sum())

# %%
# 3. Tratamiento simple de valores nulos
for col in df.columns:
    if df[col].dtype.name == "category":
        df[col] = df[col].cat.add_categories("Desconocido").fillna("Desconocido")
    elif df[col].dtype == "object":
        df[col] = df[col].fillna("Nulo")
    else:
        df[col] = df[col].fillna(df[col].median())

# %%
# 4. Eliminar duplicados
duplicates = df.duplicated().sum()
print("Duplicados encontrados:", duplicates)
df = df.drop_duplicates()

# 5. Normalizaciones específicas

# 5.1 Normalizar curso
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

# %%
# 5.2 Año de estudio
df["your_current_year_of_study"] = (
    df["your_current_year_of_study"]
    .astype(str)
    .str.lower()
    .str.replace("year", "")
    .str.strip()
    .replace({"1": "Year 1", "2": "Year 2", "3": "Year 3", "4": "Year 4"})
)

# 5.3 CGPA
df["what_is_your_cgpa?"] = df["what_is_your_cgpa?"].astype(str).str.strip()
df["what_is_your_cgpa?"] = df["what_is_your_cgpa?"].replace({
    "3.50 - 4.00": "3.50 - 4.00",
    "3.50-4.00": "3.50 - 4.00"
})

# 5.4 Convertir columnas Yes/No a 1/0
yn_cols = [
    "marital_status",
    "do_you_have_depression?",
    "do_you_have_anxiety?",
    "do_you_have_panic_attack?",
    "did_you_seek_any_specialist_for_a_treatment?"
]

for col in yn_cols:
    if col in df.columns:
        df[col] = df[col].map({"Yes": 1, "No": 0})

# 5.5 Timestamp a datetime (si existe)
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

# 5.6 Edad a entero
df["age"] = df["age"].astype(float).astype(int)

# %%
# 6. Traducción de nombres de columnas al español
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

print("\nEncabezados finales del DataFrame:")
print(df.columns)

df.head()

# %% [markdown]
# # Bloque 2. Cálculos agregados y figuras para cada parte del storytelling
# Aquí se generan las figuras siguiendo la estructura: contexto → factores académicos → personales → ayuda

# %% [markdown]
# ## Pestaña 1 Contexto: Calculos

# %%
# BLOQUE 2: Calculos agregados y figuras para cada parte del storytelling con plotly
# ______________________________________________________________________
# -------------------------------
# 2.1 Pestaña Contexto: Sección Detalle por síntoma, Gráficas: Distribución general de síntomas
# -------------------------------
# Conteos Sí/No de cada síntoma
counts_dep = df["tiene_depresion"].value_counts().sort_index()
counts_ans = df["tiene_ansiedad"].value_counts().sort_index()
counts_panic = df["tiene_ataques_panico"].value_counts().sort_index()

# Porcentajes
percent_dep = (counts_dep / counts_dep.sum() * 100).round(1)
percent_ans = (counts_ans / counts_ans.sum() * 100).round(1)
percent_panic = (counts_panic / counts_panic.sum() * 100).round(1)

# %% [markdown]
# ## Pestaña 1 Contexto: Distribución de estudiantes con síntomas de depresión

# %%
# Gráfico 1: Dispersión
# _______________________________________________________________
# Opciones de gráfica tipo barra
'''
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
fig_dep.update_yaxes(range=[0, counts_dep.max() + 7])   # Ajuste de etiquetas

# Grafico 2: Ansiedad
# _______________________________________________________________
fig_ans = px.bar(
    x=["No (0)", "Sí (1)"],
    y=counts_ans.values,
    labels={"x": "Respuesta", "y": "Cantidad de estudiantes"},
    title="Distribución de estudiantes con síntomas de ansiedad"
)
fig_ans.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_ans.values, percent_ans.values)],
    textposition="outside"
)
fig_ans.update_yaxes(range=[0, counts_ans.max() + 7])   # Ajuste de etiquetas

# Gráfico 3: Ataques de pánico
# _______________________________________________________________
fig_panic = px.bar(
    x=["No (0)", "Sí (1)"],
    y=counts_panic.values,
    labels={"x": "Respuesta", "y": "Cantidad de estudiantes"},
    title="Distribución de estudiantes con ataques de pánico"
)
fig_panic.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_panic.values, percent_panic.values)],
    textposition="outside"
)
fig_panic.update_yaxes(range=[0, counts_panic.max() + 7])   # Ajuste de etiquetas
'''
# ============================================================
# GRÁFICO 1: DEPRESIÓN (Pie)
# ============================================================
fig_dep = px.pie(
    names=["No (0)", "Sí (1)"],
    values=counts_dep.values,
    title="Distribución de estudiantes con síntomas de depresión"
)
fig_dep.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_dep.values, percent_dep.values)],
    textinfo="text+percent",  # Muestra tanto el texto personalizado como el %
    textposition="inside"
)

# %% [markdown]
# ## Pestaña 1 Contexto: Distribución de estudiantes con síntomas de ansiedad

# %%
# ============================================================
# GRÁFICO 2: ANSIEDAD (Pie)
# ============================================================
fig_ans = px.pie(
    names=["No (0)", "Sí (1)"],
    values=counts_ans.values,
    title="Distribución de estudiantes con síntomas de ansiedad"
)
fig_ans.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_ans.values, percent_ans.values)],
    textinfo="text+percent",
    textposition="inside"
)

# %% [markdown]
# ## Pestaña 1 Contexto: Distribución de estudiantes con ataques de pánico

# %%
# ============================================================
# GRÁFICO 3: ATAQUES DE PÁNICO (Pie)
# ============================================================
fig_panic = px.pie(
    names=["No (0)", "Sí (1)"],
    values=counts_panic.values,
    title="Distribución de estudiantes con ataques de pánico"
)
fig_panic.update_traces(
    text=[f"{v} ({p}%)" for v, p in zip(counts_panic.values, percent_panic.values)],
    textinfo="text+percent",
    textposition="inside"
)

# %% [markdown]
# ## Pestaña 1 Contexto: Distribución de estudiantes por síntoma emocional

# %%
# Gráfico resumen: total de casos por síntoma
counts_symptoms = pd.Series({
    "Depresión": df["tiene_depresion"].sum(),
    "Ansiedad": df["tiene_ansiedad"].sum(),
    "Ataques de pánico": df["tiene_ataques_panico"].sum()
})

# Gráfico tipo barra
'''
fig_resumen_sintomas = px.bar(
    x=counts_symptoms.index,
    y=counts_symptoms.values,
    labels={"x": "Síntoma", "y": "Número de estudiantes"},
    title="Número de estudiantes que reportan cada síntoma emocional",
    width=600,   # Ancho personalizado
    height=450   # Opcional
)
#fig_resumen_sintomas.update_traces(text=counts_symptoms.values, textposition="outside")

fig_resumen_sintomas.update_traces(
    text=counts_symptoms.values,
    textposition="outside"
)

# Ajustar espacio para que se vean los textos
fig_resumen_sintomas.update_yaxes(range=[0, counts_symptoms.max() + 7])

#fig_resumen_sintomas.show()
'''
# Gráfico tipo Pie
fig_resumen_sintomas = px.pie(
    names=counts_symptoms.index,
    values=counts_symptoms.values,
    title="Distribución de estudiantes por síntoma emocional",
    hole=0,        # Si quieres tipo doughnut, cambia a 0.4
)

# Mostrar valores y porcentajes dentro o fuera del pie
fig_resumen_sintomas.update_traces(
    textinfo="label+value+percent",
    textposition="inside"   # Usa "outside" si prefieres afuera
)

fig_resumen_sintomas.update_layout(title_x=0.5)

# fig_resumen_sintomas.show()  # En Dash no se necesita


# %% [markdown]
# # Pestaña 2 Factores Académicos
# ## Pestaña 2 Estudiantes con depresión por programa académico

# %%
# 2.2 Factores académicos
# -------------------------------

# 2.2.1 Programa académico vs Depresión
program_dep = (
    df.groupby("programa_academico")["tiene_depresion"]
    .sum()
    .sort_values(ascending=False)
)
# Filtrar solo los que son mayores que 0
program_dep = program_dep.loc[program_dep > 0]

fig_programa_dep = px.bar(
    x=program_dep.index,
    y=program_dep.values,
    labels={"x": "Programa académico", "y": "Estudiantes con depresión"},
    title="Estudiantes con depresión por programa académico"
)
fig_programa_dep.update_layout(xaxis=dict(tickangle=75))

# %%
# 2.2.2 Promedio de calificaciones vs Depresión
dep_por_cgpa = df.groupby("Promedio_de_calificaciones")["tiene_depresion"].sum().sort_index()
# Filtrar intervalos con al menos un caso
dep_por_cgpa = dep_por_cgpa[dep_por_cgpa > 0]

fig_cgpa_dep = px.bar(
    x=dep_por_cgpa.index,
    y=dep_por_cgpa.values,
    labels={"x": "Promedio de calificaciones (CGPA)", "y": "Estudiantes con depresión"},
    title="Relación entre CGPA y depresión"
)

#fig_cgpa_dep.update_layout(xaxis=dict(tickangle=360))

# %%
# 2.2.3 Año de estudio vs Ansiedad y Depresión (nueva figura)
anio_symptoms = (
    df.groupby("año_estudio")[["tiene_ansiedad", "tiene_depresion"]]
    .mean()
    .reset_index()
)

fig_anio_symptoms = px.bar(
    anio_symptoms,
    x="año_estudio",
    y=["tiene_ansiedad", "tiene_depresion"],
    barmode="group",
    labels={"value": "Proporción de estudiantes", "año_estudio": "Año de estudio", "variable": "Síntoma"},
    title="Proporción de ansiedad y depresión por año de estudio"
)


# %%
# -------------------------------
# 2.3 FACTORES PERSONALES
# -------------------------------

# 2.3.1 Género vs Ataques de pánico
panic_por_genero = df.groupby("genero")["tiene_ataques_panico"].mean().reset_index()

fig_genero_panic = px.bar(
    panic_por_genero,
    x="genero",
    y="tiene_ataques_panico",
    labels={"genero": "Género", "tiene_ataques_panico": "Proporción con ataques de pánico"},
    title="Proporción de estudiantes con ataques de pánico por género"
)



# %%
# 2.3.2 Estado civil vs Ansiedad
ans_por_estado = df.groupby("estado_civil")["tiene_ansiedad"].mean().reset_index()

fig_estado_ans = px.bar(
    ans_por_estado,
    x="estado_civil",
    y="tiene_ansiedad",
    labels={"estado_civil": "Estado civil", "tiene_ansiedad": "Proporción con ansiedad"},
    title="Proporción de estudiantes con ansiedad por estado civil"
)
fig_estado_ans



# %%
# 2.3.3 Correlaciones (Edad y síntomas)
yn_cols_esp = [
    "tiene_depresion",
    "tiene_ansiedad",
    "tiene_ataques_panico",
    "busco_tratamiento_especialista"
]
numeric_cols = ["edad"] + yn_cols_esp
corr = df[numeric_cols].corr()

# Propuesta Maria Fernanda
'''
fig_corr = px.imshow(
    corr,
    text_auto=True,
    color_continuous_scale="Oranges",
    title="Mapa de calor de correlaciones: edad, síntomas y búsqueda de tratamiento"
)
'''
fig_corr = px.imshow(
    corr,
    text_auto=".2f",               # Muestra los valores con 2 decimales
    color_continuous_scale="RdBu", # Colores rojo-azul para positiva/negativa
    title="Mapa de calor de correlaciones: edad, síntomas y búsqueda de tratamiento",
    width=700,
    height=600,
    aspect="auto"                  # Ajusta proporción de celdas
)

# Ajustes de estilo
fig_corr.update_layout(
    title_x=0.5,                   # Centrar el título
    coloraxis_colorbar=dict(
        title="Correlación",
        tickvals=[-1, -0.5, 0, 0.5, 1],
        ticktext=["-1", "-0.5", "0", "0.5", "1"]
    )
)

# Rotar etiquetas si es necesario
fig_corr.update_xaxes(tickangle=45)
fig_corr.update_yaxes(tickangle=0)

# Mostrar la figura


# %%
# -------------------------------
# 2.4 Acceso a ayuda profesional
# -------------------------------

# Proporción que busca tratamiento entre quienes SÍ tienen cada síntoma
def prop_tratamiento(cond_col):
    sub = df[df[cond_col] == 1]
    if len(sub) == 0:
        return 0
    return sub["busco_tratamiento_especialista"].mean()

help_dep = prop_tratamiento("tiene_depresion")
help_ans = prop_tratamiento("tiene_ansiedad")
help_panic = prop_tratamiento("tiene_ataques_panico")

help_data = pd.DataFrame({
    "Síntoma": ["Depresión", "Ansiedad", "Ataques de pánico"],
    "Proporción_que_busca_tratamiento": [help_dep, help_ans, help_panic]
})

fig_help_symptoms = px.bar(
    help_data,
    x="Síntoma",
    y="Proporción_que_busca_tratamiento",
    labels={"Proporción_que_busca_tratamiento": "Proporción que busca tratamiento"},
    title="Proporción de estudiantes con síntomas que buscan tratamiento especializado"
)
fig_help_symptoms.update_yaxes(tickformat=".0%")




# %%
# -------------------------------
# 2.5 INSIGHT PRINCIPAL (Clímax)
# -------------------------------

# Para el clímax usamos la misma figura, pero con título más narrativo
fig_insight = fig_help_symptoms.update_layout(
    title="Brecha entre padecer síntomas y buscar ayuda profesional"
)


# %% [markdown]
# # Bloque 3 – Layout de la app Dash con tabs narrativos
# Aquí organizamos el storytelling: cada Tab responde a una parte de la guía.

# %%
# Bloque 3: Configuración del layout de Dash con storytelling
# =============================================================================
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        "Storytelling: Salud Mental en Estudiantes Universitarios",
        style={"textAlign": "center", "marginBottom": "10px"}
    ),
    html.P(
        "Narrativa basada en el libro 'The Power of Data Storytelling' y el conjunto de datos 'Student Mental Health'.",
        style={"textAlign": "center", "marginBottom": "30px"}
    ),

    dcc.Tabs([

        # ---------------- Pestaña 1: Contexto ----------------
dcc.Tab(label="1. Contexto", children=[
    html.Br(),
    html.H2("Contexto del problema"),
    html.P(
        "En los últimos años, la salud mental ha adquirido una importancia exponencial debido al aumento "
        "de trastornos como la ansiedad o la depresión. La OMS estima que 1 de cada 7 adolescentes presenta "
        "un trastorno mental (OMS 2025). En el ámbito educativo por otro lado, diversas investigaciones "
        "señalan que la depresión puede afectar hasta al 66 % de los estudiantes universitarios y la ansiedad "
        "a más del 40 %, influyendo directamente en su concentración, rendimiento y permanencia académica. "
        "En Colombia, se calcula que el 44,7 % de los estudiantes reporta algún tipo de afectación emocional "
        "como estrés o ansiedad (El Colombiano, 2025)."
    ),
    html.P(
        "Es por lo anterior que vemos la importancia de analizar este conjunto de datos para estudiar la "
        "relación entre la vida académica y el bienestar mental de los estudiantes universitarios, con el fin "
        "de encontrar puntos clave para implementar mejoras continuas."
    ),
    
    html.H3("Descripción del conjunto de datos:"),
    html.P(
        "La información fue recopilada mediante una encuesta anónima en línea aplicada a 102 estudiantes "
        "universitarios de diversas disciplinas. Las variables incluidas son:"
    ),
    html.Ul([
        html.Li("Seleccione su género: Identidad de género del encuestado."),
        html.Li("Edad: La edad del estudiante."),
        html.Li("¿Cuál es tu curso?: Programa académico del estudiante."),
        html.Li("Año actual de estudio: Nivel académico actual."),
        html.Li("¿Cuál es su CGPA?: Promedio acumulado de calificaciones."),
        html.Li("Estado civil: Situación civil del estudiante."),
        html.Li("¿Sufre usted de depresión, ansiedad o ataques de pánico?: Síntomas reportados."),
        html.Li("¿Consultó a algún especialista para recibir tratamiento?: Búsqueda de ayuda profesional."),
    ]),

    html.H3("Resultado general:"),
    html.P("Inicialmente se observa cuántos estudiantes reportan cada uno de los trastornos mentales:"),

    html.H3("Distribución general de síntomas"),
    html.P("A continuación se muestra el porcentaje de estudiantes que reportan cada síntoma emocional:"),
    dcc.Graph(figure=fig_resumen_sintomas),

    html.P("Distribuidos de la siguiente manera:"),

    html.H4("Detalle por síntoma"),


    html.Div([
        html.Div([dcc.Graph(figure=fig_dep)], style={"width": "32%"}),
        html.Div([dcc.Graph(figure=fig_ans)], style={"width": "32%"}),
        html.Div([dcc.Graph(figure=fig_panic)], style={"width": "32%"}),
    ], style={"display": "flex", "justify-content": "space-between"}),

    html.Br(),

    html.P(
        "Se puede concluir que todos los estudiantes encuestados tenían o tuvieron algún tipo de trastorno "
        "mental, ya sea ansiedad, depresión o ataques de pánico. Las proporciones entre cada condición son "
        "muy similares, aunque la depresión presenta una ligera prevalencia del 34.3 %. Sin embargo, las "
        "diferencias no son estadísticamente significativas."
    ),
]),


        # ---------------- Pestaña 2: Factores academicos ----------------

        # ---------------- Pestaña 2: Factores académicos ----------------
        
dcc.Tab(label="2. Factores académicos", children=[
    html.Br(),
    html.H2("Factores académicos en relación a la salud mental", style={"fontWeight": "bold"}),

    # ----- INTRODUCCIÓN -----
    html.P(
        "La siguiente variable por explorar es el programa académico en relación con los estudiantes que tienen "
        "depresión. Se encuentra que priman con un 2.5 las carreras de tecnología de la información y ciencias "
        "computacionales; a continuación, se encuentran Inglés, Psicología y Educación con un 2, y con una menor "
        "cantidad se encuentran las carreras restantes de los alumnos encuestados."
    ),

    # ----- GRÁFICA 1: Estudiantes con depresión por programa -----
    html.H3("Estudiantes con depresión por programa académico"),
    dcc.Graph(figure=fig_programa_dep),

    html.Br(),

    # ----- TEXTO 2 -----
    html.P(
        "De igual forma, se toma la siguiente variable a considerar, la cual relaciona los estudiantes con "
        "depresión con el promedio de calificaciones. Podemos observar que el promedio acumulado de calificaciones, "
        "considerado una medida del rendimiento académico, oscila entre 3.0 y 3.49 con aproximadamente 17 estudiantes; "
        "contiguo a este, el rango de 3.5 a 4.0 con aproximadamente 13 estudiantes; y finalmente el rango entre "
        "2.5 y 2.9 con cerca de 3 estudiantes. Dado lo anterior, la mayoría de los estudiantes superan una media "
        "académica, sin embargo, es una calificación baja para unas expectativas académicas elevadas."
    ),

    # ----- GRÁFICA 2: CGPA y depresión -----
    html.H3("Relación entre CGPA y depresión"),
    dcc.Graph(figure=fig_cgpa_dep),

    html.Br(),

    # ----- TEXTO 3 -----
    html.P(
        "Continuando con las relaciones de las variables de depresión, anexamos la variable de ansiedad en relación "
        "al año de estudio. Podemos observar que en el tercer año se encuentra el mayor número de estudiantes con "
        "depresión y el segundo mayor número de estudiantes con ansiedad; mientras que en el segundo año se encuentra "
        "una misma cantidad de estudiantes con ansiedad y con depresión. Esto puede relacionarse a que los momentos "
        "críticos de un estudiante suelen ser antes del último año, pues se toman decisiones importantes como la "
        "modalidad y tema de grado."
    ),

    # ----- GRÁFICA 3: Año de estudio vs síntomas -----
    html.H3("Ansiedad y depresión por año de estudio"),
    dcc.Graph(figure=fig_anio_symptoms),

    html.Br(),
]),
       
        
        # ---------------- Pestaña 3: Factores personales ----------------
        dcc.Tab(label="3. Factores personales", children=[
            html.Br(),
            html.H2("Relación entre factores personales y salud mental"),
            html.P(
                "Además de las variables académicas, factores personales como el género, "
                "la edad y el estado civil pueden influir en el bienestar emocional."
            ),

            html.H3("Ataques de pánico por género"),
            html.P(
                "Esta gráfica muestra la proporción de estudiantes que reportan ataques de pánico "
                "según su género, lo que permite identificar posibles grupos más vulnerables."
            ),
            dcc.Graph(figure=fig_genero_panic),

            html.H3("Ansiedad por estado civil"),
            html.P(
                "Aquí observamos la proporción de estudiantes con ansiedad en cada categoría de estado civil. Las diferencias pueden estar relacionadas con redes de apoyo, carga familiar u otras responsabilidades."
            ),
            dcc.Graph(figure=fig_estado_ans),

            html.H3("Correlaciones entre edad, síntomas y búsqueda de tratamiento"),
            html.P(
                "El mapa de calor resume la correlación entre la edad, los síntomas emocionales y la búsqueda de tratamiento. Aunque las correlaciones no implican causalidad, ayudan a identificar relaciones lineales entre variables."
            ),
            dcc.Graph(figure=fig_corr)
        ]),

        # ---------------- Pestaña 4: Acceso a ayuda profesional ----------------
        dcc.Tab(label="4. Acceso a ayuda profesional", children=[
            html.Br(),
            html.H2("¿Los estudiantes buscan ayuda profesional?"),
            html.P(
                "Un aspecto crítico de la salud mental es la disposición a buscar apoyo profesional. "
                "A continuación se muestra qué proporción de estudiantes con síntomas reporta haber "
                "buscado tratamiento con un especialista."
            ),
            dcc.Graph(figure=fig_help_symptoms),
            html.P(
                "Podemos observar una brecha importante: aunque muchos estudiantes reportan síntomas, "
                "solo una fracción de ellos busca ayuda profesional, lo que sugiere barreras como estigmas, "
                "falta de información o acceso limitado a servicios."
            )
        ]),

        # ---------------- Pestaña 5: Insight principal (Clímax) ----------------
        dcc.Tab(label="5. Insight principal", children=[
            html.Br(),
            html.H2("Insight principal de la historia"),
            html.P(
                "El hallazgo más relevante de este análisis es la brecha entre la presencia de síntomas "
                "y la búsqueda de ayuda profesional. Una parte significativa de los estudiantes que reportan "
                "ansiedad, depresión o ataques de pánico no acude a un especialista."
            ),
            dcc.Graph(figure=fig_insight),
            html.P(
                "Este resultado sugiere que, además de identificar factores de riesgo, las instituciones "
                "deben enfocarse en derribar barreras para el acceso a servicios de apoyo psicológico y "
                "promover activamente el cuidado de la salud mental."
            )
        ]),

        # ---------------- Pestaña 6: Limitaciones ----------------
        dcc.Tab(label="6. Limitaciones del análisis", children=[
            html.Br(),
            html.H2("Limitaciones y consideraciones"),
            html.P(
                "Aunque este conjunto de datos ofrece información valiosa, es importante reconocer "
                "algunas limitaciones que afectan la interpretación de los resultados:"
            ),
            html.Ul([
                html.Li("Las respuestas son auto-reportadas y pueden incluir sesgos de percepción."),
                html.Li("La muestra no representa a todos los estudiantes universitarios ni a todas las instituciones."),
                html.Li("No se incluyen variables socioeconómicas ni antecedentes clínicos detallados."),
                html.Li("Las relaciones observadas son correlaciones, no permiten establecer causalidad."),
                html.Li("Puede existir sesgo de participación: responden más quienes tienen interés en el tema.")
            ]),
            html.P(
                "Estas limitaciones no invalidan los hallazgos, pero sí invitan a interpretarlos con cautela "
                "y a complementarlos con otros estudios cuantitativos y cualitativos."
            )
        ]),

        # ---------------- Pestaña 7: conclusión y recomendaciones ----------------
        dcc.Tab(label="7. Conclusión y recomendaciones", children=[
            html.Br(),
            html.H2("Conclusiones y recomendaciones"),
            html.P(
                "Los datos analizados muestran que la salud mental estudiantil está asociada tanto a factores "
                "académicos como personales, y que existe una brecha considerable entre el padecimiento de "
                "síntomas y la búsqueda de ayuda profesional."
            ),
            html.P(
                "A partir de estos hallazgos, se pueden plantear algunas recomendaciones para instituciones educativas "
                "y responsables de políticas de bienestar universitario:"
            ),
            html.Ul([
                html.Li("Fortalecer los programas de bienestar institucional y servicios de apoyo psicológico."),
                html.Li("Implementar campañas de sensibilización que reduzcan el estigma asociado a la salud mental."),
                html.Li("Ofrecer acompañamiento académico a estudiantes con bajo rendimiento y alta carga emocional."),
                html.Li("Diseñar rutas claras y accesibles para que los estudiantes puedan buscar ayuda a tiempo."),
                html.Li("Monitorear de manera periódica el bienestar emocional como parte de la experiencia educativa.")
            ]),
            html.P(
                "En síntesis, los datos no solo describen una realidad, sino que llaman a la acción: "
                "cuidar la salud mental de los estudiantes es fundamental para su éxito académico y su "
                "desarrollo integral."
            )
        ]),
    ])
])


# %% [markdown]
# # Bloque 4 – Ejecutar la app localmente
# En la última celda del notebook, solo necesitas:

# %%
# Bloque 4: Ejecucion local de la aplicación
# ______________________________________________________________________________
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=8050, debug=True)

#if __name__ == "__main__":
#    app.run(host="127.0.0.1", port=8050, debug=True)
    # o simplemente:
    # app.run(debug=True)



# =============================================================================
# 8. EJECUCIÓN EN RENDER
# =============================================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

















