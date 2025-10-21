from faststream import FastStream

from service.fs_broker import broker
from service.fs_subs.user_sub import router as user_router

app = FastStream(broker)

broker.include_router(user_router)

