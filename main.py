import os
import requests
import logging
import shutil
from datetime import datetime
import asyncio
from config import token
from aiogram import Bot, Dispatcher, types, executor

bot = Bot(token=token)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

host = 'http://127.0.0.1:8000'

with open("data/channels.txt", 'r') as file:
    channels = file.readlines()
with open("data/admins.txt", 'r') as file:
    admins = file.readlines()


async def set_default_commands():
    await dp.bot.set_my_commands([types.BotCommand("start", "Запустить бота"),
                                  types.BotCommand("give_id", "Показать id пользователя"),
                                  types.BotCommand("add_admins", "Добавить админов "
                                                                 "(выполняется только для админов)"),
                                  types.BotCommand("delete_admins", "Удалить админов "
                                                                    "(выполняется только для админов)"),
                                  types.BotCommand('add_channels', "Добавить каналы "
                                                                   "(выполняется только для админов)"),
                                  types.BotCommand('delete_channels', "Удалить каналы "
                                                                      "(выполняется только для админов)")])


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await set_default_commands()
    response = requests.post(f'{host}/staff_api/user/loading/{hash(message.from_user.id)}/{message.from_user.username}/'
                             f'{0}')
    if response:
        with open('data/users.txt', 'a') as f:
            f.write('\n' + message.from_user.id)
        keyboard = []
        flag = False
        for i in channels:
            if not flag:
                username = f'@{i[i.rfind("/") + 1:]}'
                chat = await bot.get_chat(username)
                user_channel_status = await bot.get_chat_member(chat_id=chat.id, user_id=message.from_user.id)
                if user_channel_status.status != "left":
                    keyboard.append([types.InlineKeyboardButton(text='Подписаться', url=i)])
                else:
                    flag = True
            else:
                keyboard.append([types.InlineKeyboardButton(text='Подписаться', url=i)])
        if flag:
            keyboard.append([types.InlineKeyboardButton(text='Проверить подписки', callback_data="check_subscribes")])
            await message.answer('Рады видеть тебя!\n\nМы первое колесо фортуны в Telegram, которое дает скидки на'
                                 ' продукты локальных и отечественных брендов!\n\nПрокрути колесо и узнай,'
                                 ' что мы приготовили для тебя сегодня!\n\nНе забудь подписаться на наших спонсоров:',
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard))
        else:
            response = requests.post(f'{host}/staff_api/user/spin_update/{message.from_user.id}/{1}')
            if response:
                keyboard = [[types.InlineKeyboardButton('Крутить колесо',
                                                        url="https://t.me/fortuna_wheel_bot/wheel")]]
                await message.answer("Отлично! Теперь мы можем начинать!\n\n"
                                     "Давай немного ознакомимся с правилами:\n\n"
                                     "1️⃣Призы выдают спонсоры, а не владельцы рулетки."
                                     " Ссылки на их каналы ты получил при подписке."
                                     " Администраторов можно найти в описаниях этих каналов.\n\n"
                                     "2️⃣Все призы фиксируются в базе данных,"
                                     " которая передается спонсорам после конкурса для предотвращения обмана."
                                     " Это наша мера безопасности.\n\n"
                                     "3️⃣Не забудь включить уведомления для бота,"
                                     " чтобы каждый день выигрывать классные призы!"
                                     " Не все зависит от спонсоров, поэтому заявки на проблемы с приложением можно"
                                     " оставлять здесь. Если у тебя есть идеи по улучшению, делись!\n@grmnsupport",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard))
            else:
                await message.answer("Произошла не придвиденная ошибка. Работы уже ведутся.")
                await bot.send_message(message.from_user.id, 'Произошла ошибка\n"Http статус:",'
                                                             f' {response.status_code}, "(", {response.reason}, ")")')
    else:
        await message.answer("Произошла не придвиденная ошибка. Работы уже ведутся.")
        await bot.send_message(message.from_user.id, 'Произошла ошибка\n"Http статус:",'
                                                     f' {response.status_code}, "(", {response.reason}, ")")')


