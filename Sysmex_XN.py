# Sysmex 2020-11-09 (from tcpServ 2020-09-21)
import socket
import sys
import time
import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from Parsing import parse_xn350, record
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const
from threading import Thread
import logging.config

logging.config.fileConfig('logging.ini')
logger = logging.getLogger()

def create_socket():
    """ Create connection and listening on PORT

    also log all receiveing data
    :return: received data
    """
    buffer_size: int = 1024 * 20  # 20  (Normally 1024, but to fast response it may be smaller)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # OSError: [WinError 10048] Обычно разрешается только одно использование адреса сокета (протокол/сетевой адрес/порт)
    try:
        s.bind((const.host, const.port))  # Host and port must be a tuple, e.g. s.connect(('10.12.0.30', 6634))
    except Exception as e:
        mes = "ERR >>> при попытке открыть порт (повторный запуск)."
        write_log(mes + str(e))
        write_errlog(mes, str(e))
        logger.exception('При попытке открыть сокет (повторный запуск).')
        sys.exit(911)  # ToDO - не завершается! mainloop?
    finally:
        pass

    s.listen(1)  # the value may help by setting the maximum length of the queue for pending connections.
    write_log('>>> Start listening...')
    logger.info(f'Start listening... {const.analyser_name}, id={const.analyser_id}, IP:{const.host}:{const.port}.')
    conn, addr = s.accept()
    mes = f'>>> Connection and address: {conn} {addr}.'
    write_log(mes + "-" * 20)
    logger.info(f'Connection and address: {conn} {addr}.')
    no_data = b'--- NO DATA! It is fake :)'  # чтобы не было ошибки 2020-10-19
    data_received = b''
    rec_eot = b'L|1|N\r'  # Message Terminator Record 'L' - Indicates the end of the message
    while 1:
        # ConnectionResetError: [WinError 10054] Удаленный хост принудительно разорвал существующее подключение
        # data = b'Номер анализатора'  # data - это не тот объект, что будет создан при выполнении data = conn.recv(buffer_size)
        # write_log(f'>>> debug1 01 data = b"01" id(data)={id(data)}.')
        try:
            # ERR 2020-10-02 UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc7 in position 68: invalid continuation byte
            data = no_data  # чтобы не было ошибки 2020-10-19
            err1 = """ File "D:\_KDL_\Python\TestSocket\Sysmex_XN.py", line 55, in create_socket
                    write_log(f'>>> получена часть данных, data:\n{data}\n--- конец части данных.')
                    UnboundLocalError: local variable 'data' referenced before assignment"""
            data = conn.recv(buffer_size)  # data - это каждый раз новый объект!!!
            write_log(f'>>> debug1 02 data = conn.recv(buffer_size) id(data)={id(data)}.')
            logger.debug(f'data = conn.recv(buffer_size) id(data)={id(data)}.')
            # raise socket.error
        except Exception as e:
            write_log("ERR >>> " + str(e))
            write_errlog("ERR ---", str(e))
            logger.exception("ERR data = conn.recv(buffer_size)")
            # socket.error
            # if e.__class__.__name__ == "socket.error":
            #     write_log("ERR [WinError 10054] Удаленный хост принудительно разорвал существующее подключение.")
        else:
            pass
        finally:
            if data != no_data:
                write_log(f'>>> получена часть данных, data:\n{data}\n--- конец части данных.')
                logger.debug(f'Received part of data:\n{data}')
                data_received += data

        if data == no_data:
            write_log(f'>>> no_data - return.')  # 2020-10-29  пров на выход по нет данных
            logger.debug('no_data - return.')
            return ''
        elif data.upper().find(b'QKRQ') > -1:
            write_log('>>> Кукареку - не спим, работаем...')
            write_log(data.decode())
            logger.info("We don't sleep! " + data.decode())
            return ''
        elif not data:
            write_log('>>> not data - break.')
            logger.debug('no_data - break.')
            break
        elif data.find(rec_eot) > -1:
            write_log(f'>>> find rec_eot - break.\n{data}\n--- конец rec_eot.')
            logger.debug('find rec_eot.')
            break
        else:
            write_log(f'>>> Received:\n{data}')
            logger.debug(f'Received unknown data:\n{data}')

    conn.close()
    write_log(f'>>> Connection closed normally. data_received:\n{data_received}\n--- конец data_received.')
    logger.info(f'Connection closed normally. data_received:\n{data_received}')
    return data_received


