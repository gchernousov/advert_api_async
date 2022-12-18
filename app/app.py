import json
import datetime
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.exc import StatementError
from typing import Callable, Awaitable

from models import Base, UserModel, TokenModel, AdvertisementModel
from auth import hash_password, check_password
from config import PG_DSN, TOKEN_TTL


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
    raise error_class(
        text=json.dumps({'status': 'ERROR', 'description': message}),
        content_type='application/json',
    )


def show_advertisements(advertisements):
    adv_list = []
    for advertisement in advertisements:
        adv_data = {'id': advertisement.id, 'title': advertisement.title, 'created': str(advertisement.created)}
        adv_list.append(adv_data)
    return adv_list


async def get_item(item_class, item_id, session):
    try:
        item = await session.get(item_class, item_id)
    except StatementError:
        raise http_error(web.HTTPForbidden, f'incorrect format of {item_class.__name__}')
    if item is None:
        raise http_error(web.HTTPNotFound, f'{item_class.__name__} is not found')
    return item


async def authentication(headers, session):
    token = headers.get('Token')
    if token is None:
        raise http_error(web.HTTPForbidden, 'need Token for this request')
    token = await get_item(TokenModel, token, session)
    if token.creation_time + datetime.timedelta(seconds=TOKEN_TTL) <= datetime.datetime.now():
        raise http_error(web.HTTPForbidden, 'token is expired')
    return token.user_id


async def check_user_owner(user_id, user_object_id, session):
    user_object = await get_item(UserModel, user_object_id, session)
    if user_object.id != user_id:
        raise http_error(web.HTTPUnauthorized, 'permission denied')
    return user_object


async def check_advertisement_owner(user_id, adv_id, session):
    advertisement = await get_item(AdvertisementModel, adv_id, session)
    if advertisement.user_id != user_id:
        raise http_error(web.HTTPUnauthorized, 'permission denied')
    return advertisement


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
        adv_list = show_advertisements(user.advertisement)
        return web.json_response({'id': user.id, 'name': user.name,
                                  'email': user.email, 'registration': str(user.registration_date),
                                  'advertisements': adv_list})

    async def post(self):
        user_data = await self.request.json()
        if 'name' in user_data.keys() and 'password' in user_data.keys():
            user_data['password'] = hash_password(user_data['password'])
            new_user = UserModel(**user_data)
            self.request['session'].add(new_user)
            await self.request['session'].commit()
            return web.json_response({'id': new_user.id})
        else:
            raise http_error(web.HTTPBadRequest, 'name or password is missing')

    async def patch(self):
        user_object_id = int(self.request.match_info['user_id'])
        user_id = await authentication(self.request.headers, self.request['session'])
        user_object = check_user_owner(user_id, user_object_id, self.request['session'])
        user_data = await self.request.json()
        if 'password' in user_data.keys():
            user_data['password'] = hash_password(user_data['password'])
        for field, value in user_data.items():
            setattr(user_object, field, value)
        self.request['session'].add(user_object)
        await self.request['session'].commit()
        return web.json_response({'status': 'user is changed'})

    async def delete(self):
        user_object_id = int(self.request.match_info['user_id'])
        user_id = await authentication(self.request.headers, self.request['session'])
        user_object = check_user_owner(user_id, user_object_id, self.request['session'])
        await self.request['session'].delete(user_object)
        await self.request['session'].commit()
        return web.json_response({'status': 'user is delete'})


class AdvertisementView(web.View):

    async def get(self):
        adv_id = int(self.request.match_info['adv_id'])
        advertisement = await get_item(AdvertisementModel, adv_id, self.request['session'])
        return web.json_response({'id': advertisement.id, 'title': advertisement.title,
                                  'description': advertisement.description,
                                  'created': str(advertisement.created),
                                  'user id': advertisement.user_id})

    async def post(self):
        user_id = await authentication(self.request.headers, self.request['session'])
        adv_data = await self.request.json()
        if 'title' in adv_data.keys() and 'description' in adv_data.keys():
            adv_data['user_id'] = user_id
            new_advertisement = AdvertisementModel(**adv_data)
            self.request['session'].add(new_advertisement)
            await self.request['session'].commit()
            return web.json_response({'id': new_advertisement.id})
        else:
            raise http_error(web.HTTPBadRequest, 'title or description is missing')

    async def patch(self):
        user_id = await authentication(self.request.headers, self.request['session'])
        adv_id = int(self.request.match_info['adv_id'])
        advertisement = await check_advertisement_owner(user_id, adv_id, self.request['session'])
        new_data = await self.request.json()
        for field, value in new_data.items():
            setattr(advertisement, field, value)
        self.request['session'].add(advertisement)
        await self.request['session'].commit()
        return web.json_response({'status': 'advertisement is changed'})

    async def delete(self):
        user_id = await authentication(self.request.headers, self.request['session'])
        adv_id = int(self.request.match_info['adv_id'])
        advertisement = await check_advertisement_owner(user_id, adv_id, self.request['session'])
        await self.request['session'].delete(advertisement)
        await self.request['session'].commit()
        return web.json_response({'status': 'advertisement is delete'})


async def app_context(app: web.Application):
    async with engine.begin() as connect:
        async with Session() as session:
            await session.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
            await session.commit()
        await connect.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


async def start_app():
    app = web.Application(middlewares=[session_middleware])
    app.cleanup_ctx.append(app_context)

    app.add_routes(
        [
            web.post('/login/', login),
            web.get('/users/{user_id:\d+}', UserView),
            web.post('/users/', UserView),
            web.patch('/users/{user_id:\d+}', UserView),
            web.get('/advertisements/{adv_id:\d+}', AdvertisementView),
            web.post('/advertisements/', AdvertisementView),
            web.patch('/advertisements/{adv_id:\d+}', AdvertisementView),
            web.delete('/advertisements/{adv_id:\d+}', AdvertisementView)
        ]
    )

    return app


if __name__ == '__main__':

    application = start_app()
    web.run_app(application)
