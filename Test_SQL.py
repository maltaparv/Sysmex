import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const
from Parsing import parse_xn350, record

def sql_insert(str_sql: str) -> int:
    """ Запись в MS SQL одного результата от анализатора
    :type str_sql: str
    """
    try:
        conn = pyodbc.connect(const.sql_run)
        cursor = conn.cursor()
        write_log(str_sql)
        cursor.execute('set dateformat ymd;')
        cursor.execute(str_sql)
        conn.commit()
    except Exception as e:
        write_log("ERR Ошибка при записи SQL. " + str(e))
        write_errlog("ERR Ошибка при записи SQL.", str(e))
        return -1
    return 0

print('Test_SQL')
fn_ini = 'sysmex.ini'
read_ini(fn_ini)

cnt_max = 22  # (ограничение кол-ва полей в LabAutoResult)
result_text = 'тест22 Sysmex XN-350 '

# record.an = [an_no, an_name, an_res, an_ed, an_flag, an_time]  # current record with one result
record.__init__()  # при получении данных - "обнулить" всё
record.history_number = 72022

str_start = 'INSERT INTO [LabAutoResult].[dbo].[AnalyzerResults](Analyzer_Id, HistoryNumber'
str_tail = f')Values({const.analyser_id}, {record.history_number}'

record.list_research.append([1, 'WBC', '5,55', '10*3/uL', 'N', '2020-09-19 13:25:04'])
record.list_research.append([2, 'RBC', '2,18', '10*6/uL', 'L', '2020-09-19 13:25:04'])
record.list_research.append([3, 'HGB', '6,7', 'g/dL', 'L', '2020-09-19 13:25:04'])
record.list_research.append([4, 'HCT', '22,2', '%', 'L', '2020-09-19 13:25:04'])
#record.list_research.append([5, 'MCV', '101,8', 'fL', 'H', '2020-09-19 13:25:04'])
#record.list_research.append([6, 'MCH', '30,7', 'pg', 'N', '2020-09-19 13:25:04'])
#record.list_research.append([7, 'MCHC', '30,2', 'g/dL', 'L', '2020-09-19 13:25:04'])
#record.list_research.append([8, 'PLT', '573', '10*3/uL', 'H', '2020-09-19 13:25:04'])
#record.list_research.append([9, 'NEUT%', '43,3', '%', 'W', '2020-09-19 13:25:04'])
#record.list_research.append([10, 'LYMPH%', '39,6', '%', 'W', '2020-09-19 13:25:04'])

str_parm_names = ''
result_date = '2020-12-31 23:59:57'
nom = 0  # кол-во параметров (CntParam в SQL)
for an in record.list_research:
    nom = an[0]
    str_parm_names += ''.join([f', ParamName{nom}, ParamValue{nom}, ParamMsr{nom}, Attention{nom} '])
    str_tail += ''.join([f", '{an[1]}', '{an[2]}', '{an[3]}', '{an[4]}' "])
    result_date = an[5]  # '2020-12-31 23:59:59' # дату-время выполнения берём из последнего анализа.

str_parm_names += ''.join([', CntParam, ResultDate, ResultText'])
str_tail += ''.join([f", {nom}, '{result_date}', '{result_text}'"])
# str_tail += ''.join([f", GetDate(), '{result_text}'"])  # для второго варианта  - по времени добавления в SQL.

str_insert = ''.join([str_start, str_parm_names, str_tail, ')'])
return_code_sql = sql_insert(str_insert)
print(f'return_code_sql={return_code_sql}.')