def sql_insert(str_sql: str) -> int:
    """ Запись в MS SQL одного результата от анализатора
    :type str_sql: str
    """
    try:
        conn = pyodbc.connect(const.sql_run)
        cursor = conn.cursor()
        write_log(str_sql)
        logger.info(str_sql)
        cursor.execute('set dateformat ymd;')
        cursor.execute(str_sql)
        conn.commit()
    except Exception as e:
        write_log("ERR Ошибка при записи SQL. " + str(e))
        write_errlog("ERR Ошибка при записи SQL.", str(e))
        logger.exception("ERR Ошибка при записи SQL.")
        return -1
    return 0


def transfer():
    """ Передача полученного от анализатора (всё уже в record.)

    :return: None
    """
    write_log(f">>> transfer(): номер истории={record.history_number}, ФИО={record.fio}")
    logger.info(f"Номер истории={record.history_number}, ФИО={record.fio}")
    cnt_max = 22  # (ограничение кол-ва полей в LabAutoResult)
    result_text = record.result_text  # 'тест7 Sysmex XN-350 '
    str_start = 'INSERT INTO [LabAutoResult].[dbo].[AnalyzerResults](Analyzer_Id,HistoryNumber'  # начало строки INSERT
    str_tail = f')Values({const.analyser_id},{record.history_number}'  # хвост строки INSERT
    str_parm_names = ''
    result_date = '2020-12-31 23:59:57'
    nom = 0  # кол-во параметров (CntParam в SQL)
    for an in record.list_research:
        write_log(f"Получено: {str(an)}")
        logger.info(f"Получено: {str(an)}")
        nom = an[0]  # берём номер исследоваия, который выдал анализатор, а не считаем сами!
        # TODO_ проверка на превышение максимального количества анализов (ограничение кол-ва полей в LabAutoResult)
        if nom > cnt_max:
            write_log(f'Анализов больше максимального({cnt_max}).')
            logger.warning(f'Анализов больше максимального({cnt_max}).')
            nom = cnt_max
            break

        str_parm_names += ''.join([f', ParamName{nom}, ParamValue{nom}, ParamMsr{nom}, Attention{nom} '])
        str_tail += ''.join([f", '{an[1]}', '{an[2]}', '{an[3]}', '{an[4]}' "])
        result_date = an[5]  # '2020-12-31 23:59:59' # дату-время выполнения берём из последнего анализа.
    str_parm_names += ''.join([', CntParam, ResultDate, ResultText'])
    str_tail += ''.join([f", {nom}, '{result_date}', '{result_text}'"])
    # str_tail += ''.join([f", GetDate(), '{result_text}'"])  # для второго варианта  - по времени добавления в SQL.

    str_insert = ''.join([str_start, str_parm_names, str_tail, ')'])
    return_code_sql = sql_insert(str_insert)
    logger.debug(f"Код возврата после записи SQL={return_code_sql}.")

    # TODO в ResultText добавлять: ФИО и все подсказки-диагнозы для врача, т.к. пока ещё неизвестно, куда их добавлять.
    # примеры: Anemia, Atypical_Lympho?, Iron_Deficiency?, - а надо ли всё это перевести на русский???
    # write_log('Данные в словаре:')
    # for key in record.dict_rec:
    #     write_log(f'dict {key}, {record.dict_rec[key]}')


def mainloop() -> None:
    """ ждём соединения

    :return: None
    """
    while True:
        record.__init__()  # при получении данных - "обнулить" всё
        data_obtained = create_socket()
        write_log(f"Получено байт: {len(data_obtained)}.\n{data_obtained}")
        logger.debug(f"Получено байт: {len(data_obtained)}.\n{data_obtained}")
        if len(data_obtained) > 0:
            parse_xn350(data_obtained)
            logger.debug("Передача...")
            transfer()


def log_alive():
    """ для внешнего контролирования, что процесс жив, периодически пишется в файл текущее время

    :return: None
    """
    while True:
        write_log(f'id: {const.analyser_id}.', f'{const.path_errlog}\\LogAlive.txt', f_mode='w')  # перезаписывать!
        time.sleep(60)  # 60 сек


if __name__ == '__main__':
    fn_ini = 'sysmex.ini'
    read_ini(fn_ini)
    write_log(f'Run {const.analyser_name}, analyser_id={const.analyser_id}, ' +
              f'analyser_location={const.analyser_location}, listening IP:{const.host}:{const.port}.')
    logger.info(f'Запуск {const.analyser_name}, id={const.analyser_id}, {const.analyser_location}, '
                f'IP:{const.host}:{const.port}.')
    # th = Thread(target=log_alive, name=f'{const.analyser_id}_ALIVE')
    th = Thread(target=log_alive, name='Sysmex_ALIVE')
    th.start()
    mainloop()
