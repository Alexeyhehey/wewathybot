#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import time
from aiogram import types, executor, Bot, Dispatcher
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
import hashlib
import pyowm
import asyncio
import aiohttp
from datetime import datetime
import pytz
from PIL import Image,  ImageFont, ImageFilter, ImageDraw
from func import *
import tg_analytic
from peremennaya import *
import pickle

def save():
    bd = open('database.py', 'wb')
    pickle.dump(stat_inline,bd)
    bd.close()

open_file = open('database.py', 'rb')
stat_inline = pickle.load(open('database.py', 'rb'))




logging.basicConfig(filename='log.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

bot = Bot('1284940013:AAEtTMFfJcz86Chgq-5cpfXuJRBri4O4qGs', parse_mode='HTML')#1058409836:AAHqeC0jIg8sLuPgttnVeJP1QVu5yok6yCo #1284940013:AAEtTMFfJcz86Chgq-5cpfXuJRBri4O4qGs
dp = Dispatcher(bot)

@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    try:
        owm = await connector(token=owm_token)
        place = inline_query.query
        observation = owm.weather_at_place(place)
        w = observation.get_weather()
        temp = w.get_temperature('celsius')["temp"]
        wind = w.get_wind()['speed']
        detailed_status = w.get_detailed_status()

        if place != '':
            check, obs, speed, temp, max_, min_, status1 = await get_weather_inline_func(place=place, owm=owm)
            if check is True:
                text = ("В локации <b>" + place + "</b> сейчас " + status1 + "\nВетер – " + str(round(wind)) + " км\ч\n🌡 – " + str(round(temp)) + " ℃")
                input_content = InputTextMessageContent(text)
                result_id: str = hashlib.md5(place.encode()).hexdigest()
                item = InlineQueryResultArticle(
					id=result_id,
					title=f'Показать погоду в ' + place,
					input_message_content=input_content,
                    )
    except:
        print('cant check weather')
    try:
        stat_inline['stat'] += 1
        save()
        print('инлай был отправлен ' + place)
        await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)
    except Exception as e:
        print(e)







@dp.message_handler(commands=['start'])
async def start_message(message):
    id = message.from_user.id
    if id not in stat_inline['users']:
        stat_inline['users'].append(id)
        save()
    await statistics(message.chat.id, message.text)
    await message.answer("Привет!\n Доступные команды:\n/w *локация* для получения погоды\n/sunrise *Region/City* для получения времени рассвета\n@weathybot *локация* что бы отправить в любой чат\nДоп. информация по командам - /help")

@dp.message_handler(commands=['help'])
async def start_message(message):
	await statistics(message.chat.id, message.text)
	await message.answer('/w – Ввести /w *локация*\nПример: /w Киев.\nВведите тег бота и локацию, что бы бот отправил информацию о погоде в любой чат. Пример: @weathybot Киев \n/sunrsie – Время рассвета в выбранном городе региона. \nВыбор локации осуществляется путём прописания региона и города через /\nПример: /sunrise Europe/Kiev. Обязательно на английском! \n(Приплюсовать ч. пояс выбранной локации к итоговому времени)')


#idraw = ImageDraw.Draw(img)
#width, height = img.size

@dp.message_handler(commands=['w'])
async def w_message(message):
    owm = await connector(token=owm_token)
    place = message.get_args()
    if place != '':
        check, obs, speed, temp, max_, min_, status = await get_weather_func(place=place, owm=owm)
        if check is True:
            await aiohttp_file_downloader()
            to_save = await start_drawing(temp=round(temp), speed=round(speed), place=place, status=status)
            with open(to_save, 'rb') as photo:
                stat_inline['w_stat'] += 1
                save()
                await statistics(message.chat.id, message.text)
                await bot.send_photo(message.chat.id, photo)
        else:
            await message.answer('Такого города/Страны не существует')
    else:
        await message.answer('Неверное использование')


@dp.message_handler(commands=['sunrise'])
async def sunrise_message(message):
    owm = pyowm.OWM('ef10360ae36e154345f37afd1f0ce884', language = "ru")
    try:
        args = message.text.split(maxsplit=1)[1]
        IST = pytz.timezone(args)
    except:
        await bot.send_message(message.chat.id, "Неверный регион или город. \nПример: /sunrise Europe/Kiev")
        return
    try:
        place1 = args.split("/")[1]
    except:
        bot.send.message(message.chat.id, "Неправильное использование")
        return
    observation = owm.weather_at_place(place1)
    w = observation.get_weather()
    IST = pytz.timezone(args)
    sun = w.get_sunrise_time('iso')
    await statistics(message.chat.id, message.text)
    stat_inline['sunrise_stat'] += 1
    save()
    await bot.send_message(message.chat.id, 'Информация по восходу солнца в <b>' + place1 + '</b>: \n' + str(sun) + '\nЧасовой пояс указанной локации:\n' + str(datetime.datetime.now(IST)) + '\n(Прибавьте часовой пояс указанной локации к результату) ')



@dp.message_handler(lambda message: message.text.lower() == 'статистик', content_types=['text'])
async def stat_inline1(message):
    await message.answer('пользователей: ' + str(len(stat_inline['users'])) + '\nколичество инлайнов:' + str(stat_inline['stat']) + '\nКоличество /w: ' + str(stat_inline['w_stat']) + '\nколичество /sunrise: ' + str(stat_inline['sunrise_stat']))

@dp.message_handler(content_types=['text'])
async def handle_text(message):
	try:
		if message.text[:10] == 'статистика' or message.text[:10] == 'Cтатистика':
			st = message.text.split(' ')
			if 'txt' in st or 'тхт' in st:
				tg_analytic.analysis(st,message.chat.id)
				with open('%s.txt' %message.chat.id ,'r',encoding='UTF-8') as file:
					await bot.send_document(message.chat.id,file)
					tg_analytic.remove(message.chat.id)
			else:
				messages = tg_analytic.analysis(st,message.chat.id)
				await bot.send_message(message.chat.id, messages)
	except:
		await message.answer('упс')


if __name__ == '__main__':

	print('bot has been started')
	executor.start_polling(dp)
