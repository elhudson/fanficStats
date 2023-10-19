class Person(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(self)
        self.name=kwargs['name']
        self.id=kwargs['id']

class Fan(Person):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

class Actor(Person):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)