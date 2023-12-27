import pandas as pd
import streamlit as st
from req import send_unique_grade
from external import do_mapa, do_mapa_final, do_mapa_final_so_parecer
from dbquery import update_document, query_rec

def to_float_grade(nota):
    try:
        return float(nota)
    except ValueError:
        return "FV"

for_index_option_at_selectbox = {
    '': 0,
    "PC": 1,
    "EP": 2,
    "PI": 3,
}

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


def recuperação(turma, df):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para essa turma")
        st.stop()
    df_to_show = df.copy()
    st.write("### ESTUDANTES EM RECUPERAÇÃO")
    df_to_show1 = df_to_show.set_index('estudante')
    df_to_show2 = df_to_show1[df_to_show1.lt(15).any(axis=1)]
    df_to_show3 = df_to_show2.mask(df_to_show2.ge(15))
    st.write(df_to_show3.fillna("~~"))
    colunas = df_to_show3.columns[df_to_show3.notna().any()]
    componente = st.selectbox("selecione o componente", colunas)
    df_to_show4 = df_to_show3[componente].dropna()
    if f'{turma}{componente}' not in st.session_state:
      df_to_showz = df_to_show4.reset_index()
      df_to_showz['matrícula'] = df_to_showz['estudante'].apply(lambda x: x.split(' - ')[1])
      search = list(query_rec(
         seleção_of_students=df_to_showz['matrícula'].to_list(), 
         componente=componente))
      if search:
        ndfs = pd.DataFrame(search)
        ndfs.index = ndfs['name'] + ' - ' + ndfs['matricula']
        ndfs['nota'] = ndfs['med']
        ndfs['compareceu'] = True
        others = pd.DataFrame([], index=df_to_show4[~df_to_show4.index.isin(ndfs.index)].index, columns=['nota', 'compareceu'])
        others['compareceu'] = False
        others['nota'] = 0.0
        ndf = pd.concat([ndfs, others], axis=0 )[['nota', 'compareceu']]
        st.session_state[f'{turma}{componente}'] = ndf
      else:
        ndf =  pd.DataFrame()
        ndf.index = df_to_show4.index
        ndf['nota'] = 0.0
        ndf['compareceu'] = False
        st.session_state[f'{turma}{componente}'] = ndf
    st.write(st.session_state[f'{turma}{componente}'])
    for student in st.session_state[f'{turma}{componente}'].index:
        se_compareceu = st.session_state[f'{turma}{componente}'].loc[student, 'compareceu']
        compareceu = st.checkbox(label=f'{student} COMPARECEU?', value=se_compareceu)
        if compareceu:
          value = st.session_state[f'{turma}{componente}'].loc[student, 'nota']
          if value == 'FV':
            value = 0.0
          new_grade = st.number_input(
              label=f'Nota de {student}', min_value=0.0, max_value=10.0,
              step=0.1, value=value
          )
          st.session_state[f'{turma}{componente}'].loc[student, 'nota'] = new_grade
          st.session_state[f'{turma}{componente}'].loc[student, 'compareceu'] = compareceu
    if st.button(label='Enviar'):
        sucesso = False
        st.write(st.session_state[f'{turma}{componente}'])
        for student in st.session_state[f'{turma}{componente}'].index:
            nota = st.session_state[f'{turma}{componente}'].loc[student, 'nota']
            compareceu = st.session_state[f'{turma}{componente}'].loc[student, 'compareceu']
            if compareceu:
                full_document = {
                    "name": student.split(" - ")[0],
                    "matricula": student.split(" - ")[1],
                    "envio_por": f"SECRETARIA: {st.session_state.prof['full_name']}",
                    "nota": to_float_grade(nota),
                    "disciplina": componente
                }
                
                if update_document(full_document):
                  st.success(f"{student} atualizado com sucesso")
                  sucesso = True
                else:
                  st.error(f"Erro ao atualizar {student}")
        if sucesso:
          del st.session_state[f'{turma}{componente}']
          st.rerun()

         
