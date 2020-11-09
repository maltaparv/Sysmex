# ClassLib 2020-10-07
class RECORD:
    """ Data received from analyser SYSMEX XLN series...

    #TODO is it necessary to put the example of test data here?
    """

    def __init__(self):  # Конструктор
        self.fio = '*** это тестовый пример! ***'
        self.history_number = -911  # 99998 for testing - is it coming to MS SQL?
        self.list_research = []
        self.an = []
        self.dict_rec = {}

    fio = 'Тестовый О.Н.'
    history_number = 99998  # for testing - is it coming to MS SQL?

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

    def __init__(self):  # Конструктор класса
        self.analyser_id = 911  # сюда читаем из ini-файла
        self.analyser_name = 'analyser_name01'  # сюда читаем из ini-файла
        self.analyser_location = 'ГБСМП РнД'
        self.host = ''  # '127.0.0.1' or empty string - to accept connections on all available IPv4 interfaces.
        self.port = 50987
        self.sql_run = 'Asu pass=<***>'
        self.path_log = '.'  # директория запуска
        self.path_errlog = '.'  # директория запуска
        self.mode = 'test_mode'
        self.num_run = 123
        self.last_run = 'today:))'


const = CONST()
