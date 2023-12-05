import pandas as pd
import streamlit as st
from external import do_mapa
from req import send_unique_grade


def download_excel_file(lista, turma, tipo):
  st.download_button(
    label="Baixar arquivo no formato do Excel",
    data=lista,
    file_name=f"{turma}_{tipo.replace(' ', '_')}.xlsx",
    mime=
    "application/vnd.openxmlformats-    officedocument.spreadsheetml.sheet",
  )

def cf1(value):
    data = str(value).replace(',', '.')
    try:
        number = float(data)
    except ValueError:
        return 'FV'
    if 0 <= number <= 10:
        if number == 0: return '0'
        if number <= 3.5: return '3.5'
        if number <= 4.9: return '4.5'
        if number <= 10: return '7.5'
    else:
        return 'FV'

def translate_grade(value):
    value = cf1(value)
    if value == 'FV': return 'FV'
    if value == '0': return 'SC'
    if value == '3.5': return 'AC'
    if value == '4.5': return 'EC'
    if value == '7.5': return 'C'

to_map = {
    'SC': 0,
    'AC': 3.5,
    'EC': 4.5, 
    'C': 7.5
}

new_map = {
    0.0:  'PI',
    3.5:  'PI',
    4.5:  'PI',
    7.5:  'PI',
    7.0:  'PI',
    8.0:  'PI',
    11.0: 'EP',
    9.0:  'PI',
    12.0: 'EP',
    15.0: 'PC',
    10.5: 'EP',
    11.5: 'EP',
    14.5: 'EP',
    12.5: 'EP',
    15.5: 'PC',
    18.5: 'PC',
    13.5: 'EP',
    16.5: 'PC',
    19.5: 'PC',
    22.5: 'PC'
}

status_map = {'PI': 'REPROVADO ❌', 'EP': 'RECUPERAÇÃO 👎', 'PC': 'APROVADO 👍'}


def quanto_falta_func(value):
    data = str(value).replace(',', '.')
    try:
        number = float(data)
    except ValueError:
        return '?'
    if 0 <= number <= 7.5:
        if number == 0: return 'NADA ✅'
        if number <= 3.5: return 'AC'
        if number <= 4.5: return 'EC'
        if number <= 7.5: return 'C'
    else:
        return 'INALCANÇÁVEL ❌'


def process_in_eja(data_df):
    if data_df.empty:
        st.info("Não houve nenhum lançamento de notas para esse diário")
        st.stop()
    if 'I' in data_df.columns:
        data_df['I'] = data_df['I'].apply(translate_grade)
    if 'II' in data_df.columns:
        data_df['II'] = data_df['II'].apply(translate_grade)
    if 'III' in data_df.columns:
        data_df['III'] = data_df['III'].apply(translate_grade)
    to_map_df = data_df.applymap(lambda x: to_map.get(x) if x in to_map else x)
    return to_map_df.iloc[:, 1:].fillna(0).replace('FV', 0).astype(float).sum(axis=1).map(new_map)

def eja_func(turma, init_value):


    st.write("### TABELA DE NOTAS ORIGINAIS")
    st.write(init_value.set_index('estudante'))
    bytes_data = do_mapa(init_value, turma=turma) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='MAPA_PARCIAL_EJA')
    