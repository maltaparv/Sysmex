# ProcLib 2020-09-30 (a la EC-1060 computer :)) (2020-11-09 to GitHub)
import os.path
import datetime
from ClassLib import const

# TODO_done 10-12 all constants must be in separate class (2020-10-03)
def write_log(message, log_file='Log') -> None:
    """ Log all data and current date-time stamp to special file

    :param message:
    :param log_file:
    :return: None
    """
    # TODO send list of parameters instead of one    write_log(*message) -> None:(2020-10-03)
    # write_log(message: str) -> None:    write_log(*message) -> None:
    now = datetime.datetime.now()
    # TODO_done 10-12 all constants must be in separate class (2020-10-03)
    # const.path_log = r"D:\_KDL_\Sysmex XN-350\Data_Sysmex\\"  # - from ini-file
    filename = f'{const.path_log}\\{log_file}{now.strftime("%Y-%m-%d")}.txt'
    print('===', filename)
    # r'D:\TempData\Log.tx  t' r"D:\_KDL_\Sysmex XN-350\Data_Sysmex\LogSysmex.txt" "LogSysmex.txt"
    with open(filename, 'a') as f:
        time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        prefix_message = f'{time_stamp} {message}'
        f.write(f'{prefix_message}\n')
        if const.mode.find('SCR') > -1:
            print(prefix_message, sep=' ')  # and always print to screen


def write_errlog(message, o_err) -> None:
    """Log all data and current date-time stamp to special file """
    # write_log(message: str) -> None:    write_log(*message) -> None:
    now = datetime.datetime.now()
    # TODO_done 10-12 all constants must be in separate class (2020-10-03)
    filename = f'{const.path_errlog}\\ErrLog.txt'
    # r'D:\TempData\Log.txt' r"D:\_KDL_\Sysmex XN-350\Data_Sysmex\LogSysmex.txt" "LogSysmex.txt"
    with open(filename, 'a') as f:
        time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        prefix_message = f'{time_stamp} {message}'
        print(prefix_message)  # and always print to screen
        print(o_err)
        f.write(f'{prefix_message}\n')
        f.write(o_err)
        f.write('\n')
        if const.mode.find('SCR') > -1:
            print(prefix_message)
            print(o_err)


def read_ini(ini_file):
    """ Читаем все константы
    
    see help on https://python-scripts.com/configparser-python-example
    :param ini_file:
    :param const:
    :return:
    """
    import configparser  # импортируем библиотеку
    # ini_file = "Sysmex350.ini"
    if not os.path.isfile(ini_file):
        write_log(f"Нет файла {ini_file}. Завершение работы.")
        raise SystemExit(1)  # exit(0) sys.exit

    # TODO check errors in filling ini-file, e.g.:  path_log = <empty>, etc. (2020-10-03)

    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read(ini_file)  # читаем конфиг

    const.analyser_id = int(config['Common']['analyser_id'])
    const.analyser_name = config['Common']['analyser_name']
    const.analyser_location = config['Common']['analyser_location']  # .encode('cp1251').decode('utf8')

    const.host = config['Connection']['host']
    const.port = int(config['Connection']['port'])
    # const.sql_run = config.get('Connection', 'sql_run1')
    const.server = config.get('Connection', 'server')
    const.database = config.get('Connection', 'database')
    const.user_name = config.get('Connection', 'user_name')
    const.password = config.get('Connection', 'pwd')
    const.sql_run = ''.join(['DRIVER={ODBC Driver 17 for SQL Server};SERVER=', const.server,
                             ';DATABASE=', const.database, ';UID=', const.user_name, ';PWD=', const.password])
    const.path_log = config.get('LogFiles', 'path_log')
    const.path_errlog = config.get('LogFiles', 'path_errlog')
    const.mode = config.get('Modes', 'mode')

    const.num_run = int(config.get('Stat', 'num_run')) + 1
    config.set('Stat', 'num_run', str(const.num_run))
    config.set('Stat', 'last_run', str(datetime.datetime.now()))
    with open(ini_file, "w") as config_file:
        config.write(config_file)

    # ToDo_Done 10-12 all constants must be in separate class (2020-10-03)
    print(f'analyser_id={const.analyser_id}.')
    print(f'analyser_name={const.analyser_name}.')
    print(type(const.host), len(const.host))
    print(f'host=({const.host}).')
    print(f'port={const.port}.')
    print(f'path_log={const.path_log}')
    print(f'path_errlog={const.path_errlog}')
    print(f'num_run = {const.num_run}.')
    print(f'last_run={const.last_run}.')


if __name__ == "__main__":
    write_log("Testing function write_log in my ProcLib.")
    write_log("Testing function write_log in my ProcLib - write to ErrLog.", log_file='ErrLog')
    # для def write_log(*message) -> None:
    # write_log("aa1")  # ('aa1',)
    # write_log("a1", "b2")  # ('a1', 'b2')
    # write_log(123, "c33")  # ('a1', 'b2')
