import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from ProcLib import write_log, write_errlog, read_ini

# _path_ini_file: str = "BCS_XP.ini"  # или лучше назвать "settings.ini"?
# _path_log: str = "."  # задаётся в ini-файле в секции [LogFiles]
# _path_err_log: str = "."
_analyzer_id: int = 911  # задаётся в ini-файле в секции [Connection]
# _com_port_name: str = 'no!'
# _sql_connect: str = 'yes'
_server: str = 'Asu-911'  # 'tcp:myserver._database.windows.net'
_database: str = 'LabAutoResult'
_username: str = 'sa'
_password: str = '1'
# _err_date: str = 'd-m-y'  # задаётся в ini-файле в секции [Statistics]
# _err_msg: str = 'xx-x'
_run_count: int = 911
# _list_modes: str = '-'  # задаётся в ini-файле в секции [Modes]
_debug: bool = False


def sql_insert(str_sql: str) -> str:
    """ Запись в MS SQL одного результата от анализатора
    :type str_sql: str
    """
    str_insert = str_sql

    history_number = 99000 + _run_count
    result_text = 'тест антитела'
    param_name1 = 'COVID-19'
    param_value1 = 'ОБНАРУЖЕНО'
    str_insert = "INSERT INTO [LabAutoResult].[dbo].[AnalyzerResults]" \
                 + "(Analyzer_Id, HistoryNumber, ResultDate, CntParam, ResultText, ParamName1, ParamValue1)Values(" \
                 + str(_analyzer_id) + ", " + str(history_number) + ", GetDate(), 1, '" + result_text + "', '" \
                 + param_name1 + "', '" + param_value1 + "')"
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' \
                              + _server + ';DATABASE=' + _database + ';UID=' + _username + ';PWD=' + _password)
        cursor = conn.cursor()
        if _debug:
            print('proc sql_insert:', str_insert)
        write_log(str_insert)
        cursor.execute(str_insert)
        conn.commit()
    except Exception:
        write_errlog("Ошибка при записи SQL.")
        write_log("Ошибка при записи SQL.")
        if _debug:
            print('Exception: ---', Exception)
        return -1
    return 0
    # row = cursor.fetchone()
    # while row:

print('Test_SQL')
ss = sql_insert('abc123')
print(ss)