def recuperação_eja(turma, df):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para essa turma")
        st.stop()
    df_to_show = df.copy()
    st.write("### ESTUDANTES EM RECUPERAÇÃO")
    df_to_show1 = df_to_show.set_index('estudante')
    # seleciona apenas aqueles que tem conceito diferente de 'PC"
    df_to_show2 = df_to_show1[df_to_show1.ne('PC').any(axis=1)]
    df_to_show3 = df_to_show2.mask(df_to_show2.eq('PC'))
    st.write(df_to_show3.fillna("~~"))
    colunas = df_to_show3.columns[df_to_show3.notna().any()]
    componente = st.selectbox("selecione o componente", colunas)
    df_to_show4 = df_to_show3[componente].dropna()
    if f'{turma}{componente}' not in st.session_state:
      df_to_showz = df_to_show4.reset_index()
      df_to_showz['matrícula'] = df_to_showz['estudante'].apply(lambda x: x.split(' - ')[1])
      search = list(query_rec(
         seleção_of_students=df_to_showz['matrícula'].to_list(), 
         componente=componente))
      if search:
        ndfs = pd.DataFrame(search)
        ndfs.index = ndfs['name'] + ' - ' + ndfs['matricula']
        ndfs['nota'] = ndfs['med']
        ndfs['compareceu'] = True
        others = pd.DataFrame([], index=df_to_show4[~df_to_show4.index.isin(ndfs.index)].index, columns=['nota', 'compareceu'])
        others['compareceu'] = False
        others['nota'] = ''
        ndf = pd.concat([ndfs, others], axis=0 )[['nota', 'compareceu']]
        st.session_state[f'{turma}{componente}'] = ndf
      else:
        ndf =  pd.DataFrame()
        ndf.index = df_to_show4.index
        ndf['nota'] = ''
        ndf['compareceu'] = False
        st.session_state[f'{turma}{componente}'] = ndf
    st.write(st.session_state[f'{turma}{componente}'])
    for student in st.session_state[f'{turma}{componente}'].index:
        se_compareceu = st.session_state[f'{turma}{componente}'].loc[student, 'compareceu']
        compareceu = st.checkbox(label=f'{student} COMPARECEU?', value=se_compareceu)
        if compareceu:
          value = st.session_state[f'{turma}{componente}'].loc[student, 'nota']
          if value == 'FV':
            value = ''
          new_grade = st.selectbox(
              options=['', 'PC', 'EP', 'PI'],
              label=f'Nota de {student}',  index=for_index_option_at_selectbox.get(value, 0)
          )
          st.session_state[f'{turma}{componente}'].loc[student, 'nota'] = new_grade
          st.session_state[f'{turma}{componente}'].loc[student, 'compareceu'] = compareceu
    if st.button(label='Enviar'):
        sucesso = False
        st.write(st.session_state[f'{turma}{componente}'])
        for student in st.session_state[f'{turma}{componente}'].index:
            nota = st.session_state[f'{turma}{componente}'].loc[student, 'nota']
            compareceu = st.session_state[f'{turma}{componente}'].loc[student, 'compareceu']
            if compareceu:
                full_document = {
                    "name": student.split(" - ")[0],
                    "matricula": student.split(" - ")[1],
                    "envio_por": f"SECRETARIA: {st.session_state.prof['full_name']}",
                    "nota": nota,
                    "disciplina": componente
                }
                
                if update_document(full_document):
                  st.success(f"{student} atualizado com sucesso")
                  sucesso = True
                else:
                  st.error(f"Erro ao atualizar {student}")
        if sucesso:
          del st.session_state[f'{turma}{componente}']
          st.rerun()


    # bytes_data = do_mapa(df_to_show, turma=turma) 
    # if bytes_data:
    #     download_excel_file(lista=bytes_data, turma=turma, tipo='MAPA_PARCIAL')
def select_bad_grades(df):
    df_to_show1 = df.set_index('estudante')
    df_to_show2 = df_to_show1[df_to_show1.lt(15).any(axis=1)]
    return df_to_show2.mask(df_to_show2.ge(15))

def select_bad_grades_eja(df):
    df_to_show1 = df.set_index('estudante')
    df_to_show2 = df_to_show1[df_to_show1.ne('PC').any(axis=1)]
    return df_to_show2.mask(df_to_show2.eq('PC'))

