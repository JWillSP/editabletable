import pandas as pd
import streamlit as st
from req import send_unique_grade
from external import do_mapa


def download_excel_file(lista, turma, tipo):
  st.download_button(
    label="Baixar arquivo no formato do Excel",
    data=lista,
    file_name=f"{turma}_{tipo.replace(' ', '_')}.xlsx",
    mime=
    "application/vnd.openxmlformats-    officedocument.spreadsheetml.sheet",
  )

def main_func(turma, df):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para essa turma")
        st.stop()

    df_to_show = df.copy()

    st.write("### notas originais")
    st.write(df_to_show.set_index('estudante'))
    bytes_data = do_mapa(df_to_show, turma=turma) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='MAPA_PARCIAL')

