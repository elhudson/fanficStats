class Person(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self.name=kwargs['name']
        