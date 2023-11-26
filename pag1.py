import pandas as pd
import streamlit as st
from external import do_file2_eja
from req import send_unique_grade


def send_student_grade(student_dict, prof_user_dict, main_user_admin):
    root_data = {
        "student": student_dict,
        "prof_user": prof_user_dict,
        "main_user_admin": main_user_admin
    }
    to_return = send_unique_grade(root_data)
    print(to_return)

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


def eja_func(componente, turma, data_df, prof_user, main_user_admin):

    if data_df.empty:
        st.info("Não houve nenhum lançamento de notas para esse diário")
        st.stop()
    prof_user_dict = {
        'full_name': prof_user
    }
    # PERCURSO IS THE SUM OF THE GRADES AND APPLY THE NEW MAP
    if 'I' in data_df.columns:
        data_df['I'] = data_df['I'].apply(translate_grade)
    if 'II' in data_df.columns:
        data_df['II'] = data_df['II'].apply(translate_grade)
    if 'III' in data_df.columns:
        data_df['III'] = data_df['III'].apply(translate_grade)
    to_map_df = data_df.applymap(lambda x: to_map.get(x) if x in to_map else x)
    init_value = data_df.copy()
    if 'I' in data_df.columns and 'II' in data_df.columns:
        total = 15 - to_map_df.loc[:, ['I', 'II']].fillna(0).replace('FV', 0).astype(float).sum(axis=1)
        init_value['PRECISA NA III UND.'] = total.apply(quanto_falta_func)

    if 'I' in data_df.columns and 'II' in data_df.columns and 'III' in data_df.columns:
        init_value['PERCURSO'] = to_map_df.iloc[:, 1:].fillna(0).replace('FV', 0).astype(float).sum(axis=1).map(new_map)
        init_value['status'] = init_value['PERCURSO'].map(status_map).fillna('PI')
    st.write("### TABELA DE NOTAS ORIGINAIS")
    st.write(init_value.set_index('estudante'))
    bytes_data = do_file2_eja(init_value, turma=turma, comp=componente) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='CONCEITOS_ATÉ_AGORA')
    st.divider()
    st.write("### CONSERTE OS CONCEITOS NA TABELA ABAIXO")
    result = st.data_editor(
        data_df,
        column_config={
            "I": st.column_config.SelectboxColumn(
                "I",
                help="CONCEITOS DA I UNIDADE",
                width="small",
                options=[
                    "FV",
                    "C",
                    "EC", 
                    "AC",
                    "SC"
                ],
                required=True,
            ),
            'II': st.column_config.SelectboxColumn(
                "II",
                help="CONCEITOS DA II UNIDADE",
                width="small",
                options=[
                    "FV",
                    "C",
                    "EC", 
                    "AC",
                    "SC"
                ],
                required=True,
            ),
            'III': st.column_config.SelectboxColumn(
                "III",
                help="CONCEITOS DA III UNIDADE",
                width="small",
                options=[
                    "FV",
                    "C",
                    "EC", 
                    "AC",
                    "SC"
                ],
                required=True,
            )
        },
        hide_index=True,
        disabled=['estudante']
    )
    diff = result.merge(data_df, on='estudante', suffixes=('_depois', '_antes'))
    # st.table(result)
    # st.table(diff)
    difd = {}
    for col_name in result.set_index('estudante').columns:
        difd[col_name] = diff[diff[f'{col_name}_antes'] != diff[f'{col_name}_depois']]

    if not all([dfz.empty for dfz in difd.values()]):
        my_list = []
        with st.form(key='my_form'):
            for nome_col, diff_ in difd.items():
                for idx, row in diff_.iterrows():
                    total = result.set_index(
                        'estudante'
                    ).loc[
                        row['estudante'], :
                    ].apply(
                        lambda x: to_map.get(x) 
                        if x in to_map 
                        else x
                    ).sum()
                    student_dict = {
                        'estudante': row['estudante'].split(' - ')[0],
                        'matricula': row['estudante'].split(' - ')[1],
                        'nota': to_map.get(row[f'{nome_col}_depois'], row[f'{nome_col}_depois']),
                        'disciplina': componente,
                        'unidade': nome_col,
                        'turma': turma
                    }
                    percurso = new_map.get(total)
                    my_list.append(
                        (
                            st.checkbox(
                                row['estudante'] + 
                                f"  &ensp;{nome_col} &ensp;" + 
                                str(row[f'{nome_col}_antes']) +
                                " ➡ " +
                                str(row[f'{nome_col}_depois']) +
                                "&ensp; percurso:" + f" {percurso}&ensp;" + f"&ensp; {status_map.get(percurso)}"
                                # str(sum(result.set_index('estudante').loc[row['estudante'], :].to_list()))
                            ), 
                            row,
                            student_dict
                        )
                    )
            submitted = st.form_submit_button("Enviar mudanças")
            if submitted:
                to_return_bool = False
                for i in my_list:
                    if i[0]:
                        st.success(f"###### {i[1]['estudante']} teve nota alterada no banco de dados",  icon="✅")
                        send_student_grade(i[2], prof_user_dict, main_user_admin)
                        to_return_bool = True
                    else:
                        st.error(f"###### {i[1]['estudante']} NÃO teve a nota alterada pois não foi selecionado", icon="🚨")
                if to_return_bool:
                    return True


if __name__ == "__main__":
    from dbquery import base
    turma, componente = 'TFS3NOTF2E6A - GEOGRAFIA'.split(' - ')
    data_df = pd.DataFrame(base(componente, turma))
    eja_func(componente, turma, data_df)