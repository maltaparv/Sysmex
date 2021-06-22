# Sysmex XN 350,550. 2020-11-09 (from tcpServ 2020-09-21)
import socket
import sys
import os
import time
import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from Parsing import parse_xn350, record
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const
from threading import Thread
import logging.config

FN_INI = "sysmex.ini"  # начальная конфигурация. Все конфигурационные файлы располагаются в каталоге, откуда запуск.
FN_LOG = "Sysmex.log"  # циклическая запись логов. Ещё его имя и расположение и задано в FN_LOGGING_INI.
FN_LOGGING_INI = "logging.ini"  # настройки логирования.
FN_ALIVE = "LogAlive.txt"  # файл контроля, работает ли процесс (для внешней программы отслеживания).


def create_socket():
    """ Create connection and listening on PORT

    also log all receiving data
    :return: received data
    """
    buffer_size: int = 1024 * 20  # 20  (Normally 1024, but to fast response it may be smaller)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((const.host, const.port))  # Host and port must be a tuple, e.g. s.connect(('10.12.0.30', 6634))
    except OSError as e:
        if e.winerror == 10048:
            # OSError: [WinError 10048] Обычно разрешается только одно использование адреса сокета
            # (протокол/сетевой адрес/порт)
            logger.info("Это повторный запуск [WinError 10048]. Завершение работы.")
            sys.exit(901)
        else:
            logger.exception('Ошибка при открытии сокета (повторный запуск?).')
    finally:
        pass

    s.listen(1)  # the value may help by setting the maximum length of the queue for pending connections.
    logger.info(f"Ожидание соединения... {const.analyser_name}, id={const.analyser_id}, "
                f"IP:{const.host}:{const.port}, PID:{const.pid}.")
    conn, addr = s.accept()
    logger.info(f"Соединенились с анализатором: {conn} {addr}.")
    no_data = b'--- NO DATA! It is fake :)'  # чтобы не было ошибки 2020-10-19
    data_received = b''
    rec_eot = b'L|1|N\r'  # Message Terminator Record 'L' - Indicates the end of the message
    while 1:
        try:
            data = no_data  # чтобы не было ошибки 2020-10-19
            err1 = """ File "D:\_KDL_\Python\TestSocket\Sysmex_XN.py", line 55, in create_socket
                    UnboundLocalError: local variable 'data' referenced before assignment"""
            data = conn.recv(buffer_size)  # data - это каждый раз новый объект!!!
        except Exception as e:  # socket.error
            if e.winerror == 10054:
                logger.info("Анализатор принудительно разорвал соединение [WinError 10054].")
                # ConnectionResetError: [WinError 10054] Удаленный хост принудительно разорвал существующее подключение
            elif e.winerror == 10053:
                logger.info(" Программа на вашем хост-компьютере разорвала установленное подключение [WinError 10053].")
                # ConnectionAbortedError: [WinError 10053]
                # Программа на вашем хост-компьютере разорвала установленное подключение
            else:
                logger.exception("Ошибка при получении данных из сокета.")
        else:
            pass  # logger.debug("--- Не было исключения при conn.recv(buffer_size)")
        finally:
            if data != no_data:
                logger.debug(f"Получены данные:\n{data}")
                data_received += data

        if data == no_data:
            logger.debug("Нет даных - return.")
            return ""
        elif data.upper().find(b'QKRQ') > -1:
            logger.info(">>> Кукареку - не спим, работаем! " + data.decode())
            return ""
        elif not data:
            logger.debug("Нет даных - break.")
            break
        elif data.find(rec_eot) > -1:
            logger.debug("Есть Message Terminator Record 'L' - break.")
            break
        else:
            logger.warning(f"Получены неизвестные данные:\n{data}")
    conn.close()
    logger.info(f"Соединение закрыто успешно.")
    return data_received


def sql_insert(str_sql: str) -> int:
    """ Запись в MS SQL одного результата от анализатора
    :type str_sql: str
    """
    try:
        conn = pyodbc.connect(const.sql_run)
        cursor = conn.cursor()
        logger.info(str_sql)
        cursor.execute('set dateformat ymd;')
        cursor.execute(str_sql)
        conn.commit()
    except Exception as e:
        logger.exception("Ошибка при записи SQL.")
        return -1
    return 0


