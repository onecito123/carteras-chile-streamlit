import pandas as pd
import streamlit as st

import os
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Consolidador de Acciones", page_icon="📈")

# Título de la aplicación
st.title("Consolidador de Precios de Acciones Chilenas")

# 1. Widgets para ingresar fechas
col1, col2 = st.columns(2)
with col1:
    fecha_inicio = st.text_input("Fecha de inicio (YYYY-MM-DD)", "2024-04-17")
with col2:
    fecha_fin = st.text_input("Fecha de fin (YYYY-MM-DD)", "2025-04-17")

# 2. Widget para subir archivos CSV
archivos_csv = st.file_uploader("Sube tus archivos CSV de acciones", 
                              type="csv",
                              accept_multiple_files=True)

if archivos_csv and fecha_inicio and fecha_fin:
    try:
        # Crear rango de fechas
        date_range = pd.date_range(fecha_inicio, fecha_fin, freq='D')
        df_final = pd.DataFrame(index=date_range)
        df_final.index.name = 'Fecha'

        # Procesar cada archivo
        for archivo in archivos_csv:
            nombre_accion = os.path.splitext(archivo.name)[0]
            
            # Leer CSV
            try:
                df = pd.read_csv(
                    archivo,
                    usecols=[0, 1],
                    header=0,
                    parse_dates=[0],
                    encoding='latin-1',
                    dayfirst=True,
                    thousands='.',
                    decimal=','
                )
            except UnicodeDecodeError:
                df = pd.read_csv(
                    archivo,
                    usecols=[0, 1],
                    header=0,
                    parse_dates=[0],
                    encoding='utf-8',
                    dayfirst=True,
                    thousands='.',
                    decimal=','
                )
            
            # Limpiar datos
            df.columns = ['Fecha', nombre_accion]
            df = df.dropna().drop_duplicates('Fecha').set_index('Fecha')
            df_final = df_final.join(df, how='left')

        # 3. Procesamiento final
        df_final['Fin_de_semana'] = df_final.index.dayofweek.isin([5, 6])
        df_final = df_final.ffill().sort_index(axis=1)

        # 4. Mostrar previsualización
        st.subheader("Vista Previa de Datos")
        st.dataframe(df_final.head(10))

        # 5. Botón de descarga
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_final.to_excel(writer)
        
        st.download_button(
            label="Descargar Excel consolidado",
            data=output.getvalue(),
            file_name="acciones_consolidadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.info("⚠️ Por favor sube los archivos CSV e ingresa las fechas")