from data.init_db import SessionDep
from sqlmodel import select
from models.db_models import Sales, SalesBase, SalesPublic, SalesUpdate


async def get_all_sales(common_params: dict, session: SessionDep):
<<<<<<< HEAD
    res = await session.exec(select(Sales).offset(common_params["skip"]).limit(common_params["limit"]))
    sales = res.all()
=======
    sales = session.exec(select(Sales).offset(common_params["skip"]).limit(common_params["limit"])).all()
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
    return sales


async def get_sale_by_id(id_sale: int, session: SessionDep):
<<<<<<< HEAD
    res = await session.exec(select(Sales).where(Sales.id_sale == id_sale))
    sale = res.first()
=======
    sale = session.exec(select(Sales).where(Sales.id_sale == id_sale)).first()
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
    if sale:
        return sale
    return None


async def creater_sale(sale_date: SalesBase, session: SessionDep):
    db_sale = Sales.model_validate(sale_date)
    session.add(db_sale)
    session.commit()
    session.refresh(db_sale)
    return db_sale


async def update_sale(id_sale: int, sale_update: SalesUpdate, session: SessionDep):
<<<<<<< HEAD
    sale = await session.get(Sales, id_sale)
=======
    sale = session.get(Sales, id_sale)
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
    if sale:
        sale_data = sale_update.model_dump(exclude_unset=True)
        sale.sqlmodel_update(sale_data)
        session.add(sale)
        session.commit()
        session.refresh(sale)
        return sale
    return None


async def delete_sale(id_sale, session: SessionDep):
<<<<<<< HEAD
    sale = await session.get(Sales, id_sale)
=======
    sale = session.get(Sales, id_sale)
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
    if sale:
        session.delete(sale)
        session.commit()
        return sale
    return None
