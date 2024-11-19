from cProfile import label
from token import AWAIT

import schedule
import time
import logging
import asyncio
from prettytable import PrettyTable

from aiogram.types import CallbackQuery, message, ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Location
import sqlite3 as sq
import os

from getpass import getpass

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from pyexpat.errors import messages

import Markups_general.markups_general_ru_us as mk_gen_rs
import Markups_general.markups_ru as mk_ru
import Markups_general.markups_us as mk_us
import information.about_ru as ab_r
import information.about_us as ab_u
import information.staff_ru as s_r
import information.staff_us as s_u
import information.implementation_experience_ru as ie_r
import information.implementation_experience_us as ie_u

class ReviewsState(StatesGroup):
    write_reviews_state_ru = State()
    write_reviews_state_us = State()

# Создаем бота и диспетчерf
bot = Bot(token='7548377015:AAEDsUeTL6iTi8ox53ZP-FFpz57YcqyHKCM')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with state.proxy() as data:
        data['user_id'] = user_id
    # Код для отправки сообщения пользователю и установки состояния
    await bot.send_message(message.chat.id, "Здравствуйте!Я бот-помощник Algoritm23.\nHello I'm the bot assistant Algoritm23", reply_markup=mk_gen_rs.btn_сhoice)

@dp.callback_query_handler(lambda c: c.data == 'ru')
async def ru(callback_query: types.CallbackQuery):
    user_ru = [
        callback_query.from_user.id,
        callback_query.from_user.last_name,
        callback_query.from_user.first_name,
        'ru'
    ]
    with sq.connect('sq_baze/users.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                first_name TEXT,
                last_name TEXT,
                language TEXT
            )""")
        cur.execute("""UPDATE users SET last_name = ?, first_name = ?, language = ? WHERE user_id = ?""",
                    (callback_query.from_user.last_name, callback_query.from_user.first_name, 'ru',
                     callback_query.from_user.id))

        # Если не обновили ни одной записи, значит, её нет, и нужно вставить новую
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (user_id, last_name, first_name, language) VALUES (?, ?, ?, ?)", user_ru)
        await bot.answer_callback_query(callback_query.id, text='Вы перешли на русский язык!')
        await bot.send_message(callback_query.from_user.id, text='Вы перешли на русский язык!', reply_markup=mk_ru.btn_general_menu_ru)

@dp.callback_query_handler(lambda c: c.data == 'us')
async def us(callback_query: types.CallbackQuery):
    user_us = [
        callback_query.from_user.id,
        callback_query.from_user.last_name,
        callback_query.from_user.first_name,
        'us'
    ]
    with sq.connect('sq_baze/users.db') as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            language TEXT
        )""")
        # Попробуйте обновить запись
        cur.execute("""UPDATE users SET last_name = ?, first_name = ?, language = ? WHERE user_id = ?""",
                    (callback_query.from_user.last_name, callback_query.from_user.first_name, 'us',
                     callback_query.from_user.id))

        # Если не обновили ни одной записи, значит, её нет, и нужно вставить новую
        if cur.rowcount == 0:
            cur.execute("INSERT INTO users (user_id, last_name, first_name, language) VALUES (?, ?, ?, ?)", user_us)

        con.commit()
        await bot.answer_callback_query(callback_query.id, text='You have switched to English!')
        await bot.send_message(callback_query.from_user.id, text='You have switched to English!', reply_markup=mk_us.btn_general_menu_us)

@dp.message_handler(lambda message: message.text == '📖О нас')
async def about_ru(message: types.Message):
    await bot.send_message(message.chat.id, ab_r.about_ru)

@dp.message_handler(lambda message: message.text == '📖About')
async def about_us(message: types.Message):
    await bot.send_message(message.chat.id, ab_u.about_us)

@dp.message_handler(lambda message: message.text == '🏢Сотрудники')
async def staff_ru(message: types.Message):
    staff_info = s_r.name_while_ru()
    await bot.send_message(message.chat.id, 'Наши сотрудники:\n\n' + staff_info)

@dp.message_handler(lambda message: message.text == '🏢Staff')
async def staff_us(message: types.Message):
    staff_info = s_u.name_while_us()
    await bot.send_message(message.chat.id, 'Our staff:\n\n' + staff_info)

