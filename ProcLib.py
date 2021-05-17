# ProcLib 2020-09-30 (a la EC-1060 computer :)) (2020-11-09 to GitHub)
import os.path
import datetime
from ClassLib import const
import configparser


# TODO_done 10-12 all constants must be in separate class (2020-10-03)
def write_log(message, log_file='Log', f_mode='a') -> None:
    """ Log all data and current date-time stamp to special file

    :param message:
    :param log_file:
    :param f_mode:
    :return: None
    """
    # TODO send list of parameters instead of one    write_log(*message) -> None:(2020-10-03)
    # write_log(message: str) -> None:    write_log(*message) -> None:
    now = datetime.datetime.now()
    if log_file == 'Log':
        filename = f'{const.path_log}\\{log_file}{now.strftime("%Y-%m-%d")}.txt'
    else:
        filename = log_file
    with open(filename, f_mode) as f:
        time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        prefix_message = f'{time_stamp} {message}'
        f.write(f'{prefix_message}\n')
        if const.mode.find('SCR') > -1 and f_mode != 'w':
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
        if "SCR" in const.mode:
            print(prefix_message)
            print(o_err)


def read_ini(ini_file):
    """ Читаем все константы
    
    see help on https://python-scripts.com/configparser-python-example
    :param ini_file:
    :param const:
    :return:
    """
    # TODO check errors in filling ini-file, e.g.:  path_log = <empty>, etc. (2020-10-03)
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read(ini_file)  # читаем конфиг

    const.analyser_id = int(config['Connection']['analyser_id'])
    const.analyser_name = config['Connection']['analyser_name']
    const.analyser_location = config['Connection']['analyser_location']  # .encode('cp1251').decode('utf8')
    const.host = config['Connection']['host']
    const.port = int(config['Connection']['port'])
    const.server = config.get('Connection', 'server')
    const.database = config.get('Connection', 'database')
    const.user_name = config.get('Connection', 'user_name')
    const.password = config.get('Connection', 'pwd')
    const.sql_run = ''.join(['DRIVER={ODBC Driver 17 for SQL Server};SERVER=', const.server,
                             ';DATABASE=', const.database, ';UID=', const.user_name, ';PWD=', const.password])
    const.mode = config.get('Modes', 'mode')
    const.Max_Cnt_Param = int(config.get('Check', 'Max_Cnt_Param'))
    const.Max_Length_Analyze_Name = int(config.get('Check', 'Max_Length_Analyze_Name'))
    const.num_run = int(config.get('Stat', 'num_run')) + 1
    config.set('Stat', 'num_run', str(const.num_run))
    const.last_run = str(datetime.datetime.now())
    config.set('Stat', 'last_run', const.last_run)
    with open(ini_file, "w") as config_file:
        config.write(config_file)


if __name__ == "__main__":
    write_log("Testing function write_log in my ProcLib.")
    write_log("Testing function write_log in my ProcLib - write to ErrLog.", log_file='ErrLog')
