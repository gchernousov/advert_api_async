import json
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import Callable, Awaitable

from models import Base, UserModel
from auth import hash_password, check_password
from config import PG_DSN

print(f'>>>> in app.py :: {PG_DSN}')
engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@web.middleware
async def session_middleware(request: web.Request,
                             handler: Callable[[web.Request], Awaitable[web.Response]]) -> web.Response:
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response


def http_error(error_class, message):
    print('>>> RAISE ERROR:')
    print(error_class)
    print(message)
    print('---')
    raise error_class(
        text=json.dumps({'status': 'ERROR', 'description': message}),
        content_type='application/json',
    )


async def get_item(item_class, item_id, session):
    pass


# views

class UserView(web.View):

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await self.request['session'].get(UserModel, user_id)
        if user is None:
            raise http_error(web.HTTPNotFound, 'user is not found')
        return web.json_response({'id': user.id, 'name': user.name,
                                  'email': user.email, 'registration': str(user.registration_date),
                                  'advertisement': user.advertisement})

    async def post(self):
        user_data = await self.request.json()
        user_data['password'] = hash_password(user_data['password'])
        new_user = UserModel(**user_data)
        self.request['session'].add(new_user)
        await self.request['session'].commit()
        return web.json_response({'id': new_user.id})

    async def patch(self):
        pass

    async def delete(self):
        pass


async def app_context(app: web.Application):
    async with engine.begin() as connect:
        async with Session() as session:
            await session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            await session.commit()
        await connect.run_sync(Base.metadata.create_all)
    print('------START------')
    yield
    print('------STOP------')
    await engine.dispose()


async def start_app():
    app = web.Application(middlewares=[session_middleware])
    app.cleanup_ctx.append(app_context)

    app.add_routes(
        [
            web.get("/users/{user_id:\d+}", UserView),
            web.post("/users/", UserView)
        ]
    )

    return app

if __name__ == '__main__':

    application = start_app()
    web.run_app(application)