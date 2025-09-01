from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends

from data.init_db import SessionDep
from models.db_models import SalesBase, SalesPublic, SalesUpdate
from data import sales
from service.common_params import commonDep

router = APIRouter(prefix="/sales", tags=["sales"])



@router.get("/")
async def get_all_sales(session: SessionDep, commons: commonDep):
    result = await sales.get_all_sales(commons, session)
    return result


@router.get("/{sale_id}")
async def get_sale_by_id(sale_id: int, session: SessionDep):
    if result := await sales.get_sale_by_id(sale_id, session):
        return result

    raise HTTPException(status_code=404, detail="Sale not found")


@router.post("/sale", response_model=SalesPublic)
async def create_sale(sale_data: Annotated[SalesBase, Depends()], session: SessionDep):
    result = await sales.creater_sale(sale_data, session)
    return result


@router.put("/{sale_id}", response_model=SalesPublic)
async def update_sale(sale_id: int, update_data: Annotated[SalesUpdate, Depends()], session: SessionDep):
    if result := await sales.update_sale(sale_id, update_data, session):
        return result
    raise HTTPException(status_code=404, detail="Sale not found")


@router.delete("/{sale_id}", response_model=SalesPublic)
async def delete_sale(sale_id: int, session: SessionDep):
    if result := await sales.delete_sale(sale_id, session):
        return result
    raise HTTPException(status_code=404, detail="Sale not found")