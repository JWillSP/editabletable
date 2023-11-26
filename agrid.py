import pandas as pd
import streamlit as st
from req import send_unique_grade
from external import do_file2


def download_excel_file(lista, turma, tipo):
  st.download_button(
    label="Baixar arquivo no formato do Excel",
    data=lista,
    file_name=f"{turma}_{tipo.replace(' ', '_')}.xlsx",
    mime=
    "application/vnd.openxmlformats-    officedocument.spreadsheetml.sheet",
  )

def send_student_grade(student_dict, prof_user_dict, main_user_admin):
    root_data = {
        "student": student_dict,
        "prof_user": prof_user_dict,
        "main_user_admin": main_user_admin
    }
    to_return = send_unique_grade(root_data)
    print(to_return)


def main_func(componente, turma, df, prof_user, main_user_admin):
    if df.empty:
        st.info("Não houve nenhum lançamento de notas para esse diário")
        st.stop()
    prof_user_dict = {
        'full_name': prof_user
    }

    df_to_show = df.copy()
    df_to_show['total'] = df.iloc[:, 1:].fillna(0).replace('FV', 0).sum(axis=1)
    df_to_show['quanto_precisa'] = df_to_show['total'].apply(lambda x: 15 - x if x < 15 else pd.NA)
    df_to_show['status'] = df_to_show['total'].apply(lambda x:  'RECUPERAÇÃO 👎' if x < 15 else 'APROVADO 👍')
    st.write("### notas originais")
    st.write(df_to_show.set_index('estudante'))
    bytes_data = do_file2(df_to_show, turma=turma, comp=componente) 
    if bytes_data:
        download_excel_file(lista=bytes_data, turma=turma, tipo='MÉDIAS_ATÉ_AGORA')

    def on_change():
        st.write(df)
        st.info("Dataframe edited")
    st.divider()
    st.write("### Conserte as notas do estudantes na tabela abaixo")

    df2 = st.data_editor(
        df,
        column_config={
            "I": st.column_config.NumberColumn(
                "I und.",
                help="Média do aluno na I unidade",
                min_value=0,
                max_value=10,
                step=0.1,
                format="%.1f",
            ),
            'II': st.column_config.NumberColumn(
                "II und.",
                help="Média do aluno na I unidade",
                min_value=0,
                max_value=10,
                step=0.1,
                format="%.1f",
            ),
            'III': st.column_config.NumberColumn(
                "III und.",
                help="Média do aluno na I unidade",
                min_value=0,
                max_value=10,
                step=0.1,
                format="%.1f",
            )
        },
        hide_index=True,
        disabled=['estudante']
    )
    diff = df2.merge(df, on='estudante', suffixes=('_depois', '_antes'))
    difd = {}
    for col_name in df2.set_index('estudante').columns:
        difd[col_name] = diff[diff[f'{col_name}_antes'] != diff[f'{col_name}_depois']]

    if not all([dfz.empty for dfz in difd.values()]):
        my_list = []
        with st.form(key='my_form'):
            for nome_col, diff_ in difd.items():
                for idx, row in diff_.iterrows():
                    total = sum(df2.set_index('estudante').loc[row['estudante'], :].to_list())
                    student_dict = {
                        'estudante': row['estudante'].split(' - ')[0],
                        'matricula': row['estudante'].split(' - ')[1],
                        'nota': row[f'{nome_col}_depois'],
                        'disciplina': componente,
                        'unidade': nome_col,
                        'turma': turma
                    }
                    my_list.append(
                        (
                            st.checkbox(
                                student_dict['estudante'] + 
                                f"  &ensp;{nome_col} und. &ensp;" + 
                                str(row[f'{nome_col}_antes']).replace('.', ',') +
                                " ➡ " +
                                str( student_dict['nota']).replace('.', ',') +
                                "&ensp; TOTAL=" + # applay format "%.1f"
                                '{}'.format(
                                    total, '.1f'
                                ).replace('.', ',') +
                                "&ensp; " +  ('RECUPERAÇÃO 👎' if total < 15 else 'APROVADO 👍')
                            ),
                            row,
                            student_dict
                        )
                    )
            submitted = st.form_submit_button("Enviar Mudanças")
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
    componente = "FISICA"
    turma = "EMMAT3B"
    df = pd.DataFrame(base(componente, turma))
    main_func(componente, turma, df)