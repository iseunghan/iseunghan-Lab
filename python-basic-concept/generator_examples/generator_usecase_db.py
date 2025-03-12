from typing import Generator

from fastapi import FastAPI, APIRouter

from mock_db import MockDatabase

app = FastAPI()
router = APIRouter()


@router.get("/entries")
async def get_entries() -> list[dict]:
    """
    단점: db 생성 및  connection, disconnect를 직접 해줘야 함.
    """
    db = MockDatabase()
    db.connect()
    entries = db.entries
    db.disconnect()
    return entries


def get_db() -> Generator[MockDatabase, None, None]:
    db = MockDatabase()
    db.connect()
    yield db
    db.disconnect()


@router.get("/entries-enhanced")
async def get_entries_enhanced(db: MockDatabase = Depends(get_db)) -> list[dict]:
    """
    Depends + Generator를 이용하여 FastAPI가 자동적으로 lazeinit을 해주고, destory까지 해준다!
    """
    return db.entries
