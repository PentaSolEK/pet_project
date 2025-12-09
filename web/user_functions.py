from datetime import datetime

from fastapi import Depends, APIRouter, HTTPException
from typing import Annotated

from data.init_db import SessionDep
from models.other_models import BuyTicketForm
from data.concerts import get_concert_by_name, get_concert_id_by_musicgroup, get_concert_by_id
from data.users import get_user_by_email, update_user
from models.db_models import UsersUpdate, SalesBase, Concert
from data.sales import creater_sale
from data.tickets_type import get_ticket_type_by_name
from data.tickets import get_ticket
from data.hall_ticket_type import get_hall_ticket_type
from data.groups import get_musicgroup_by_name

router = APIRouter(prefix="/user_funcs", tags=["user_funcs"])


@router.post("/buy_ticket", description="Форма для покупки билетов")
async def buy_ticket(data: Annotated[BuyTicketForm, Depends()], session:SessionDep):
    (concert_name, ticket_count, ticket_type,
     user_mail, user_name, user_last_name, user_age) = (data.concert_name,
                                                        data.ticket_count,
                                                        data.ticket_type,
                                                        data.user_mail,
                                                        data.user_name,
                                                        data.user_last_name,
                                                        data.user_age)
    user = await get_user_by_email(user_mail, session)
    if not user:
        raise HTTPException(status_code=404, detail="User is not registered!")
    if (user_name != user.name) or (user_last_name != user.surname) or (user_age != user.age):
        data_to_update = UsersUpdate(name=user_name, surname=user_last_name, age=user_age)
        res = await update_user(user.id_user, data_to_update, session)
        if not res:
            raise HTTPException(status_code=404, detail="Ошибка при обновлении данных пользователя!")

    concert_data = await get_concert_by_name(data.concert_name, session)
    if not concert_data:
        raise HTTPException(status_code=404, detail=f"Concert with name {data.concert_name} not found!")
    concert_id = concert_data.id_concert
    hall_id = concert_data.id_hall

    ticket_type_data = await get_ticket_type_by_name(ticket_type, session)
    if not ticket_type_data:
        raise HTTPException(status_code=404, detail=f"Ticket type {ticket_type} not found!")

    hall_ticket_type_data = await get_hall_ticket_type(id_hall=hall_id,
                                                       id_ticket_type=ticket_type_data.id_type,
                                                       session=session)
    if not hall_ticket_type_data:
        raise HTTPException(status_code=404, detail=f"Hall ticket type not found!")

    ticket_data = await get_ticket(concert_id, hall_ticket_type_data.id_hall_ticketTypes, session)
    if not ticket_data:
        raise HTTPException(status_code=404, detail=f"Ticket not found!")
    sale_data = SalesBase(id_user=user.id_user,
                          id_ticket=ticket_data.id_ticket,
                          count=ticket_count, sale_date=datetime.now())
    sale = await creater_sale(sale_data, session)
    return sale

@router.get("/filter_concert_buy_group", description="Возвращает все концерты выбранной группы")
async def get_concert_by_group_name(musicgroup: str, session: SessionDep) -> list[Concert]:
    musicgroup_in_db = await get_musicgroup_by_name(musicgroup, session)
    if not musicgroup_in_db:
        raise HTTPException(status_code=404, detail=f"Музыкальная группа {musicgroup} не найдена!")
    musicgroup_id = musicgroup_in_db.id_group
    concerts = await get_concert_id_by_musicgroup(musicgroup_id, session)
    if not concerts:
        raise HTTPException(status_code=404, detail=f"Концерты музыкальной группы {musicgroup} не найдены!")
    concerts_lst: list[Concert] = []
    for concert in concerts:
        concerts_lst.append(await get_concert_by_id(concert.id_concert, session))
    return concerts_lst




