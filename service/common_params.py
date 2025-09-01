from typing import Annotated

from fastapi import Depends


async def common_params(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}

commonDep = Annotated[dict, Depends(common_params)]