@dp.message_handler(lambda message: message.text == '⭐Отзывы')
async def reviews_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Открываю отзывы', reply_markup=mk_ru.btn_reviews_menu_ru)

@dp.message_handler(lambda message: message.text == '⭐Reviews')
async def reviews_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Opening reviews', reply_markup=mk_us.btn_reviews_menu_ru)

@dp.message_handler(lambda message: message.text == '🔍Посмотреть отзывы')
async def reviews_ru(message: types.Message):
    with sq.connect('sq_baze/reviews.db') as con:
        cur = con.cursor()
        # Создание таблицы, если её нет
        cur.execute("""CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            reviews TEXT
        )""")

        # Получение отзывов
        cur.execute("SELECT first_name, last_name, reviews FROM reviews")
        reviews = cur.fetchall()

        if not reviews:  # Если список отзывов пуст
            await bot.send_message(message.chat.id, 'Нет отзывов.')
        else:
            # Формирование строки с отзывами
            reviews_text = 'Отзывы:\n\n'
            for first_name, last_name, review in reviews:
                reviews_text += f'Имя: {first_name}, \nФамилия: {last_name}\nОтзыв: {review}\n{"." * 40}\n'
            await bot.send_message(message.chat.id, reviews_text)

@dp.message_handler(lambda message: message.text == '🔍View reviews')
async def reviews_us(message: types.Message):
    with sq.connect('sq_baze/reviews.db') as con:
        cur = con.cursor()
        # Создание таблицы, если её нет
        cur.execute("""CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            reviews TEXT
        )""")

        # Получение отзывов
        cur.execute("SELECT first_name, last_name, reviews FROM reviews")
        reviews = cur.fetchall()

        if not reviews:  # Если список отзывов пуст
            await bot.send_message(message.chat.id, "There're no reviews.")
        else:
            # Формирование строки с отзывами
            reviews_text = 'Reviews:\n\n'
            for first_name, last_name, review in reviews:
                reviews_text += f'Name: {first_name}, \nSurname: {last_name}\nReview: {review}\n{"." * 40}\n'
            await bot.send_message(message.chat.id, reviews_text)

@dp.message_handler(lambda message: message.text == '✍️Написать отзыв')
async def write_reviews_ru(message: types.Message, state: FSMContext):
        await bot.send_message(message.chat.id, 'Напишите ваш отзыв')
        await ReviewsState.write_reviews_state_ru.set()

@dp.message_handler(state=ReviewsState.write_reviews_state_ru)
async def write_reviews_ru_state(message: types.Message, state: FSMContext):
    user_text = message.text
    user_id = (message.from_user.id, message.from_user.first_name, message.from_user.last_name, user_text)
    with sq.connect('sq_baze/reviews.db') as con:
        cur = con.cursor()
        # Создание таблицы, если её нет
        cur.execute("""CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            reviews TEXT
        )""")
        cur.execute("INSERT INTO reviews (user_id, first_name, last_name, reviews) VALUES (?, ?, ?, ?)", user_id)
        con.commit()
        await bot.send_message(message.chat.id, 'Спасибо за отзыв!')
        await state.finish()

@dp.message_handler(lambda message: message.text == '✍️Write a review')
async def write_reviews_us(message: types.Message, state: FSMContext):
        await bot.send_message(message.chat.id, 'Write your review')
        await ReviewsState.write_reviews_state_us.set()

@dp.message_handler(state=ReviewsState.write_reviews_state_us)
async def write_reviews_us_state(message: types.Message, state: FSMContext):
    user_text = message.text
    user_id = (message.from_user.id, message.from_user.first_name, message.from_user.last_name, user_text)
    with sq.connect('sq_baze/reviews.db') as con:
        cur = con.cursor()
        # Создание таблицы, если её нет
        cur.execute("""CREATE TABLE IF NOT EXISTS reviews(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            reviews TEXT
        )""")
        cur.execute("INSERT INTO reviews (user_id, first_name, last_name, reviews) VALUES (?, ?, ?, ?)", user_id)
        con.commit()
        await bot.send_message(message.chat.id, 'Thanks for the feedback!')
        await state.finish()

