class MockDatabase:
    def __init__(self) -> None:
        self._entries: list[dict] = []
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def _connection_check(self):
        if not self._connected:
            raise RuntimeError("Database is disconnected")

    def add(self, entry: dict) -> None:
        self._connection_check()
        self._entries.append(entry)

    @property
    def entries(self)-> list[dict]:
        self._connection_check()
        return self._entries