from dataclasses import dataclass


class RunConfiguration:
    args = []

    def __init__(self, name, **kwargs):
        self.name = name
        # this is gross but I don't really like it :)
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self.__dict__)