def mapa_final(turma, df):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para essa turma")
        st.stop()
    df_to_show = df.copy()
    st.write("### ESTUDANTES EM RECUPERAÇÃO")
    if 'TF' in turma or 'TJ' in turma:
       df_to_show3 = select_bad_grades_eja(df_to_show)
    else:
       df_to_show3 = select_bad_grades(df_to_show)
    st.write(df_to_show3.fillna("~~"))
    colunas = df_to_show3.columns[df_to_show3.notna().any()]
    df_to_show5 = pd.DataFrame([], index=df_to_show3.index, columns=colunas)
    for componente in colunas:
      df_to_show4 = df_to_show3[componente].dropna()
      df_to_showz = df_to_show4.reset_index()
      df_to_showz['matrícula'] = df_to_showz['estudante'].apply(lambda x: x.split(' - ')[1])
      search = list(query_rec(
          seleção_of_students=df_to_showz['matrícula'].to_list(), 
          componente=componente))
      if search:
        ndfs = pd.DataFrame(search)
        ndfs.index = ndfs['name'] + ' - ' + ndfs['matricula']
        ndfs['nota'] = ndfs['med']
        ndfs['compareceu'] = True
        others = pd.DataFrame([], index=df_to_show4[~df_to_show4.index.isin(ndfs.index)].index, columns=['nota', 'compareceu'])
        others['compareceu'] = False
        others['nota'] = ''
        ndf = pd.concat([ndfs, others], axis=0 )[['nota', 'compareceu']]
        st.session_state[f'{turma}{componente}'] = ndf
      else:
        ndf =  pd.DataFrame()
        ndf.index = df_to_show4.index
        ndf['nota'] = ''
        ndf['compareceu'] = False
        st.session_state[f'{turma}{componente}'] = ndf
      df_to_show5.loc[:, componente] = ndf['nota']
    st.write(df_to_show5)
    result = [df_to_show3, df_to_show5]
    bytes_data = do_mapa_final(result, turma=turma) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='MAPA_FINAL')



def mapa_final_so_conceito(turma, df):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para essa turma")
        st.stop()
    df_to_show = df.copy()
    st.write("### ESTUDANTES EM RECUPERAÇÃO")
    if 'TF' in turma or 'TJ' in turma:
       df_to_show3 = select_bad_grades_eja(df_to_show)
    else:
       df_to_show3 = select_bad_grades(df_to_show)
    st.write(df_to_show3.fillna("~~"))
    colunas = df_to_show3.columns[df_to_show3.notna().any()]
    df_to_show5 = pd.DataFrame([], index=df_to_show3.index, columns=colunas)
    for componente in colunas:
      df_to_show4 = df_to_show3[componente].dropna()
      df_to_showz = df_to_show4.reset_index()
      df_to_showz['matrícula'] = df_to_showz['estudante'].apply(lambda x: x.split(' - ')[1])
      search = list(query_rec(
          seleção_of_students=df_to_showz['matrícula'].to_list(), 
          componente=componente))
      if search:
        ndfs = pd.DataFrame(search)
        ndfs.index = ndfs['name'] + ' - ' + ndfs['matricula']
        ndfs['nota'] = ndfs['med']
        ndfs['compareceu'] = True
        others = pd.DataFrame([], index=df_to_show4[~df_to_show4.index.isin(ndfs.index)].index, columns=['nota', 'compareceu'])
        others['compareceu'] = False
        others['nota'] = ''
        ndf = pd.concat([ndfs, others], axis=0 )[['nota', 'compareceu']]
        st.session_state[f'{turma}{componente}'] = ndf
      else:
        ndf =  pd.DataFrame()
        ndf.index = df_to_show4.index
        ndf['nota'] = ''
        ndf['compareceu'] = False
        st.session_state[f'{turma}{componente}'] = ndf
      df_to_show5.loc[:, componente] = ndf['nota']
    st.write(df_to_show5)
    result = [df_to_show3, df_to_show5]
    bytes_data = do_mapa_final_so_parecer(result, turma=turma) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='MAPA_FINAL')
