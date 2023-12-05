# import MongoClient
import streamlit as st

try:
    dbcred = st.secrets["dbcred"]
    db1 = st.secrets["db1"]
    stds_col = st.secrets["alunos"]
    idvmeds = st.secrets["idvmeds"]
except FileNotFoundError:
    import os
    dbcred = os.environ['dbcred']
    db1 = os.environ["db1"]
    stds_col = os.environ["alunos"]
    idvmeds = os.environ["idvmeds"]


def base(componente, turma):
    from pymongo import MongoClient
    client = MongoClient(dbcred)
    db = client[db1]
    alunos  = db[stds_col]
    estudantes = list(alunos.find({"turma": turma}))
    query =   {
        'componente': componente,
        'matrícula': {"$in": [estudante['matrícula'] for estudante in estudantes]}
        }
    def show_performance_query_result(query_):
        return db[idvmeds].find(query, {"_id": 0})   

    coro = list(show_performance_query_result(query))
    import pandas as pd
    df = pd.DataFrame(coro)
    def norm(string):
    # take off all latim accents like á, ã, ç, etc
        import unicodedata
        return unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')
    if df.empty:
        return df
    df = df[['matrícula', 'name', 'med', 'unidade']]
    df = df.replace('FV', 0)
    df['med'] = df['med'].astype(float)
    pivot = pd.pivot_table(df, index='matrícula', columns='unidade', values='med')
    # pivot['total'] = pivot.fillna(0).replace('FV', 0).sum(axis=1)
    new_index = pivot.index.map(
        {
            estudante['matrícula']:  
            norm(estudante['estudante']) +
            ' - ' + 
            estudante['matrícula']
            for estudante in estudantes
        }
    )
    pivot['estudante'] = new_index
    pivot = pivot.sort_values(by=['estudante'])
    # put estudante column in the first column
    cols = list(pivot.columns)
    cols = [cols[-1]] + cols[:-1]
    pivot = pivot[cols]

    return pivot



