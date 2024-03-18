from abc import ABC


class myInterface(ABC):
    def __init__(self, token) -> None:
        super().__init__()
        self.token = token


class myClass(myInterface):
    def __init__(self, token) -> None:
        super().__init__(token)


c = myClass(token=123)
print(c.token)