def transfer():
    """ Передача полученного от анализатора (всё уже в record.)

    :return: None
    """
    logger.info(f"Номер истории={record.history_number}, ФИО={record.fio}")
    # cnt_max = 28  # (ограничение кол-ва полей в LabAutoResult - было 22)
    result_text = record.result_text  # 'тест7 Sysmex XN-350 '
    str_start = 'INSERT INTO [LabAutoResult].[dbo].[AnalyzerResults](Analyzer_Id,HistoryNumber,Comment1'  # INSERT
    str_tail = f')Values({const.analyser_id},{record.history_number},{record.sample_id_no}'  # хвост строки INSERT
    str_parm_names = ''
    result_date = '2020-12-31 23:59:57'
    s_an = 'Полученные анализы:'  # полученные результы (для логов - все вместе, в разных строках)
    nom = 0  # кол-во параметров (CntParam в SQL)
    for an in record.list_research:
        s_an += f"\n{str(an)}"   # полученные результаты (для логов - все вместе, в разных строках)
        nom = an[0]  # берём номер исследоваия, который выдал анализатор, а не считаем сами!
        # TODO_ проверка на превышение максимального количества анализов (ограничение кол-ва полей в LabAutoResult)
        if nom > const.max_cnt_param:  # cnt_max: (ограничение кол-ва полей в LabAutoResult - было 22)
            logger.warning(f"Количество анализов больше максимального (max={const.max_cnt_param}).")
            nom = const.max_cnt_param
            break
        an_name = an[1]  # название анализа
        if len(an_name) > const.max_length_analyze_name:
            logger.warning(f"Длинное название {nom}-го анализа: {an_name}. (max={const.max_length_analyze_name}).")
            an_name = ''.join([an_name[0:const.max_length_analyze_name-5], '<cut>'])  # припишем призак обрезания :))

        str_parm_names += ''.join([f', ParamName{nom}, ParamValue{nom}, ParamMsr{nom}, Attention{nom} '])
        str_tail += ''.join([f", '{an_name}', '{an[2]}', '{an[3]}', '{an[4]}' "])
        result_date = an[5]  # '2020-12-31 23:59:59' # дату-время выполнения берём из последнего анализа.
    logger.info(s_an)
    str_parm_names += ''.join([', CntParam, ResultDate, Comment2, ResultText'])
    str_tail += ''.join([f", {nom}, '{result_date}', '{record.diagnosis}', '{result_text}'"])
    # str_tail += ''.join([f", GetDate(), '{result_text}'"])  # для второго варианта  - по времени добавления в SQL.

    str_insert = ''.join([str_start, str_parm_names, str_tail, ')'])
    return_code_sql = sql_insert(str_insert)
    logger.debug(f"diagnosis: {record.diagnosis}")
    logger.info(f"Код возврата после записи SQL={return_code_sql}.")  ## was logger.debug  earlier.

    # TODO в ResultText добавлять: ФИО и все подсказки-диагнозы для врача, т.к. пока ещё неизвестно, куда их добавлять.
    # примеры: Anemia, Atypical_Lympho?, Iron_Deficiency?, - а надо ли всё это перевести на русский???
    # write_log('Данные в словаре:')
    # for key in record.dict_rec:
    #     write_log(f'dict {key}, {record.dict_rec[key]}')


def mainloop() -> None:
    """ ждём соединения

    :return: None
    """
    while 1:
        record.__init__()  # при получении данных - "обнулить" всё
        data_obtained = create_socket()
        logger.debug(f"Получено байт: {len(data_obtained)}.\n{data_obtained}")
        if len(data_obtained) > 0:
            parse_xn350(data_obtained)
            transfer()


def log_alive():
    """ для внешнего контролирования, что процесс жив, периодически пишется в файл текущее время

    :return: None
    """
    while 1:
        write_log(f"id: {const.analyser_id}.", FN_ALIVE, f_mode="w")  # перезаписывать!
        time.sleep(60)  # 60 сек


if __name__ == '__main__':
    # Проверка наличия конфигурационных файлов
    if not os.path.isfile(FN_LOGGING_INI):
        write_log(f"; CRITICAL; Не найден ini-файл логирования: {FN_LOGGING_INI}. Завершение работы.", FN_LOG)
        sys.exit(1)  # sys.exit(1)  exit(2) os._exit(3) quit(4) raise SystemExit(5)

    name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    logging.config.fileConfig(FN_LOGGING_INI)
    logger = logging.getLogger(name)

    if not os.path.isfile(FN_INI):
        logger.fatal(f"Не найден конфигурационный ini-файл: {FN_INI}. Завершение работы.")
        sys.exit(2)

    read_ini(FN_INI)
    const.pid = os.getpid()
    logger.info(f'Запуск {const.analyser_name}, id={const.analyser_id}, {const.analyser_location}, '
                f'IP:{const.host}:{const.port}, PID:{const.pid}.')

    th = Thread(target=log_alive, name=FN_ALIVE, daemon=True)
    # Процесс - демон, чтобы можно было выйти из основного при повторном запуске по sys.exit(901).
    # This thread dies when main thread exits.
    th.start()
    mainloop()
    print("--- Exit from __main__.")  # Сюда не доходим :) Только снятие процесса.
    sys.exit(911)
