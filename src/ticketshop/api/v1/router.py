from fastapi import APIRouter
from . import auth, concerts, halls, groups, tickettype, sales

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(concerts.router)
api_router.include_router(halls.router)
api_router.include_router(groups.router)
api_router.include_router(tickettype.router)
api_router.include_router(sales.router)