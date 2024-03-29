# Parsing.py 2020-11-09 ParseXN350
from ClassLib import RECORD
from datetime import datetime
import logging.config
import decimal

logger = logging.getLogger()


def parse_order_record(line):
    # comming line = "O|1||^^                    58^M|^^^^WBC\^^^^RBC\^^^^HGB\^^^^..." - sample_id_no="58"
    field = line.decode('cp1251').split('|')
    idn = field[3].split('^')
    record.sample_id_no = idn[2].strip()
    logger.info(f"Sample ID No: {record.sample_id_no}")
    return None


def parse_patient_record(line):
    """парсинг строки пациента. Получаем номер истории, ФИО, и (если будет нужно) название отделения.

    :param line:
    :return:
    """
    line_patient = line.decode('cp1251')
    logger.debug(f"Patient Info Record: {line_patient}")
    record_field = line.decode('cp1251').split('|')
    if len(record_field) <= 4:
        logger.warning(f"Нет номера истории, ФИО: {line_patient}")
        record.history_number = "0"
        record.fio = "--- нет ФИО ---"
        return None
    record.history_number = record_field[4]
    if len(record.history_number) == 0:
        record.history_number = '0'
        logger.warning(f"Нет номера истории: {line_patient}")
    record.fio = record_field[5].replace('^', ' ').strip()
    if len(record.fio) == 0:
        record.fio = "--- не ввели ФИО ---"

    logger.debug(f"parse_patient_record: record.history_number={record.history_number}, record.fio={record.fio}.")
    return None


def parse_result_record(line):
    """ парсинг строки с результатами исследований

    :param line:
    :return:
    """
    record_field = line.decode('cp1251').split('|')
    if len(record_field) < 12:
        logger.warning(f"Строка {line} содержит менее 12 полей. Она игнорируется.")
        return
    an_no = int(record_field[1])
    an_name = record_field[2].replace('^', ' ').strip()

    if an_no <= 28:
        an_name = an_name[:-2]  # Analysis Parameter ID without last 2 characters: "^^^^WBC^1" -> "^^^^WBC"
    else:
        if an_name[:5] != "SCAT_" and an_name[:5] != "DIST_":  # это ссылка на рисунки .PNG - их пропускаем.
            record.diagnosis += "".join([an_name, "#"])  # заполняем строку предполагаемых диагнозов.

    an_res = record_field[3]
    if an_name == 'HGB' or an_name == 'MCHC':
        an_res = an_res.replace(',', '.')
        #print(record_field)
        if an_res != '----':  # мало крови
            ## была ошибка:  decimal.InvalidOperation: [<class 'decimal.ConversionSyntax'>]
            an_res = decimal.Decimal(an_res) * 10
            an_res = str(an_res).replace('.0', ' ').strip()

    an_ed = record_field[4]
    an_flag = record_field[6]
    date_string = record_field[12]  # 20200908110303
    date_object = datetime.strptime(date_string, "%Y%m%d%H%M%S")  # "20201008235159"
    an_time = date_object.strftime('%Y-%m-%d %H:%M:%S')  # для MS SQL формат такой: “2019-12-31 23:52:49.123”
    record.an = [an_no, an_name, an_res, an_ed, an_flag, an_time]  # current record with one result.
    record.list_research.append(record.an)  # Add to patient's list of analysis the current result.
    # ToDo_done 2020-10-09 Сделать словарь для одной записи вместо списка record.list_an.
    num = int(record_field[1])  # берём номер исследоваия, который выдал анализатор, а не считаем сами!
    record.dict_rec[f'number{num}'] = num
    record.dict_rec[f'ParamName{num}'] = an_name
    record.dict_rec[f'ParamValue{num}'] = an_res  # record_field[3]
    record.dict_rec[f'ParamMsr{num}'] = an_ed  # record_field[4]
    record.dict_rec[f'flag{num}'] = an_flag  # record_field[6]
    date_object = datetime.strptime(date_string, "%Y%m%d%H%M%S")  # "20201008235159"
    record.dict_rec[f'date_time{num}'] = date_object.strftime('%Y-%m-%d %H:%M:%S')
    # for num in [2, 5, 7, 8, 9, 10, 11]:
    #     record.dict_rec[f"field{num}"] = record_field[num]  # для полей с неизвестной семантикой - пусть пока будут.
    return None


def parse_xn350(data):
    """ Parsing data for Sysmex XN-350 and Sysmex XN-550

    :param data:
    :return:
    """
    logger.debug("Парсинг...")
    record.result_text = data.decode('cp1251')  # это весь полученный текст для записи в SQL.
    dl = data.splitlines()
    # Records types according to "Automated Hematology Analyzer XN-L series.
    # ASTM Host Interface Specifications", page 14.
    # A record is a series of text, beginning with an ASCII alphabetic character called the identifier.
    # and ending with [CR].
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
        elif record_id == 'O':
            parse_order_record(line)
        elif record_id == 'C':
            pass
        # logger.debug(f"Record type: {record_type}. {line}")
    return None


record = RECORD()  # to fill from all where it needs :).

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
    tt = lambda s, n: s[:-2] if n <= 28 else s
    print(f"num={number}, lambda={tt(ss, 28)}")
    print((lambda s, n: s[:-2] if n <= 28 else s)(ss, 28))

    an_name = 'HGB'
    an_res = ''  ## '14,6'  #
    an_name = 'MCHC'
    an_res = '29,4'

    if an_name == 'HGB' or an_name == 'MCHC':
        an_res = an_res.replace(',', '.')
        an_res = decimal.Decimal(an_res) * 10
        an_res = str(an_res).replace('.0', ' ').strip()

    print("an_name = " + an_name + ", an_res = " + an_res + ".")


