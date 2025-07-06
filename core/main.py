from fastapi import FastAPI
from typing import Union
from database import create_tables

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def main():
    create_tables()


if __name__ == '__main__':
    main()