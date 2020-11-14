# Sysmex 2020-11-09 (from tcpServ 2020-09-21)
import socket
import datetime

from Parsing import parse_xn350, record
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const

# TODO_done: ANALYSER_ID, PORT, PATH_LOG - read from .ini-file and assign correct values. These values are default!


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
    finally:
        pass

    s.listen(1)  # the value may help by setting the maximum length of the queue for pending connections.
    write_log('>>> Start listening...')
    conn, addr = s.accept()
    mes = f'>>> Connection and address: {conn} {addr}.'
    write_log(mes + "-" * 20)
    no_data = b'--- NO DATA! It is fake :)'  # чтобы не было ошибки 2020-10-19
    data_received = b''
    rec_eot = b'L|1|N\r'  # Message Terminator Record 'L' - Indicates the end of the message
    while 1:
        # ConnectionResetError: [WinError 10054] Удаленный хост принудительно разорвал существующее подключение
        # data = bНомер анализатора''  # data - это не тот объект, что будет создан при выполнении data = conn.recv(buffer_size)
        # write_log(f'>>> debug1 01 data = b"01" id(data)={id(data)}.')
        try:
            # ERR 2020-10-02 UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc7 in position 68: invalid continuation byte
            data = no_data  # чтобы не было ошибки 2020-10-19
            err1 = """ File "D:\_KDL_\Python\TestSocket\Sysmex_XN.py", line 55, in create_socket
                    write_log(f'>>> получена часть данных, data:\n{data}\n--- конец части данных.')
                    UnboundLocalError: local variable 'data' referenced before assignment"""
            data = conn.recv(buffer_size)  # data - это каждый раз новый объект!!!
            write_log(f'>>> debug1 02 data = conn.recv(buffer_size) id(data)={id(data)}.')
            # raise socket.error
        except Exception as e:
            write_log("ERR >>> " + str(e))
            write_errlog("ERR ---", str(e))
            # socket.error
            # if e.__class__.__name__ == "socket.error":
            #     write_log("ERR [WinError 10054] Удаленный хост принудительно разорвал существующее подключение.")
        else:
            pass
        finally:
            if data != no_data:
                write_log(f'>>> получена часть данных, data:\n{data}\n--- конец части данных.')
                write_log(f'>>> type(data)={type(data)}.')
                write_log(f'>>> debug1 3 finally id(data)={id(data)}.')
                data_received += data
                write_log(f'>>> debug1 3 data_received += data --- id(data_received)={id(data_received)}.')

        if data == no_data:
            write_log(f'>>> no_data, returm.')  # 2020-10-29  пров на выход по нет данных
            return ''
        elif data.upper().find(b'QKRQ') > -1:
            write_log('>>> Кукареку - не спим, работаем...')
            write_log(data.decode())
            return ''
        elif not data:
            # pass
            write_log('>>> not data - break.')
            break
        elif data.find(rec_eot) > -1:
            write_log(f'>>> find rec_eot - break.\n{data}\n--- конец rec_eot.')
            break
        else:
            write_log(f'>>> Received:\n{data}')

    conn.close()
    write_log(f'>>> Connection closed normally. data_received:\n{data_received}\n--- конец data_received.')
    return data_received


def transfer():
    """ Передача полченного от анализатора (всё уже в record.)

    :return: None
    """
    write_log(f">>> transfer(): номер истории={record.history_number}, ФИО={record.fio}")
    cnt_max = 22  # (ограничение кол-ва полей в LabAutoResult)
    str1 = ''  # начало строки INSERT into ... (Analyzer_Id, HistoryNumber, ResultDate,
    str2 = ''  # хвост  строки INSERT ... values(...{record.history_number}, ...
    for an in record.list_research:
        write_log(f"Получено: {str(an)}")
        #TODO проверить на превышение максимального количества анализов (ограничение кол-ва полей в LabAutoResult)
        # if key > cnt_max:
        #     write_log(f'Анализ больше максимального({cnt_max}): ')

    #TODO в ResultText добавлять: ФИО и все подсказки-диагнозы для врача, т.к. пока ещё неизвестно, куда их добавлять.
    # примеры: Anemia, Atypical_Lympho?, Iron_Deficiency?, - а надо ли всё это перевести на русский???
    write_log('Данные в словаре:')
    for key in record.dict_rec:
        write_log(f'dict {key}, {record.dict_rec[key]}')


def mainloop() -> None:
    """ ждём соединения

    :return: None
    """
    while True:
        # ToDO проверка текущей даты
        record.__init__()  # при получении данных - "обнулить" всё
        data_obtained = create_socket()
        write_log(f'>>> After create_socket() - data_obtained:\n{data_obtained}\n--- End of data_obtained.')

        if len(data_obtained) > 0:
            parse_xn350(data_obtained)
            transfer()

        # write_log(f">>> Ready to next connection. Date-time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        write_log(f">>> Ready to next connection.")

if __name__ == '__main__':
    # ToDo_done read_ini
    # const = CONST()  # to fill from ini
    # fn_ini = 'sysmex350.ini'
    fn_ini = 'sysmex550.ini'
    read_ini(fn_ini)
    write_log(f'Run {const.analyser_name}, analyser_id={const.analyser_id}, ' +
              f'analyser_location={const.analyser_location}, listening IP:{const.host}:{const.port}.')
    mainloop()
