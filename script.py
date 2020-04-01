import asyncio
import aiohttp
from aiohttp import web
import json

TOKEN = 'bot985067508:AAGNcsflc6f1PSD_p5qUIPt4OkaiJ6qpwgw'
API_URL = 'https://api.telegram.org/bot%s/sendMessage' % TOKEN

async def handler(request):
    data = await request.json()
    headers = {
        'Content-Type': 'application/json'
    }
    message = {
        'chat_id': data['message']['chat']['id'],
        'text': data['message']['text']
    }
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.post(API_URL,
                                data=json.dumps(message),
                                headers=headers) as resp:
            try:
                assert resp.status == 200
            except:
                return web.Response(status=500)
    return web.Response(status=200)

async def init_app(loop):
    app = web.Application(loop=loop, middlewares=[])
    app.router.add_post('/api/v1', handler)
    return app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        app = loop.run_until_complete(init_app(loop))
        web.run_app(app, host='0.0.0.0', port=80)
    except Exception as e:
        print('Error create server: %r' % e)
    finally:
        pass
    loop.close()