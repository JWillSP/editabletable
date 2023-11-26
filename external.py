from openpyxl import load_workbook
import io
from turmasdetalhes import prodt, get_professor_rm


def delete_rows(ws, row):
  for i in range(row, ws.max_row + 1):
    ws.delete_rows(row)

def get_turno(turma):
  if 'NOT' in turma:
    return 'NOTURNO'
  elif 'MAT' in turma:
    return 'MATUTINO'
  elif 'VES' in turma:
    return 'VESPERTINO'
  else:
    return 'INTEGRAL 7H'


def do_file2(df, turma='', prof='', comp='comp.: '):
  lista = [x[1].to_dict() for x in df.iterrows()]
  wb = load_workbook(filename='./statics/MEDIASTODASUNIDADES.xlsx')
  ws = wb.active
  turno = get_turno(turma)
  if prof:
    nome_rm = prodt[1]
    matrícula = nome_rm.get(prof)
    pro_nome = prodt[0].get(matrícula)
  else:
    pro_nome = get_professor_rm(turma, comp)
  ws['A3'] = turma + ' - ' + turno
  ws['A4'] = pro_nome
  ws['G4'] = comp
  start_row = 6
  num_rows = start_row + len(lista)
  for i, item in enumerate(lista):
    estudante  = item.get("estudante").split(' - ')[0]
    I = item.get("I")
    II = item.get("II")
    III = item.get("III")
    row = start_row + i
    ws.cell(row=row, column=1).value = estudante
    ws.cell(row=row, column=2).value = I
    ws.cell(row=row, column=3).value = II
    ws.cell(row=row, column=4).value = III



  delete_rows(ws=ws, row=num_rows + 1)
  buffer = io.BytesIO()
  wb.save(buffer)
  bytes_data = buffer.getvalue()
  buffer.close()
  return bytes_data


def do_file2_eja(df, turma='', prof='', comp='comp.: '):
  lista = [x[1].to_dict() for x in df.iterrows()]
  wb = load_workbook(filename='./statics/MEDIASTODASUNIDADES_EJA.xlsx')
  ws = wb.active
  turno = get_turno(turma)
  if prof:
    nome_rm = prodt[1]
    matrícula = nome_rm.get(prof)
    pro_nome = prodt[0].get(matrícula)
  else:
    pro_nome =get_professor_rm(turma, comp)
  ws['A3'] = turma + ' - ' + turno
  ws['A4'] = pro_nome
  ws['E4'] = comp
  start_row = 6
  num_rows = start_row + len(lista)
  for i, item in enumerate(lista):
    estudante  = item.get("estudante").split(' - ')[0]
    I = item.get("I")
    II = item.get("II")
    III = item.get("III")
    PERCURSO = item.get("PERCURSO")
    quanto_precisa = item.get('PRECISA NA III UND.')
    row = start_row + i
    ws.cell(row=row, column=1).value = estudante
    ws.cell(row=row, column=2).value = I
    ws.cell(row=row, column=3).value = II
    ws.cell(row=row, column=4).value = quanto_precisa
    ws.cell(row=row, column=5).value = III
    ws.cell(row=row, column=6).value = PERCURSO


  delete_rows(ws=ws, row=num_rows + 1)
  buffer = io.BytesIO()
  wb.save(buffer)
  bytes_data = buffer.getvalue()
  buffer.close()
  return bytes_data