@dp.callback_query_handler()
async def check_subscribes(call: types.CallbackQuery):
    await call.message.answer("Вы ещё не подписались на всех спонсоров, а значит пока не можете учавствовать"
                              " в розыгрыше")
    await start(call.message)


@dp.message_handler(commands=["give_id"])
async def give_id(message: types.Message):
    await message.answer(message.from_user.id)


@dp.message_handler(commands=["add_admins"])
async def add_admins(message: types.Message):
    if str(message.from_user.id) in admins:
        ids = message.text.split()
        text = ""
        with open("data/admins.txt", 'a') as admin:
            for i in ids[1:]:
                admin.write('\n' + i)
                text += i + ', '
        await message.reply(f"Пользователи {text[:-2]} успешно добавлены")
    else:
        await message.answer("Для выполнения этой команды нужны права администратора.")


@dp.message_handler(commands=["delete_admins"])
async def delete_admins(message: types.Message):
    if str(message.from_user.id) in admins:
        ids = message.text.split()
        text = ''
        for i in ids[1:]:
            if i == '@all':
                admins.clear()
                break
            if i in admins:
                admins.pop(admins.index(i))
                text += i + ', '
        with open("data/admins.txt", 'w') as admin:
            admin.write(admins[0])
            for i in admins[1:]:
                admin.write('\n' + i)
        await message.reply(f"Пользователи {text[:-2]} успешно удалены")
    else:
        await message.answer("Для выполнения этой команды нужны права администратора.")


@dp.message_handler(commands=["add_channels"])
async def add_channels(message: types.Message):
    if str(message.from_user.id) in admins:
        ids = message.text.split()
        text = ""
        with open("data/channels.txt", 'a') as channel:
            for i in ids[1:]:
                channel.write('\n' + i)
                text += i + ', '
        await message.reply(f"Каналы {text[:-2]} успешно добавлены")
        with open('data/users.txt') as f:
            users = f.readlines()
        for i in users:
            response = requests.post(f'{host}/staff_api/user/spin_update/{i}/{1}')
            if not response:
                await message.answer("Произошла не придвиденная ошибка. Работы уже ведутся.")
                await bot.send_message(message.from_user.id, 'Произошла ошибка\n"Http статус:",'
                                                             f' {response.status_code}, "(", {response.reason},'
                                                             f' ")")')
                break
            else:
                await message.answer("Произошла не придвиденная ошибка. Работы уже ведутся.")
                await bot.send_message(message.from_user.id, 'Произошла ошибка\n"Http статус:",'
                                                             f' {response.status_code}, "(", {response.reason},'
                                                             f' ")")')
                break
    else:
        await message.answer("Для выполнения этой команды нужны права администратора.")


@dp.message_handler(commands=["delete_channels"])
async def delete_channels(message: types.Message):
    if str(message.from_user.id) in admins:
        ids = message.text.split()
        text = ''
        for i in ids[1:]:
            if i == "@all":
                channels.clear()
                break
            if i in channels:
                channels.pop(channels.index(i))
                text += i + ', '
        with open("data/channels.txt", 'w') as channel:
            channel.write(channels[0])
            for i in channels[1:]:
                channel.write('\n' + i)
        await message.reply(f"Каналы {text[:-2]} успешно удалены")
    else:
        await message.answer("Для выполнения этой команды нужны права администратора.")


@dp.message_handler(commands=["add_prize"])
async def add_prize(message: types.Message):
    if str(message.from_user.id) in admins:
        prizes = message.text.split()
        for i in range(1, len(prizes), 2):
            if i + 1 < len(prizes):
                response = requests.post(f'{host}/staff_api/user/{prizes[i]}/{prizes[i + 1]}')
                if not response:
                    await message.answer("Произошла не придвиденная ошибка. Работы уже ведутся.")
                    await bot.send_message(message.from_user.id, 'Произошла ошибка\n"Http статус:",'
                                                                 f' {response.status_code}, "(", {response.reason},'
                                                                 f' ")")')
    else:
        await message.answer("Для выполнения этой команды нужны права администратора.")


@dp.message_handler(content_types="web_app_data")
def web_app(web_data):
    print(web_data.web_app_data.data)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
