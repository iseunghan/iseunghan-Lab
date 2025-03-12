from typing import Generator
from mock_db import MockDatabase

@pytest.fixture
def db() -> Generator[MockDatabase, None, None]:
    db = MockDatabase()
    db.connect()
    yield db
    db._entries = []
    db.disconnect()

def test_add_entry(db: MockDatabase) -> None:
    assert db.entries == []
    db.add({"name": "jon"})
    assert db.entries == [{"name": "jon"}]