@dp.message_handler(lambda message: message.text == '🌐Поменять язык')
async def help_ru(message: types.Message):
    user = ('us', message.from_user.id)
    with sq.connect('sq_baze/users.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET language = ? WHERE user_id = ?", user)
        con.commit()
        await bot.send_message(message.chat.id, "We've changed your language", reply_markup=mk_us.btn_settings_menu_us)

@dp.message_handler(lambda message: message.text == '🌐Change the language')
async def help_ru(message: types.Message):
    user = ('ru', message.from_user.id)
    with sq.connect('sq_baze/users.db') as con:
        cur = con.cursor()
        cur.execute("UPDATE users SET language = ? WHERE user_id = ?", user)
        con.commit()
        await bot.send_message(message.chat.id, "Мы изменили ваш язык", reply_markup=mk_ru.btn_settings_menu_ru)

@dp.message_handler(lambda message: message.text == '⚙️Настройки')
async def settings_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Открываю настройки', reply_markup=mk_ru.btn_settings_menu_ru)

@dp.message_handler(lambda message: message.text == '⚙️Settings')
async def settings_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Opening the settings', reply_markup=mk_us.btn_settings_menu_us)

@dp.message_handler(lambda message: message.text == '🔙Назад в главное меню')
async def back_to_the_main_menu_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Возвращаюсь в главное меню', reply_markup=mk_ru.btn_general_menu_ru)

@dp.message_handler(lambda message: message.text == '🔙Back to the main menu')
async def back_to_the_main_menu_us(message: types.Message):
    await bot.send_message(message.chat.id, "I'm going back to the main menu", reply_markup=mk_us.btn_general_menu_us)

@dp.message_handler(lambda message: message.text == '🔙Назад')
async def back_to_the_main_menu_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Возвращаюсь в панель-помощи', reply_markup=mk_ru.btn_help_menu_ru)

@dp.message_handler(lambda message: message.text == '🔙Back')
async def back_to_the_main_menu_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Возвращаюсь в панель-помощи', reply_markup=mk_us.btn_help_menu_us)

@dp.message_handler(lambda message: message.text == '💼Опыт внедрения')
async def implementation_experience_ru(message: types.Message):
    # Объединяем список с переносами строк
    experience_text = '\n'.join(ie_r.implementation_experience_ru)

    # Форматируем текст с выделением заголовков
    formatted_text = 'Опыт внедрения проектов основателем компании:\n\n' + experience_text

    # Отправляем сообщение пользователю
    await bot.send_message(message.chat.id, formatted_text, parse_mode='Markdown')

@dp.message_handler(lambda message: message.text == '💼Implementation experience')
async def implementation_experience_us(message: types.Message):
    # Объединяем список с переносами строк
    experience_text = '\n'.join(ie_u.implementation_experience_us)

    # Форматируем текст с выделением заголовков
    formatted_text = 'Project implementation experience by the founder of the company:\n\n' + experience_text

    # Отправляем сообщение пользователю
    await bot.send_message(message.chat.id, formatted_text, parse_mode='Markdown')

@dp.message_handler(lambda message: message.text == '❓Помощь')
async def help_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Открываю панель помощи', reply_markup=mk_ru.btn_help_menu_ru)

@dp.message_handler(lambda message: message.text == '❓Help')
async def help_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Opening the help panel', reply_markup=mk_us.btn_help_menu_us)

@dp.message_handler(lambda message: message.text == '📞Обратная связь с IT сотруником')
async def feedback_from_the_IT_partner_ru(message: types.Message):
    username = message.from_user.username  # Получаем имя пользователя
    chat_id = -1002166563393
    thread_id = 10

    if username:
        result_message = (
            'Клиент хочет связаться с IT сотрудником!\n'
            f"Телеграмм клиента: <a href='https://t.me/{username}'>@{username}</a>\n"
        )
    else:
        result_message = 'Клиент хочет связаться с IT сотрудником! Имя пользователя недоступно.\n'

    # Отправляем сообщение с инлайн-кнопками в нужный чат
    await bot.send_message(chat_id, result_message, parse_mode=ParseMode.HTML, message_thread_id=thread_id)
    await message.reply('Сотрудник вам скоро ответит!')

@dp.message_handler(lambda message: message.text == '📞Feedback from the IT partner')
async def feedback_from_the_IT_partner_us(message: types.Message):
    username = message.from_user.username  # Получаем имя пользователя
    chat_id = -1002166563393
    thread_id = 10

    if username:
        result_message = (
            'Клиент хочет связаться с IT сотрудником!\n'
            f"Телеграмм клиента: <a href='https://t.me/{username}'>@{username}</a>\n"
        )
    else:
        result_message = "Клиент хочет связаться с IT сотрудником! Имя пользователя недоступно.\n"

    # Отправляем сообщение с инлайн-кнопками в нужный чат
    await bot.send_message(chat_id, result_message, parse_mode=ParseMode.HTML, message_thread_id=thread_id)
    await message.reply('The employee will answer you soon!')

@dp.message_handler(lambda message: message.text == '🤝Обратная связь с Генеральным Директором')
async def feedback_from_the_general_director_ru(message: types.Message):
    gen_chat_id = '193458128'  # Замените на реальный chat_id Генерального Директора
    username = message.from_user.username

    if username:
        result_message = (
            'Клиент хочет связаться с Генеральным Директором!\n'
            f"Телеграмм клиента: <a href='https://t.me/{username}'>@{username}</a>\n"
        )
        # Отправляем сообщение Генеральному Директору
        await bot.send_message(gen_chat_id, result_message, parse_mode=ParseMode.HTML)
        await message.reply('Генеральный директор скоро вам ответит!')
    else:
        await message.reply('Имя пользователя недоступно. Не удалось отправить сообщение Генеральному Директору.')

@dp.message_handler(lambda message: message.text == '🤝Feedback from the General Director')
async def feedback_from_the_general_director_us(message: types.Message):
    gen_chat_id = '193458128'  # Замените на реальный chat_id Генерального Директора
    username = message.from_user.username

    if username:
        result_message = (
            'Клиент хочет связаться с Генеральным Директором!\n'
            f"Телеграмм клиента: <a href='https://t.me/{username}'>@{username}</a>\n"
        )
        # Отправляем сообщение Генеральному Директору
        await bot.send_message(gen_chat_id, result_message, parse_mode=ParseMode.HTML)
        await message.reply('The General Director will reply to you soon!')
    else:
        await message.reply("The user's name is not available. The message could not be sent to the General Director.")

@dp.message_handler(lambda message: message.text == '📚Инструкции')
async def instruciton_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Открываю инструкции', reply_markup=mk_ru.btn_help_instructions_menu_ru)

@dp.message_handler(lambda message: message.text == '📚Instructions')
async def instruciton_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Открываю инструкции', reply_markup=mk_us.btn_help_instructions_menu_us)

@dp.message_handler(lambda message: message.text == '📖Инструкция по Учету техники')
async def instruction_one_ru(message: types.Message):
    with open("instructions/РЕК_Учет техники.docx", "rb") as docx_file:
        await bot.send_document(message.chat.id, docx_file)

@dp.message_handler(lambda message: message.text == '📝Инструкция по созданию Заявки на МПЗ')
async def instruction_two_ru(message: types.Message):
    with open("instructions/РЕК_1_Инструкция_по_созданию_заявки_на_МПЗ_4.docx", "rb") as docx_file:
        await bot.send_document(message.chat.id, docx_file)

@dp.message_handler(lambda message: message.text == '📄Инструкция по созданию Приходного ордера, Поступления доп.\nРасходов, Регистрации входящей документации и Получение сертификатов')
async def instruction_three_ru(message: types.Message):
    with open("instructions/3_3_Инструкция_по_созданию_Приходного_ордера,_поступление_доп_расходов.docx", "rb") as docx_file:
        await bot.send_document(message.chat.id, docx_file)

@dp.message_handler(lambda message: message.text == '📑Инструкция по созданию Заказа поставщику')
async def instruction_four_ru(message: types.Message):
    with open("instructions/РЕК_Инструкция_по_созданию_Заказа_поставщику.docx", "rb") as docx_file:
        await bot.send_document(message.chat.id, docx_file)

@dp.message_handler(lambda message: message.text == '🌐Наш сайт')
async def our_website_ru(message: types.Message):
    await bot.send_message(message.chat.id, 'Нажмите на кнопку для перехода на сайт', reply_markup=mk_ru.website_menu_ru)

@dp.message_handler(lambda message: message.text == '🌐Our website')
async def our_website_us(message: types.Message):
    await bot.send_message(message.chat.id, 'Click on the button to go to the website', reply_markup=mk_us.website_menu_us)


# Запуск бота
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    executor.start_polling(dp, loop=loop, skip_updates=True)