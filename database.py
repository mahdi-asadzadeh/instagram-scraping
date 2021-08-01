import dataset


class MetaSingleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super().__call__(*args, **kwargs)
        return cls._instance[cls]


class DataBaseConnector(metaclass=MetaSingleton):
    def __init__(self, data_base_file_name: str):
        self.db = dataset.connect(f'sqlite:///{data_base_file_name}.db')


class DataBaseController:
    def __init__(self, data_base_file_name: str):
        self.db = DataBaseConnector(data_base_file_name).db

    def processor(self, *args, **kwargs):
        self.db[kwargs['table_name']].insert(kwargs)
 