# ClassLib 2020-10-07
class RECORD:
    """ Data received from analyser SYSMEX XLN series...

    #TODO is it necessary to put the example of test data here?
    """

    def __init__(self):  # Конструктор
        self.fio = '*** это тестовый пример! ***'
        self.history_number = 99998  # 99998 for testing.
        self.sample_id_no = "123456789"  # Sample ID No in Test Order Record.
        self.result_total = "All  Positive :))"  # Общая интерпретация результата, что печатается вверху на бланке.
        self.diagnosis = ""  # строка предполагаемых диагнозов по результатам анализов из БД анализатора.
        self.list_research = []
        self.an = []
        self.dict_rec = {}
        self.str_insert = ''
        self.result_text = ''

    # TODO test coming to MS SQL
    # FIXME: don't work!!! How to call this functions when object is created?
    def new_record(self):
        """ инициализация новой записи

        для тестирования
        
        :return: 
        """
        pass


class CONST:
    """ All constants for connections

    from anywhere
    """

    def __init__(self):  # Конструктор класса.
        self.analyser_id = 911  # сюда читаем из ini-файла.
        self.analyser_name = 'analyser_name01'  # сюда читаем из ini-файла.
        self.analyser_location = 'ГБСМП РнД'
        self.host = ''  # '127.0.0.1' or empty string - to accept connections on all available IPv4 interfaces.
        self.port = 50999
        self.sql_run = 'Asu pass=<***>'
        self.server = 'Asu-911'
        self.database = 'LabAutoResult'
        self.user_name = 'sa'
        self.password = '***'
        # self.path_log = '.'  # путь к логам
        # self.path_errlog = '.'  # путь к логам ошибок и файлу-контролю процесса (периодически пишется текущее время).
        self.mode = 'test_mode'
        self.max_cnt_param = 30  # ограничение кол-ва полей в [LabAutoResult].[dbo].[AnalyzerResults] - было 22/
        self.max_length_analyze_name = 16  # ограничение на длину названия анализа/
        self.num_run = 123
        self.pid = 999999  # pirocess id.


const = CONST()
