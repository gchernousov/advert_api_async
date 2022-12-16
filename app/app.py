import json
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import Callable, Awaitable

from models import Base, UserModel, TokenModel
from auth import hash_password, check_password
from config import PG_DSN


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
    item = await session.get(item_class, item_id)
    if item is None:
        raise http_error(web.HTTPNotFound, f'{item_class.__name__} is not found')
    return item


# views

async def login(request: web.Request):
    data = await request.json()
    if 'name' in data.keys() and 'password' in data.keys():
        query = select(UserModel).where(UserModel.name == data['name'])
        result = await request['session'].execute(query)
        user = result.scalar()
        if user is None:
            raise http_error(web.HTTPNotFound, 'user does not exist')
        if check_password(data['password'], user.password) is False:
            raise http_error(web.HTTPUnauthorized, 'password is incorrect')
        token = TokenModel(user=user)
        request['session'].add(token)
        await request['session'].commit()
        return web.json_response({'token': str(token.id)})
    else:
        raise http_error(web.HTTPBadRequest, 'name or password is missing')


class UserView(web.View):

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_item(UserModel, user_id, self.request['session'])
        return web.json_response({'id': user.id, 'name': user.name,
                                  'email': user.email, 'registration': str(user.registration_date),
                                  'advertisements': user.advertisement})

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
    print('------ APP START ------')
    yield
    print('------ APP STOP ------')
    await engine.dispose()


async def start_app():
    app = web.Application(middlewares=[session_middleware])
    app.cleanup_ctx.append(app_context)

    app.add_routes(
        [
            web.post('/login/', login),
            web.get("/users/{user_id:\d+}", UserView),
            web.post("/users/", UserView)
        ]
    )

    return app

if __name__ == '__main__':

    application = start_app()
    web.run_app(application)