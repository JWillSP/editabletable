import streamlit as st
from pymongo import MongoClient
import datetime
from sec import verify_password, assinado_rm, create_secret_key
import pandas as pd
from dbquery import base

st.set_page_config(
    page_title="Correções de notas",
    page_icon="📝"
)
st.sidebar.image("CETI_TRANS.png")
st.sidebar.image("CEDI_2.png")

def get_date_of_today():
    date_of_today = datetime.datetime.now() - datetime.timedelta(hours=3)
    return date_of_today

def get_date_obj(date_str):
    return datetime.datetime.strptime(date_str, "%d/%m/%Y")

def get_date_str(date_obj):
    return date_obj.strftime("%d/%m/%Y")

try:
    dbcred = st.secrets["dbcred"]
    db1 = st.secrets["db1"]
    users = st.secrets["users"]
    ag = st.secrets["ag"]
    sc = st.secrets["sc"]
    stds_col = st.secrets["alunos"]
except FileNotFoundError:
    import os
    dbcred = os.environ['dbcred']
    db1 = os.environ["db1"]
    users = os.environ["users"]
    ag = os.environ["ag"]
    sc = os.environ["sc"]
    stds_col = os.environ["alunos"]

def put_uuid(text):
    if text:
        return text + " - " + assinado_rm(st.session_state.sk, text)  
    return ''

client = MongoClient(dbcred)  # Substitua pela URL do seu banco de dados MongoDB
db = client[db1]
collection = db[ag]
HORAS_NUMBER = 10

if 'novo' not in st.session_state:
    st.session_state.novo = st.empty()

def is_in_time():
    try: 
        st.session_state.prof['last_time_used']
    except AttributeError:
        return False
    last_time_used = st.session_state.prof['last_time_used']
    if (datetime.datetime.now() - last_time_used).total_seconds() > HORAS_NUMBER*60:
        for key in st.session_state.keys():
            del st.session_state[key]
        st.write("Sessão expirada")
        if st.button("relogar"):
            st.rerun()
    else:
        st.session_state.prof['last_time_used'] = datetime.datetime.now()
        return True


def pipe_eja(df):
    from pag1_mapa_parcial import process_in_eja
    return process_in_eja(df)

def pipe_reg(df):
    return df.iloc[:, 1:].fillna(0).replace('FV', 0).sum(axis=1)

def main(nnovo):
    if is_in_time():
        nnovo.empty()
        st.write(f"Olá, {st.session_state.prof['full_name']}")
        username = st.session_state.prof['username']
        if st.button("sair"):
            del st.session_state.prof
            st.rerun()
        if st.session_state.prof['isAdmin']:
            all_turmas = db['META'].find_one({'_id': stds_col}).get('matriz', {})
            all_keys = [turma for turma in all_turmas ]
            turma = st.selectbox("selecione a turma", ['-- selecione --']+ sorted(all_keys))
            if turma != '-- selecione --':
                if 'TF' in turma or 'TJ' in turma:
                    pipe = pipe_eja
                else:
                    pipe = pipe_reg
                componentes = sorted(all_turmas.get(turma, []))

                df_totais = pd.DataFrame()
                for componente in componentes:
                    seleção = f'{turma} - {componente}'
                    if seleção not in st.session_state:
                        print('setando base')
                        st.session_state[seleção] = base(componente, turma)
                    else:
                        print('usando base')
                    data_df = pd.DataFrame(st.session_state[seleção])
                    df_totais = pd.concat(
                        [
                            df_totais,
                            pd.DataFrame(
                                pipe(data_df),
                                columns=[componente]
                            )
                        ],
                        axis=1
                    )
                else:
                    df_totais['estudante'] = data_df['estudante']
                if 'TF' in turma or 'TJ' in turma:
                    from pag1_mapa_parcial import eja_func as main_func

                else:
                    from agrid_mapa_parcial import main_func

                to_receive = main_func(
                    turma,
                    df_totais,
                )
                if to_receive:
                    del st.session_state[seleção]
                    print('deletando base')
                    st.rerun()
        else:
            st.error("Você não tem permissão para acessar essa página")

if "prof" not in st.session_state:
    login_page = st.session_state.novo.container()
    login_page.title("faça login")
    with st.form("login_form"):
        username = st.text_input("usuário").strip()
        password = st.text_input("senha", type="password").strip()
        if st.form_submit_button("login"):
            prof_db = db[users]
            prof = prof_db.find_one({"username": username})
            if verify_password(password, prof['hashed_password']):
                st.session_state.prof = {k:v for k, v in prof.items() if k != "_id"}
                # include last_time_used in prof to mesure the time of inactivity
                st.session_state.prof['last_time_used'] = datetime.datetime.now()
                st.session_state.sk = create_secret_key()
            else:
                st.error("senha incorreta")

main(st.session_state.novo)