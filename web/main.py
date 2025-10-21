from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web import groups, tickettype, halls, concerts, sales, auth, user_functions
from service.fs_subs.user_sub import router as user_router
from service.fs_broker import broker

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await broker.start()

    yield

    await broker.stop()



app = FastAPI(title="Ticket shop", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(tickettype.router)
app.include_router(halls.router)
app.include_router(concerts.router)
app.include_router(sales.router)
app.include_router(auth.router)
app.include_router(user_functions.router)


@app.get("/")
def top_page():
    return {"message": "Welcome to the box office"}


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)

