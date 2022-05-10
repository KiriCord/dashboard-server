import asyncio
from typing import Optional

import uvicorn as uvicorn
from fastapi import FastAPI
from grad_api.common.grad_connection import GradConnection
from pydantic import BaseModel
from sql_parser import parse_select
from sse_starlette import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import random

app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

con = GradConnection()


class GradDate(BaseModel):
    month: int
    year: int

    def toGradDateStr(self):
        return f"{self.year},{self.month}"

#------для любых таблиц
# @app.post("/{table}/{well_id}")
# async def read_universal(table, well_id:str, begin_date: GradDate, end_date: GradDate):
#     return con.select(parse_select(f'select * from {table} where well="{well_id}" order by dt limit mmbegin=({begin_date.toGradDateStr()}) and mmend=({end_date.toGradDateStr()}) fetch field="Овальное"'))
#
#
# @app.get("/{table}/{well_id}")
# async def read_universal(table, well_id):
#     return con.select(parse_select(f'select * from {table} where well="{well_id}" order by dt fetch field="Овальное"'))
#----------------------


@app.post("/mer/{well_id}")
async def read_mer(well_id:str, begin_date: GradDate, end_date: GradDate):
    return con.select(parse_select(f'select dt, charwork, gas, liq, oil, priem from mer where well="{well_id}" order by dt limit mmbegin=({begin_date.toGradDateStr()}) and mmend=({end_date.toGradDateStr()}) fetch field="Овальное"'))


@app.get("/mer/{well_id}")
async def read_mer(well_id):
    return con.select(parse_select(f'select dt, charwork, gas, liq, oil, priem from mer where well="{well_id}" order by dt fetch field="Овальное"'))


@app.get("/mersumcum/{well_id}")
async def read_mersumcum(well_id):
    return con.select(parse_select(f'select ql, qn, zak from mersumcum where well="{well_id}" order by dt fetch field="Овальное"'))


wells = [data.well for data in con.select(parse_select('select well from wells fetch field="Овальное"'))]
#wells = ["999_2550"];


@app.get("/events")
async def test(request: Request):
    async def new_mess():
        try:
            while True:
                 yield dict(data=random.choice(wells))
                 await asyncio.sleep(10)
        except asyncio.CancelledError as e:
            print(f"Disconnected from client (via refresh/close) {request.client}")
            raise e

    return EventSourceResponse(new_mess())


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
