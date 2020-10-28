#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import datetime
import os
import pandas as pd
import asyncio
import pyowm
import aiohttp
from PIL import Image,  ImageFont, ImageFilter, ImageDraw


users_type = {
    1: 'пользователь',
    2: 'пользователя',
    3: 'пользователя',
    4: 'пользователя'
}
day_type = {
    1: 'день',
    2: 'дня',
    3: 'дня',
    4: 'дня'
}

owm_token = 'ef10360ae36e154345f37afd1f0ce884'

# remove txt file
def remove(user_id):
    path = os.getcwd() + '/%s.txt' % user_id
    os.remove(path)


'''async def sunrise(place, owm):

    try:
        obs = owm.weather_at_place(place)
        w = obs.get_weather()
        IST = w.get_reference_time(timeformat='iso')
        sun = w.get_sunrise_time('iso')

        return True, sun

    except Exception as exc:


        return False, None'''


async def start_drawing(temp, speed, place, status, img="pic.jpg", font='gtq907eh.ttf', size=80, size2=178, size3=50, size4=76, padding=30, to_save='pic2.jpg'):

    with Image.open(img) as image:

        draw = ImageDraw.Draw(image)
        template_width, template_height = image.size

        status_font = ImageFont.truetype(font, size)
        place_font = ImageFont.truetype(font, size2)
        tempp_font = ImageFont.truetype(font, size)
        windd_font = ImageFont.truetype(font, size4)
        text_widthplace = place_font.getsize(place)[0]
        text_widthstatus = status_font.getsize(status)[0]

        while text_widthplace >= template_width  - padding * 2:                    #цикл для place
            place_font = ImageFont.truetype(font, size2)
            text_widthplace = place_font.getsize(place)[0]
            size2 -= 1
            await asyncio.sleep(0)

        while text_widthstatus >= template_width - padding * 2:                        #цикл для status
            status_font = ImageFont.truetype(font, size)
            text_widthstatus = status_font.getsize(status)[0]
            size-=1
            await asyncio.sleep(0)

        draw.text(((template_width - text_widthplace) / 2, 521), place, font=place_font, fill=(144, 162, 174, 255))
        draw.text(((template_width - text_widthstatus) / 2, template_height * 0.6), status, font=status_font, fill=(141, 132, 132))
        draw.text((360,845), f'{temp} °С', font=tempp_font, fill=(141, 132, 132))
        draw.text((374,1005), f'{speed}км/ч', font=windd_font, fill=(97, 95, 150))

        image.save(to_save)

    return to_save







# download files and write content

async def aiohttp_file_downloader(url='https://linx.li/s/gtq907eh.ttf', fileopen='gtq907eh.ttf'):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(fileopen, 'wb') as file:
                file.write(await resp.content.read())



# get weather at place and return data

async def get_weather_func(place, owm):
    try:
        obs = owm.weather_at_place(place)
        w = obs.get_weather()
        return True, obs, w.get_wind()['speed'], w.get_temperature('celsius')["temp"], w.get_temperature('celsius')["temp_max"], w.get_temperature('celsius')["temp_min"], w.get_detailed_status()
    except Exception as exc:
        return False, None, None, None, None, None, None

async def get_weather_inline_func(place, owm):
    try:
        obs = owm.weather_at_place(place)
        w = obs.get_weather()
        detailed_status = w.get_detailed_status()
        if detailed_status == 'гроза':
            status1 = 'гроза 🌩'
        elif detailed_status == 'переменная облачность':
            status1 = 'переменная облачность 🌤'
        elif detailed_status == 'небольшая облачность':
            status1 = 'небольшая облачность ⛅️'
        elif detailed_status == 'пасмурно':
            status1 = 'пасмурно ☁️'
        elif detailed_status == 'ясно':
            status1 = 'ясно ☀️'
        elif detailed_status == 'облачно с прояснениями':
            status1 = 'облачно с прояснениями ⛅️'
        elif detailed_status == 'небольшой дождь':
            status1 = 'небольшой дождь 🌦'
        elif detailed_status == 'проливной дождь':
            status1 = 'проливной дождь 🌧'
        elif detailed_status == 'небольшой проливной дождь':
            status1 = 'небольшой проливной дождь 🌧'
        elif detailed_status == 'снег':
            status1 = 'снег 🌨'
        else:
            status1 = detailed_status

        return True, obs, w.get_wind()['speed'], w.get_temperature('celsius')["temp"], w.get_temperature('celsius')["temp_max"], w.get_temperature('celsius')["temp_min"], status1
    except Exception as exc:
        return False, None, None, None, None, None, None


async def statistics(user_id, command):
    with open('data.csv', 'a', newline="") as file:
        wr =csv.writer(file, delimiter=';')
        wr.writerow([datetime.datetime.today().strftime("%Y-%m-%d"), user_id, command])


# connect to owm
async def connector(token, lang='ru'):
    return pyowm.OWM(token, language = lang)



# make report
