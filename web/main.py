import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web import groups, tickets, halls, concerts, sales


app = FastAPI(title="Ticket shop")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(groups.router)
app.include_router(tickets.router)
app.include_router(halls.router)
app.include_router(concerts.router)
app.include_router(sales.router)

@app.get("/")
def top_page():
    return {"message": "Welcome to the box office"}


if __name__ == "__main__":
    uvicorn.run('main:app', reload=True)

