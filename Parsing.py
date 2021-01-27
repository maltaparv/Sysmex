# Parsing.py 2020-11-09 ParseXN350
from ClassLib import RECORD
from datetime import datetime
# from Sysmex_XN import logger
import logging.config

logger = logging.getLogger()


def parse_patient_record(line):
    """парсинг строки пациента. Получаем номер истории, ФИО, и (если будет нужно) название отделения.

    :param line:
    :return:
    """
    line_patient = line.decode('cp1251')
    logger.debug(f"Patient Info Record:\n{line_patient}")
    record_field = line.decode('cp1251').split('|')
    if len(record_field) <= 4:
        logger.warning(f'Проверка Patient Info Record: Нет номера истории, ФИО: \n{line_patient}')
        record.history_number = '0'
        record.fio = '--- no fio ---'
        return None
    record.history_number = record_field[4]
    record.fio = record_field[5].replace('^', ' ').strip()
    logger.debug(f'parse_patient_record: record.history_number={record.history_number}, record.fio={record.fio=}.')
    return None


def parse_result_record(line):
    """ парсинг строки с результатами исследований

    :param line:
    :return:
    """
    record_field = line.decode('cp1251').split('|')
    if len(record_field) < 12:
        logger.warning(f'Cтрока {line} содержит менее 12 полей. Она игнорируется.')
        return
    an_no = int(record_field[1])
    an_name = record_field[2].replace('^', ' ').strip()
    # an_name = name_an(an_no, an_name)
    if an_no <= 28:
        an_name = an_name[:-2]  # Analysis Parameter ID without last 2 characters
    an_res = record_field[3]
    an_ed = record_field[4]
    an_flag = record_field[6]
    date_string = record_field[12]  # 20200908110303
    # TODO_done 2020-10-06_08 (для SQL формат такой: “2019-12-31 23:52:42.423”)
    date_object = datetime.strptime(date_string, "%Y%m%d%H%M%S")  # "20201008235159"
    an_time = date_object.strftime('%Y-%m-%d %H:%M:%S')  # для MS SQL формат такой: “2019-12-31 23:52:49.123”
    print(an_no, an_name, an_res, an_ed, an_flag, an_time, sep=';')
    record.an = [an_no, an_name, an_res, an_ed, an_flag, an_time]  # current record with one result
    record.list_research.append(record.an)  # Add to patient's list of analysis the current result
    # ToDo_done 2020-10-09 Сделать словарь для одной записи вместо списка record.list_an
    num = int(record_field[1])  # берём номер исследоваия, который выдал анализатор, а не считаем сами!
    record.dict_rec[f'number{num}'] = num
    # record.dict_rec[f'ParamName{num}'] = name_an(num, record_field[2].replace('^', ' ').strip())
    record.dict_rec[f'ParamName{num}'] = an_name
    record.dict_rec[f'ParamValue{num}'] = record_field[3]
    record.dict_rec[f'ParamMsr{num}'] = record_field[4]
    record.dict_rec[f'flag{num}'] = record_field[6]
    # TODO_2020-10-06_08 (для MS SQL формат такой: “2019-12-31 23:52:49.123”)
    date_object = datetime.strptime(record_field[12], "%Y%m%d%H%M%S")  # "20201008235159"
    record.dict_rec[f'date_time{num}'] = date_object.strftime('%Y-%m-%d %H:%M:%S')
    # for num in [2, 5, 7, 8, 9, 10, 11]:
    #     record.dict_rec[f'field{num}'] = record_field[num]  # для полей с неизвестной семантикой - пусть пока будут.
    return None


def parse_xn350(data):
    """ Parsing data for Sysmex XN-350

    :param data:
    :return:
    """
    logger.debug("Парсинг...")
    record.result_text = data.decode('cp1251')  # это весь полученный текст для записи в SQL
    dl = data.splitlines()
    # Records types according to "Automated Hematology Analyzer XN-L series.
    # ASTM Host Interface Specifications", page 14.
    # A record is a series of text, beginning with an ASCII alphabetic character called the identifier
    # and ending with [CR]
    dict_record_name = {'H': 'Header Record',
                        'P': 'Patient Info Record',
                        'Q': 'Inquiry Record',
                        'O': 'Analysis Order Record',
                        'R': 'Analysis Result Record',
                        'C': 'Comment Record',
                        'M': 'Manufacturer Info Record',
                        'S': 'Scientific Info Record',
                        'L': 'Message Terminator Record'}
    for line in dl:
        record_id = line[0:1].decode('cp1251')
        record_type = dict_record_name.get(record_id)  # из словаря получили тип записи или None, если нет в словаре.
        if record_id == 'P':
            parse_patient_record(line)
        elif record_id == 'R':
            parse_result_record(line)
        # logger.debug(f"Record type: {record_type}. {line}")
    return None


record = RECORD()  # to fill from all where it needs :))

if __name__ == '__main__':
    msg = f'Parsing - Run from {__name__}.'
    print(msg)
    msg = """
for record definitions see p.14 Automated Hematology Analyzer XN-L series
                                ASTM Host Interface Specifications.
Table 5: Records
Record type                Record     Level Description
                           identifier
Header Record              H          0     Contains the sender and the receiver information
Patient Info Record        P          1     Contains the patient information
Inquiry Record             Q          1     Contains inquiry into the host computer for analysis order information
Analysis Order Record      O          2     Contains analysis order information
Analysis Result Record     R          3     Contains analysis results
Comment Record             C          1-4   Contains comments about the sample or patient
Manufacturer Info  Record  M          1-4   Not used
Scientific Info Record     S          N/A   Not used
Message Terminator Record  L          0     Indicates the end of the message
............................................................................
"""
    number = 29
    ss = "^^^^WBC^1"
    t = lambda s, n: s[:-2] if n <= 28 else s
    print(f"num={number}, lambda={t(ss, 28)}")
    print(f"lambda={(lambda s, n: s[:-2] if n <= 28 else s)(ss, 28)}.")
