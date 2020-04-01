import asyncio
import aiohttp
from aiohttp import web
import json
import os
import generate_poster
import requests

TOKEN = os.getenv('TOKEN')
API_URL = 'https://api.telegram.org/bot%s/sendMessage' % TOKEN
PHOTO_URL = 'https://api.telegram.org/bot%s/sendPhoto' % TOKEN
GET_FILE_URL = 'https://api.telegram.org/bot%s/getFile' % TOKEN
FILE_CONTENT = 'https://api.telegram.org/file/bot%s/' % TOKEN
posters = {}

inlineTextColors = [[
  { 'text': '🤍', 'callback_data': 'FFFFFF' },
  { 'text': '💙', 'callback_data': '300ff' },
  { 'text': '💚', 'callback_data': 'df00' },
  { 'text': '🧡', 'callback_data': 'ff7400' },
  { 'text': '💜', 'callback_data': 'ae00aa' }],
  [{ 'text': '💖', 'callback_data': 'ff00d1' },
  { 'text': '🖤', 'callback_data': '000000' },
  { 'text': '💛', 'callback_data': 'fff245' },
  { 'text': '♥️', 'callback_data': 'f00026' }
]]
fonts = [
    [{ 'text': 'Comic', 'callback_data': 'Comic2.ttf' },
    { 'text': 'Curve', 'callback_data': 'Curve.otf' },
    { 'text': 'Slavic', 'callback_data': 'Slavic.ttf' }],
    [{ 'text': 'Soviet', 'callback_data': 'Soviet.ttf' },
    { 'text': 'Tahoma', 'callback_data': 'Tahoma.ttf' },
    { 'text': 'Italic', 'callback_data': 'Italic.ttf' }]
]
inlineMessageColors = [[
  { 'text': '🤍', 'callback_data': 'FFFFFF' },
  { 'text': '💙', 'callback_data': 'cec8ff' },
  { 'text': '💚', 'callback_data': '9cffbc' },
  { 'text': '🧡', 'callback_data': 'ffd4bc' },
  { 'text': '💜', 'callback_data': 'ff9bff' },
  { 'text': '💖', 'callback_data': 'ff81ff' },
  #{ 'text': '🖤', 'callback_data': '000000' },
  { 'text': '💛', 'callback_data': 'fff88e' },
  { 'text': '♥️', 'callback_data': 'ff8181' }
]]
inlineMessageLogos = [[
  { 'text': 'None ', 'callback_data': '-' },
  { 'text': '🍭', 'callback_data': 'lolypop' },
  { 'text': '🦄', 'callback_data': 'unicorn' }
]]

def checkChat(chat):
    res = ('photo_text' in chat) and ('logo' in chat) and ('photo' in chat) and ('background_color' in chat) and ('text_color' in chat) and ('font' in chat)
    print(res)
    return res

async def sendData(message, url=API_URL):
    headers = {
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.post(url,
                        data=json.dumps(message),
                        headers=headers) as resp:
            try:
                assert resp.status == 200
            except:
                return web.Response(status=500)
    return web.Response(status=200)


async def generatePoster(chat_id):
    global posters
    global GET_FILE_URL
    chat = posters[chat_id]
    GET_FILE_URL1=GET_FILE_URL+'?file_id='+chat['photo']

    headers = {
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(GET_FILE_URL1,
                        headers=headers) as resp:
            try:
                assert resp.status == 200
                res = json.loads(await resp.text())
                file_path = res['result']['file_path']
                url = FILE_CONTENT+file_path
                if not 'logo' in chat:
                    logo = ''
                else:
                    logo = chat['logo']
                byte_io = generate_poster.generate_poster(background=chat['background_color'], 
                text=chat['photo_text'], 
                text_color=chat['text_color'],
                font=chat['font'],
                logo_pic=logo,
                url=url)

                files = {'photo': byte_io}
                data = {'chat_id' : chat_id}

                r = requests.post(PHOTO_URL, files=files, data=data)
                print(r.status_code, r.reason, r.content)
            except:
                return web.Response(status=200)
    return web.Response(status=200)
    

async def handler(request):
    global posters
    data = await request.json()
    print(posters)
    if 'callback_query' in data:
        callback = data['callback_query']
        value = callback['data']
        chat_id = callback['message']['chat']['id']
        text = callback['message']['text']

        if not chat_id in posters:
            posters[chat_id] = {}

        chat = posters[chat_id]
        print(text)
        if text == '🍭  Цвет фона | Background':
            chat['background_color'] = value

        if text == '🍭 Цвет текста | Text color':
            chat['text_color'] = value

        if text == '🍭 Font family':
            chat['font'] = value

        if text == '🍭 Лого | Logo':
            chat['logo'] = value      

        if checkChat(chat):
            await generatePoster(chat_id) 

        return web.Response(status=200) 
    else:
        msg = data['message']        
        chat_id = msg['chat']['id']
        if not chat_id in posters:
            posters[chat_id] = {}
        chat = posters[chat_id]

        if 'text' in msg:
            text = msg['text']

            if text == '/start':
                message = {
                    'chat_id': chat_id,
                    'text': '🍭 Картинка | Image'
                }
                await sendData(message)

            elif text == '/done':
                print(chat)
                if checkChat(chat):
                    await generatePoster(chat_id)
                else:
                    message = {
                        'chat_id': chat_id,
                        'text': '🍭 Генерация еще не закончена | Not done yet'
                    }
                    await sendData(message)

            elif text == '/clear':
                posters[chat_id] = {}
                message = {
                    'chat_id': chat_id,
                    'text': 'Chat is cleared'
                }
                await sendData(message)

            else:
                chat['photo_text'] = text
                if checkChat(chat):
                    await generatePoster(chat_id)

        if 'photo' in msg:
            chat['photo'] = msg['photo'][0]['file_id']

            message = {
                'chat_id': msg['chat']['id'],
                'text': '🍭  Цвет фона | Background',
                'reply_markup': json.dumps({ 'inline_keyboard': inlineMessageColors })
            }
            await sendData(message)

            message = {
                'chat_id': chat_id,
                'text': '🍭 Font family',
                'reply_markup': json.dumps({ 'inline_keyboard': fonts })
            }
            await sendData(message) 

            message = {
                'chat_id': chat_id,
                'text': '🍭 Цвет текста | Text color',
                'reply_markup': json.dumps({ 'inline_keyboard': inlineTextColors })
            }
            await sendData(message)

            message = {
                'chat_id': chat_id,
                'text': '🍭 Лого | Logo',
                'reply_markup': json.dumps({ 'inline_keyboard': inlineMessageLogos })
            }
            await sendData(message)

            message = {
                'chat_id': chat_id,
                'text': '🍭 Введите текст'
            }
            await sendData(message)

    return web.Response(status=200)

async def test(request): 
    return web.Response(text="Hello, world")

async def init_app(loop):
    app = web.Application(loop=loop, middlewares=[])
    app.router.add_post('/api/v1', handler)
    app.router.add_get('/', test)
    return app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        app = loop.run_until_complete(init_app(loop))
        web.run_app(app, host='0.0.0.0', port=os.environ.get('PORT', 8080))
    except Exception as e:
        print('Error create server: %r' % e)
    finally:
        pass
    loop.close()