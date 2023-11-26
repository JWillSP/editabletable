from datetime import  datetime
from pydantic import BaseModel, Field
from typing import Union
import uuid
from pymongo import MongoClient
import streamlit as st

try:
    dbcred = st.secrets["dbcred"]
    db1 = st.secrets["db1"]
    lg = st.secrets["lg"]
except FileNotFoundError:
    import os
    dbcred = os.environ['dbcred']
    db1 = os.environ["db1"]
    lg = os.environ["lg"]


client = MongoClient(dbcred)
db = client[db1]

def date_to_uuid():
    uuid_obj = uuid.uuid5(uuid.NAMESPACE_URL, str(datetime.utcnow()))
    return str(uuid_obj)

def iso_format():
    return datetime.now().isoformat()

class UniqueGradeModel(BaseModel):
    name: str = Field(..., alias="name")
    created_at: str = Field(default_factory=iso_format)
    matricula: str = Field(..., alias="matricula")
    unidade: str = Field(..., alias="unidade")
    disciplina: str = Field(..., alias="disciplina")
    nota: Union[float, str] = Field(..., alias="nota")
    professor: str = Field(..., alias="professor")


def receive_unique_grade_on_db(
    sub
):
    unique_grade: UniqueGradeModel = UniqueGradeModel(**sub)
    nota = unique_grade.model_dump()
    nota['_id'] = date_to_uuid()
    created_at = nota['created_at']
    partículas = created_at.split('-')
    if len(partículas) == 3:
        year = partículas[0]
    else:
        year = ''
    if (
        unique_grade_response := db[f"{year}{lg}"].insert_one(nota)
    ) is not None:
        created_unique_grade = db[f"{year}{lg}"].find_one({"_id": unique_grade_response.inserted_id})
        return created_unique_grade


def send_unique_grade(root_data):
    list_keys = ['matricula', 'unidade', 'disciplina', 'nota']
    data_at_work = root_data['student']
    submission = {k:v for k, v in data_at_work.items() if k in list_keys}
    prof_data = root_data['prof_user']
    if admin_name := root_data.get("main_user_admin", None):
        responsável = f'SECRETARIA, por {admin_name}'
    else:
        responsável = prof_data['full_name']
    submission['professor'] = responsável
    submission['name'] = data_at_work.get("estudante", '')
    return receive_unique_grade_on_db(submission)



