import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const

_analyzer_id: int = 911  # задаётся в ini-файле в секции [Connection]
_server: str = 'Asu-911'  # 'tcp:myserver._database.windows.net'
_database: str = 'LabAutoResult'
_username: str = 'sa'
_password: str = '1'
_run_count: int = 911
_debug: bool = False


def sql_insert(str_sql: str) -> int:
    """ Запись в MS SQL одного результата от анализатора
    :type str_sql: str
    """

    try:
        conn = pyodbc.connect(const.sql_run)
        cursor = conn.cursor()
        write_log(str_sql)
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
history_number = 50000 + _run_count
result_text = 'ПЦР-тест на антитела и ещё кое-что...'
param_name1 = 'SARS-CoV-2'
param_value1 = 'ОБНАРУЖЕНО'
str_insert = "INSERT INTO [LabAutoResult].[dbo].[AnalyzerResults]" \
             + "(Analyzer_Id, HistoryNumber, ResultDate, CntParam, ResultText, ParamName1, ParamValue1)Values(" \
             + str(_analyzer_id) + ", " + str(history_number) + ", GetDate(), 1, '" + result_text + "', '" \
             + param_name1 + "', '" + param_value1 + "')"
return_code = sql_insert(str_insert)
print(f'return_code={return_code}.')
