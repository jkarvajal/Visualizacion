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
df_path = os.path.join(os.path.dirname(__file__), "data", "Student_Mental_health.csv")
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
