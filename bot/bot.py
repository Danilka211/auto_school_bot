




# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime, timedelta
# import json

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов (user_id)
# ADMINS = [1805060245]  # Замените на ваш настоящий user_id

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Функции для загрузки и сохранения бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             bookings_data = json.load(f)
#             for booking in bookings_data:
#                 booking["time"] = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
#             return bookings_data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         serialized_bookings = []
#         for booking in bookings:
#             serialized_bookings.append({
#                 "car": booking["car"],
#                 "time": booking["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": booking["user_id"]
#             })
#         json.dump(serialized_bookings, f, indent=4)

# # Загружаем бронирования из файла при старте
# bookings = load_bookings()

# # FSM Состояния
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars — выбор машины
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [car for car in cars if car["available"]]
#     if not available_cars:
#         await message.answer("Извините, нет доступных машин.")
#         return

#     for car in available_cars:
#         button = InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

#         caption = f"<b>{car['model']}</b>\n{car['description']}"
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=caption,
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)

#     # Создадим клавиатуру с кнопками для выбора сегодняшней даты и времени
#     today = datetime.now()
#     today_str = today.strftime('%Y-%m-%d')
#     tomorrow = today + timedelta(days=1)
#     tomorrow_str = tomorrow.strftime('%Y-%m-%d')

#     # Создаём клавиатуру, передавая список кнопок как ключевые аргументы
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[ 
#         [KeyboardButton(text=f"Сегодня ({today_str})")],
#         [KeyboardButton(text=f"Завтра ({tomorrow_str})")],
#         [KeyboardButton(text="Выбрать дату вручную")]
#     ])

#     # Отправляем сообщение с клавиатурой
#     await bot.send_message(callback.from_user.id, f"Вы выбрали {car['model']}. Выберите дату для бронирования:", reply_markup=markup)
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

#     @dp.message(BookingState.entering_time)
#     async def time_entered(message: types.Message, state: FSMContext):
#         data = await state.get_data()
#         car = data.get("car")
#         time_str = message.text.strip()

#     if not car:
#         await message.answer("Ошибка: не выбрана машина.")
#         return

#     today = datetime.now()

#     try:
#         if "(" in time_str and ")" in time_str:
#             # Извлекаем дату из скобок
#             date_part = time_str[time_str.find("(")+1 : time_str.find(")")]
#             booking_time = datetime.strptime(date_part, "%Y-%m-%d")
#         else:
#             # Ожидается ручной ввод: строго "YYYY-MM-DD"
#             booking_time = datetime.strptime(time_str, "%Y-%m-%d")
#     except ValueError:
#         await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате: 2025-05-10")
#         return

#     # Проверка на прошлое
#     if booking_time.date() < today.date():
#         await message.answer("Нельзя забронировать машину на прошедшую дату.")
#         return

#     # Проверка занятости машины
#     for booking in bookings:
#         if booking["car"]["id"] == car["id"] and booking["time"].date() == booking_time.date():
#             await message.answer(f"Машина {car['model']} уже забронирована на {booking_time.strftime('%Y-%m-%d')}.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()
#     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d')} подтверждено!")
#     await state.clear()


# # Обработка ввода времени
# # @dp.message(BookingState.entering_time)
# # async def time_entered(message: types.Message, state: FSMContext):
# #     data = await state.get_data()
# #     car = data.get("car")
# #     time_str = message.text.strip()

# #     if not car:
# #         await message.answer("Ошибка: не выбрана машина.")
# #         return

# #     today = datetime.now()

# #     # Пытаемся извлечь дату из строки вида "Сегодня (2025-05-07)" или "Завтра (2025-05-08)"
# #     try:
# #         # Ищем подстроку в скобках
# #         if "(" in time_str and ")" in time_str:
# #             date_part = time_str[time_str.find("(")+1 : time_str.find(")")]
# #             booking_time = datetime.strptime(date_part, "%Y-%m-%d")
# #         else:
# #             # Предполагаем, что дата введена вручную в формате "YYYY-MM-DD"
# #             booking_time = datetime.strptime(time_str, "%Y-%m-%d")
# #     except ValueError:
# #         await message.answer("Неверный формат даты. Пожалуйста, используйте формат: YYYY-MM-DD.")
# #         return

# #     # Проверка на прошлое
# #     if booking_time.date() < today.date():
# #         await message.answer("Нельзя забронировать машину на прошедшую дату.")
# #         return

# #     # Проверка занятости машины
# #     for booking in bookings:
# #         if booking["car"]["id"] == car["id"] and booking["time"].date() == booking_time.date():
# #             await message.answer(f"Машина {car['model']} уже забронирована на {booking_time.strftime('%Y-%m-%d')}.")
# #             return

# #     bookings.append({
# #         "car": car,
# #         "time": booking_time,
# #         "user_id": message.from_user.id
# #     })
# #     save_bookings()
# #     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d')} подтверждено!")
# #     await state.clear()


# # /cancel — отмена бронирования
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования для отмены (например, 1):"
#     await message.answer(text)

# @dp.message(lambda message: message.text.isdigit())
# async def confirm_cancellation(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_cancel = user_bookings[booking_number - 1]
#     bookings.remove(booking_to_cancel)
#     save_bookings()
#     await message.answer(f"Бронирование для {booking_to_cancel['car']['model']} отменено.")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())




# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime, timedelta
# import json

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов
# ADMINS = [1805060245]

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Загрузка и сохранение бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             bookings_data = json.load(f)
#             for booking in bookings_data:
#                 booking["time"] = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
#             return bookings_data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         serialized_bookings = []
#         for booking in bookings:
#             serialized_bookings.append({
#                 "car": booking["car"],
#                 "time": booking["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": booking["user_id"]
#             })
#         json.dump(serialized_bookings, f, indent=4)

# bookings = load_bookings()

# # FSM Состояния
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# # Команда /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # Команда /cars — выбор машины
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [car for car in cars if car["available"]]
#     if not available_cars:
#         await message.answer("Извините, нет доступных машин.")
#         return

#     for car in available_cars:
#         button = InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
#         caption = f"<b>{car['model']}</b>\n{car['description']}"
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=caption,
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)

#     today = datetime.now()
#     tomorrow = today + timedelta(days=1)
#     today_str = today.strftime('%Y-%m-%d')
#     tomorrow_str = tomorrow.strftime('%Y-%m-%d')

#     markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
#         [KeyboardButton(text=f"Сегодня ({today_str})")],
#         [KeyboardButton(text=f"Завтра ({tomorrow_str})")],
#         [KeyboardButton(text="Выбрать дату вручную")]
#     ])

#     await bot.send_message(callback.from_user.id, f"Вы выбрали {car['model']}. Выберите дату для бронирования:", reply_markup=markup)
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Обработка ввода даты
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text.strip()

#     if not car:
#         await message.answer("Ошибка: не выбрана машина.")
#         return

#     today = datetime.now()

#     try:
#         if "(" in time_str and ")" in time_str:
#             date_part = time_str[time_str.find("(")+1 : time_str.find(")")]
#             booking_time = datetime.strptime(date_part, "%Y-%m-%d")
#         else:
#             booking_time = datetime.strptime(time_str, "%Y-%m-%d")
#     except ValueError:
#         await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате: 2025-05-10")
#         return

#     if booking_time.date() < today.date():
#         await message.answer("Нельзя забронировать машину на прошедшую дату.")
#         return

#     for booking in bookings:
#         if booking["car"]["id"] == car["id"] and booking["time"].date() == booking_time.date():
#             await message.answer(f"Машина {car['model']} уже забронирована на {booking_time.strftime('%Y-%m-%d')}.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()
#     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d')} подтверждено!")
#     await state.clear()

# # Команда /cancel — отмена бронирования
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования для отмены (например, 1):"
#     await message.answer(text)

# @dp.message(lambda message: message.text.isdigit())
# async def confirm_cancellation(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_cancel = user_bookings[booking_number - 1]
#     bookings.remove(booking_to_cancel)
#     save_bookings()
#     await message.answer(f"Бронирование для {booking_to_cancel['car']['model']} отменено.")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())



# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов (user_id)
# ADMINS = [1805060245]  # Замените на ваш настоящий user_id

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Функции для загрузки и сохранения бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             bookings_data = json.load(f)
#             for booking in bookings_data:
#                 booking["time"] = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
#             return bookings_data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         serialized_bookings = []
#         for booking in bookings:
#             serialized_bookings.append({
#                 "car": booking["car"],
#                 "time": booking["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": booking["user_id"]
#             })
#         json.dump(serialized_bookings, f, indent=4)

# # Загружаем бронирования из файла при старте
# bookings = load_bookings()

# # FSM Состояния
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars — выбор машины
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [car for car in cars if car["available"]]
#     if not available_cars:
#         await message.answer("Извините, нет доступных машин.")
#         return

#     for car in available_cars:
#         button = InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

#         caption = f"<b>{car['model']}</b>\n{car['description']}"
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=caption,
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, f"Вы выбрали {car['model']}. Укажите время (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Обработка ввода времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     if not car:
#         await message.answer("Ошибка: не выбрана машина.")
#         return

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте формат: YYYY-MM-DD HH:MM.")
#         return

#     for booking in bookings:
#         if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
#             await message.answer(f"Машина {car['model']} уже забронирована на это время.")
#             return

#     bookings.append({"car": car, "time": booking_time, "user_id": message.from_user.id})
#     save_bookings()
#     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')} подтверждено!")
#     await state.clear()

# # /cancel — отмена бронирования
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования для отмены (например, 1):"
#     await message.answer(text)

# @dp.message(lambda message: message.text.isdigit())
# async def confirm_cancellation(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_cancel = user_bookings[booking_number - 1]
#     bookings.remove(booking_to_cancel)
#     save_bookings()
#     await message.answer(f"Бронирование для {booking_to_cancel['car']['model']} отменено.")

# # /my_bookings — просмотр своих бронирований
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"
#     await message.answer(text)

# # /all_bookings — только для админов
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа к этой команде.")
#         return

#     if not bookings:
#         await message.answer("Нет активных бронирований.")
#         return

#     text = "Все бронирования:\n"
#     for idx, booking in enumerate(bookings, 1):
#         car = booking["car"]
#         time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         user_id = booking["user_id"]
#         text += f"{idx}. {car['model']} на {time} (user_id: {user_id})\n"
    
#     await message.answer(text)

# # /get_id — узнать свой user_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов (user_id)
# ADMINS = [1805060245]  # Замените на ваш настоящий user_id

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Функции для загрузки и сохранения бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             bookings_data = json.load(f)
#             for booking in bookings_data:
#                 booking["time"] = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
#             return bookings_data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         serialized_bookings = []
#         for booking in bookings:
#             serialized_bookings.append({
#                 "car": booking["car"],
#                 "time": booking["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": booking["user_id"]
#             })
#         json.dump(serialized_bookings, f, indent=4)

# # Загружаем бронирования из файла при старте
# bookings = load_bookings()

# # FSM Состояния
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars — выбор машины
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [car for car in cars if car["available"]]
#     if not available_cars:
#         await message.answer("Извините, нет доступных машин.")
#         return

#     for car in available_cars:
#         button = InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

#         caption = f"<b>{car['model']}</b>\n{car['description']}"
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=caption,
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, f"Вы выбрали {car['model']}. Укажите время (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Обработка ввода времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     if not car:
#         await message.answer("Ошибка: не выбрана машина.")
#         return

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте формат: YYYY-MM-DD HH:MM.")
#         return

#     for booking in bookings:
#         if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
#             await message.answer(f"Машина {car['model']} уже забронирована на это время.")
#             return

#     # Добавление уведомлений о бронировании
#     bookings.append({"car": car, "time": booking_time, "user_id": message.from_user.id})
#     save_bookings()
    
#     # Уведомление пользователю о подтверждении бронирования
#     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')} подтверждено!")

#     # Уведомление администратору о новом бронировании
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nПользователь ID: {message.from_user.id}")

#     await state.clear()

# # /cancel — отмена бронирования
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования для отмены (например, 1):"
#     await message.answer(text)

# @dp.message(lambda message: message.text.isdigit())
# async def confirm_cancellation(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_cancel = user_bookings[booking_number - 1]
#     bookings.remove(booking_to_cancel)
#     save_bookings()
    
#     # Детализированное сообщение об отмене
#     await message.answer(f"Бронирование для {booking_to_cancel['car']['model']} на {booking_to_cancel['time'].strftime('%Y-%m-%d %H:%M')} отменено.")

# # /my_bookings — просмотр своих бронирований
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"
#     await message.answer(text)

# # /all_bookings — только для админов
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа к этой команде.")
#         return

#     if not bookings:
#         await message.answer("Нет активных бронирований.")
#         return

#     text = "Все бронирования:\n"
#     for idx, booking in enumerate(bookings, 1):
#         car = booking["car"]
#         time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         user_id = booking["user_id"]
#         text += f"{idx}. {car['model']} на {time} (user_id: {user_id})\n"
    
#     await message.answer(text)

# # /get_id — узнать свой user_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())







# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загружаем токен из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов (user_id)
# ADMINS = [1805060245]  # Замените на ваш настоящий user_id

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Функции для загрузки и сохранения бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             bookings_data = json.load(f)
#             for booking in bookings_data:
#                 booking["time"] = datetime.strptime(booking["time"], "%Y-%m-%d %H:%M:%S")
#             return bookings_data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         serialized_bookings = []
#         for booking in bookings:
#             serialized_bookings.append({
#                 "car": booking["car"],
#                 "time": booking["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": booking["user_id"]
#             })
#         json.dump(serialized_bookings, f, indent=4)

# # Загружаем бронирования из файла при старте
# bookings = load_bookings()

# # FSM Состояния
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars — выбор машины
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [car for car in cars if car["available"]]
#     if not available_cars:
#         await message.answer("Извините, нет доступных машин.")
#         return

#     for car in available_cars:
#         button = InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

#         caption = f"<b>{car['model']}</b>\n{car['description']}"
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=caption,
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, f"Вы выбрали {car['model']}. Укажите время (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Обработка ввода времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     if not car:
#         await message.answer("Ошибка: не выбрана машина.")
#         return

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте формат: YYYY-MM-DD HH:MM.")
#         return

#     for booking in bookings:
#         if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
#             await message.answer(f"Машина {car['model']} уже забронирована на это время.")
#             return

#     # Добавление уведомлений о бронировании
#     bookings.append({"car": car, "time": booking_time, "user_id": message.from_user.id})
#     save_bookings()
    
#     # Уведомление пользователю о подтверждении бронирования
#     await message.answer(f"Бронирование для {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')} подтверждено!")

#     # Уведомление администратору о новом бронировании
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nПользователь ID: {message.from_user.id}")

#     await state.clear()

# # Функция для отмены бронирования
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования для отмены (например, 1):"
#     await message.answer(text)

# # Подтверждение отмены бронирования
# @dp.message(lambda message: message.text.isdigit())
# async def confirm_cancellation(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_cancel = user_bookings[booking_number - 1]
#     bookings.remove(booking_to_cancel)
#     save_bookings()
    
#     # Детализированное сообщение об отмене
#     await message.answer(f"Бронирование для {booking_to_cancel['car']['model']} на {booking_to_cancel['time'].strftime('%Y-%m-%d %H:%M')} отменено.")

# # /my_bookings — просмотр своих бронирований
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"
#     await message.answer(text)

# # /all_bookings — только для админов
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа к этой команде.")
#         return

#     if not bookings:
#         await message.answer("Нет активных бронирований.")
#         return

#     text = "Все бронирования:\n"
#     for idx, booking in enumerate(bookings, 1):
#         car = booking["car"]
#         time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         user_id = booking["user_id"]
#         text += f"{idx}. {car['model']} на {time} (user_id: {user_id})\n"
    
#     await message.answer(text)

# # /get_id — узнать свой user_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загрузка токена из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Логирование
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов
# ADMINS = [1805060245]

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Работа с файлами бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             data = json.load(f)
#             for b in data:
#                 b["time"] = datetime.strptime(b["time"], "%Y-%m-%d %H:%M:%S")
#             return data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         json.dump([
#             {
#                 "car": b["car"],
#                 "time": b["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": b["user_id"]
#             } for b in bookings
#         ], f, indent=4)

# bookings = load_bookings()

# # FSM
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# class EditBookingState(StatesGroup):
#     choosing_booking = State()
#     entering_new_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [c for c in cars if c["available"]]
#     if not available_cars:
#         await message.answer("Нет доступных машин.")
#         return

#     for car in available_cars:
#         markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")]
#         ])
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=f"<b>{car['model']}</b>\n{car['description']}",
#             reply_markup=markup,
#             parse_mode="HTML"
#         )
#     await state.set_state(BookingState.choosing_car)

# # Выбор машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, "Укажите время бронирования (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Ввод времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте YYYY-MM-DD HH:MM.")
#         return

#     for b in bookings:
#         if b["car"]["id"] == car["id"] and b["time"] == booking_time:
#             await message.answer("Эта машина уже забронирована на указанное время.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()

#     await message.answer(f"Бронирование подтверждено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}")
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nUser ID: {message.from_user.id}")
#     await state.clear()

# # /my_bookings
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     response = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         response += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     await message.answer(response)

# # /edit_booking
# @dp.message(Command("edit_booking"))
# async def edit_booking_start(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования, которое хотите изменить:"
#     await message.answer(text)
#     await state.set_state(EditBookingState.choosing_booking)

# @dp.message(EditBookingState.choosing_booking)
# async def choose_booking_to_edit(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     try:
#         index = int(message.text) - 1
#         booking = user_bookings[index]
#     except:
#         await message.answer("Некорректный номер.")
#         return

#     await state.update_data(booking=booking)
#     await message.answer("Введите новое время (например, 2025-05-09 15:00):")
#     await state.set_state(EditBookingState.entering_new_time)

# @dp.message(EditBookingState.entering_new_time)
# async def enter_new_time(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     booking = data.get("booking")
#     try:
#         new_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат. Используйте YYYY-MM-DD HH:MM.")
#         return

#     # Проверка на занятость
#     for b in bookings:
#         if b is not booking and b["car"]["id"] == booking["car"]["id"] and b["time"] == new_time:
#             await message.answer("Это время уже занято для выбранной машины.")
#             return

#     booking["time"] = new_time
#     save_bookings()
#     await message.answer(f"Время бронирования обновлено: {booking['car']['model']} → {new_time.strftime('%Y-%m-%d %H:%M')}")
#     await state.clear()

# # /cancel
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования для отмены:"
#     await message.answer(text)

# @dp.message(lambda m: m.text.isdigit())
# async def confirm_cancel(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     index = int(message.text) - 1
#     if index < 0 or index >= len(user_bookings):
#         await message.answer("Некорректный номер.")
#         return
#     b = user_bookings[index]
#     bookings.remove(b)
#     save_bookings()
#     await message.answer(f"Бронирование отменено: {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}")

# # /all_bookings (только для админов)
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа.")
#         return

#     if not bookings:
#         await message.answer("Нет бронирований.")
#         return

#     response = "Все бронирования:\n"
#     for i, b in enumerate(bookings, 1):
#         response += f"{i}. {b['car']['model']} — {b['time'].strftime('%Y-%m-%d %H:%M')} (user_id: {b['user_id']})\n"
#     await message.answer(response)

# # /get_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загрузка токена из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Логирование
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов
# ADMINS = [1805060245]

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Работа с файлами бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             data = json.load(f)
#             for b in data:
#                 b["time"] = datetime.strptime(b["time"], "%Y-%m-%d %H:%M:%S")
#             return data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         json.dump([
#             {
#                 "car": b["car"],
#                 "time": b["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": b["user_id"]
#             } for b in bookings
#         ], f, indent=4)

# bookings = load_bookings()

# # FSM
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# class EditBookingState(StatesGroup):
#     choosing_booking = State()
#     entering_new_time = State()
#     choosing_car = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [c for c in cars if c["available"]]
#     if not available_cars:
#         await message.answer("Нет доступных машин.")
#         return

#     for car in available_cars:
#         markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")]
#         ])
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=f"<b>{car['model']}</b>\n{car['description']}",
#             reply_markup=markup,
#             parse_mode="HTML"
#         )
#     await state.set_state(BookingState.choosing_car)

# # Выбор машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, "Укажите время бронирования (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Ввод времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте YYYY-MM-DD HH:MM.")
#         return

#     for b in bookings:
#         if b["car"]["id"] == car["id"] and b["time"] == booking_time:
#             await message.answer("Эта машина уже забронирована на указанное время.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()

#     await message.answer(f"Бронирование подтверждено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}")
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nUser ID: {message.from_user.id}")
#     await state.clear()

# # /my_bookings
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     response = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         response += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     await message.answer(response)

# # /edit_booking
# @dp.message(Command("edit_booking"))
# async def edit_booking_start(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования, которое хотите изменить:"
#     await message.answer(text)
#     await state.set_state(EditBookingState.choosing_booking)

# @dp.message(EditBookingState.choosing_booking)
# async def choose_booking_to_edit(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     try:
#         index = int(message.text) - 1
#         booking = user_bookings[index]
#     except:
#         await message.answer("Некорректный номер.")
#         return

#     await state.update_data(booking=booking)
#     await message.answer("Введите новое время (например, 2025-05-09 15:00):")
#     await state.set_state(EditBookingState.entering_new_time)

# @dp.message(EditBookingState.entering_new_time)
# async def enter_new_time(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     booking = data.get("booking")
#     try:
#         new_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат. Используйте YYYY-MM-DD HH:MM.")
#         return

#     # Проверка на занятость
#     for b in bookings:
#         if b is not booking and b["car"]["id"] == booking["car"]["id"] and b["time"] == new_time:
#             await message.answer("Это время уже занято для выбранной машины.")
#             return

#     booking["time"] = new_time
#     save_bookings()
#     await message.answer(f"Время бронирования обновлено: {booking['car']['model']} → {new_time.strftime('%Y-%m-%d %H:%M')}")
#     await state.clear()

# # /edit_car
# @dp.message(Command("edit_car"))
# async def edit_car(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования, для которого хотите изменить машину (например, 1):"
#     await message.answer(text)

# @dp.message(lambda message: message.text.isdigit())
# async def confirm_edit_car(message: types.Message):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_edit = user_bookings[booking_number - 1]
#     await message.answer(f"Вы выбрали бронирование для {booking_to_edit['car']['model']} на {booking_to_edit['time'].strftime('%Y-%m-%d %H:%M')}. Укажите новую машину.")
#     await state.set_state(BookingState.choosing_car)

# # Обработка выбора новой машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen_edit(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     data = await state.get_data()
#     booking_to_edit = data.get("booking")

#     if booking_to_edit and booking_to_edit["car"]["id"] != car["id"]:
#         # Проверим, что новая машина доступна на выбранное время
#         booking_time = booking_to_edit["time"]
#         for booking in bookings:
#             if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
#                 await callback.answer(f"Машина {car['model']} уже забронирована на это время.")
#                 return

#         # Обновляем бронирование
#         booking_to_edit["car"] = car
#         save_bookings()

#         await callback.answer(f"Вы успешно изменили машину на {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")
#         await callback.message.answer(f"Бронирование обновлено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")

#     await state.clear()

# # /cancel
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования для отмены:"
#     await message.answer(text)

# @dp.message(lambda m: m.text.isdigit())
# async def confirm_cancel(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     index = int(message.text) - 1
#     if index < 0 or index >= len(user_bookings):
#         await message.answer("Некорректный номер.")
#         return
#     b = user_bookings[index]
#     bookings.remove(b)
#     save_bookings()
#     await message.answer(f"Бронирование отменено: {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}")

# # /all_bookings (только для админов)
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа.")
#         return

#     if not bookings:
#         await message.answer("Нет бронирований.")
#         return

#     response = "Все бронирования:\n"
#     for i, b in enumerate(bookings, 1):
#         response += f"{i}. {b['car']['model']} — {b['time'].strftime('%Y-%m-%d %H:%M')} (user_id: {b['user_id']})\n"
#     await message.answer(response)

# # /get_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())



# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загрузка токена из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Логирование
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов
# ADMINS = [1805060245]

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Работа с файлами бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             data = json.load(f)
#             for b in data:
#                 b["time"] = datetime.strptime(b["time"], "%Y-%m-%d %H:%M:%S")
#             return data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         json.dump([{
#             "car": b["car"],
#             "time": b["time"].strftime("%Y-%m-%d %H:%M:%S"),
#             "user_id": b["user_id"]
#         } for b in bookings], f, indent=4)

# bookings = load_bookings()

# # FSM
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# class EditBookingState(StatesGroup):
#     choosing_booking = State()
#     entering_new_time = State()
#     choosing_car = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [c for c in cars if c["available"]]
#     if not available_cars:
#         await message.answer("Нет доступных машин.")
#         return

#     for car in available_cars:
#         markup = InlineKeyboardMarkup(inline_keyboard=[[
#             InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         ]])
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=f"<b>{car['model']}</b>\n{car['description']}",
#             reply_markup=markup,
#             parse_mode="HTML"
#         )
#     await state.set_state(BookingState.choosing_car)

# # Выбор машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, "Укажите время бронирования (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Ввод времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте YYYY-MM-DD HH:MM.")
#         return

#     for b in bookings:
#         if b["car"]["id"] == car["id"] and b["time"] == booking_time:
#             await message.answer("Эта машина уже забронирована на указанное время.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()

#     await message.answer(f"Бронирование подтверждено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}")
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nUser ID: {message.from_user.id}")
#     await state.clear()

# # /my_bookings
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     response = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         response += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     await message.answer(response)

# # /edit_booking
# @dp.message(Command("edit_booking"))
# async def edit_booking_start(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования, которое хотите изменить:"
#     await message.answer(text)
#     await state.set_state(EditBookingState.choosing_booking)

# @dp.message(EditBookingState.choosing_booking)
# async def choose_booking_to_edit(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     try:
#         index = int(message.text) - 1
#         booking = user_bookings[index]
#     except (ValueError, IndexError):
#         await message.answer("Некорректный номер.")
#         return

#     await state.update_data(booking=booking)
#     await message.answer("Введите новое время (например, 2025-05-09 15:00):")
#     await state.set_state(EditBookingState.entering_new_time)

# @dp.message(EditBookingState.entering_new_time)
# async def enter_new_time(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     booking = data.get("booking")
#     try:
#         new_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат. Используйте YYYY-MM-DD HH:MM.")
#         return

#     # Проверка на занятость
#     for b in bookings:
#         if b is not booking and b["car"]["id"] == booking["car"]["id"] and b["time"] == new_time:
#             await message.answer("Это время уже занято для выбранной машины.")
#             return

#     booking["time"] = new_time
#     save_bookings()
#     await message.answer(f"Время бронирования обновлено: {booking['car']['model']} → {new_time.strftime('%Y-%m-%d %H:%M')}")
#     await state.clear()

# # /edit_car
# @dp.message(Command("edit_car"))
# async def edit_car(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for idx, booking in enumerate(user_bookings, 1):
#         car = booking["car"]
#         booking_time = booking["time"].strftime('%Y-%m-%d %H:%M')
#         text += f"{idx}. {car['model']} на {booking_time}\n"

#     text += "Введите номер бронирования, для которого хотите изменить машину (например, 1):"
#     await message.answer(text)


# @dp.message(lambda message: message.text.isdigit())
# async def confirm_edit_car(message: types.Message, state: FSMContext):
#     booking_number = int(message.text)
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if booking_number < 1 or booking_number > len(user_bookings):
#         await message.answer("Неверный номер бронирования.")
#         return

#     booking_to_edit = user_bookings[booking_number - 1]
#     await state.update_data(booking=booking_to_edit)
#     await message.answer(
#         f"Вы выбрали бронирование для {booking_to_edit['car']['model']} на {booking_to_edit['time'].strftime('%Y-%m-%d %H:%M')}. Укажите новую машину."
#     )

#     # Покажем список машин
#     available_cars = [c for c in cars if c["available"]]
#     for car in available_cars:
#         markup = InlineKeyboardMarkup(inline_keyboard=[[
#             InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")
#         ]])
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=f"<b>{car['model']}</b>\n{car['description']}",
#             reply_markup=markup,
#             parse_mode="HTML"
#         )

#     await state.set_state(EditBookingState.choosing_car)  # Используем правильное состояние

# # @dp.message(lambda message: message.text.isdigit())
# # async def confirm_edit_car(message: types.Message, state: FSMContext):
# #     booking_number = int(message.text)
# #     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
# #     if booking_number < 1 or booking_number > len(user_bookings):
# #         await message.answer("Неверный номер бронирования.")
# #         return

# #     booking_to_edit = user_bookings[booking_number - 1]
# #     await message.answer(f"Вы выбрали бронирование для {booking_to_edit['car']['model']} на {booking_to_edit['time'].strftime('%Y-%m-%d %H:%M')}. Укажите новую машину.")
# #     await state.set_state(BookingState.choosing_car)


# # @dp.message(lambda message: message.text.isdigit())
# # async def confirm_edit_car(message: types.Message):
# #     booking_number = int(message.text)
# #     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
# #     if booking_number < 1 or booking_number > len(user_bookings):
# #         await message.answer("Неверный номер бронирования.")
# #         return

# #     booking_to_edit = user_bookings[booking_number - 1]
# #     await message.answer(f"Вы выбрали бронирование для {booking_to_edit['car']['model']} на {booking_to_edit['time'].strftime('%Y-%m-%d %H:%M')}. Укажите новую машину.")
# #     await state.set_state(BookingState.choosing_car)


# # Обработка выбора новой машины
# @dp.callback_query(EditBookingState.choosing_car, F.data.startswith("car_"))
# async def car_chosen_edit(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     data = await state.get_data()
#     booking_to_edit = data.get("booking")

#     if booking_to_edit and booking_to_edit["car"]["id"] != car["id"]:
#         # Проверим, что новая машина доступна на выбранное время
#         booking_time = booking_to_edit["time"]
#         for booking in bookings:
#             if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
#                 await callback.answer(f"Машина {car['model']} уже забронирована на это время.")
#                 return

#         # Обновляем бронирование
#         booking_to_edit["car"] = car
#         save_bookings()

#         await callback.message.answer(f"Бронирование обновлено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")
#         await callback.answer("Успешно!")
#     else:
#         await callback.answer("Выберите другую машину.")

#     await state.clear()

# # @dp.callback_query(F.data.startswith("car_"))
# # async def car_chosen_edit(callback: types.CallbackQuery, state: FSMContext):
# #     car_id = int(callback.data.split("_")[1])
# #     car = next((c for c in cars if c["id"] == car_id), None)
# #     if not car:
# #         await callback.answer("Машина не найдена.")
# #         return

# #     data = await state.get_data()
# #     booking_to_edit = data.get("booking")

# #     if booking_to_edit and booking_to_edit["car"]["id"] != car["id"]:
# #         # Проверим, что новая машина доступна на выбранное время
# #         booking_time = booking_to_edit["time"]
# #         for booking in bookings:
# #             if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
# #                 await callback.answer(f"Машина {car['model']} уже забронирована на это время.")
# #                 return

# #         # Обновляем бронирование
# #         booking_to_edit["car"] = car
# #         save_bookings()

# #         await callback.answer(f"Вы успешно изменили машину на {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")
# #         await callback.message.answer(f"Бронирование обновлено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")
# #     else:
# #         await callback.answer("Необходимо выбрать другую машину.")
        
# #     await state.clear()

# # # Обработка выбора новой машины
# # @dp.callback_query(F.data.startswith("car_"))
# # async def car_chosen_edit(callback: types.CallbackQuery, state: FSMContext):
# #     car_id = int(callback.data.split("_")[1])
# #     car = next((c for c in cars if c["id"] == car_id), None)
# #     if not car:
# #         await callback.answer("Машина не найдена.")
# #         return

# #     data = await state.get_data()
# #     booking_to_edit = data.get("booking")

# #     if booking_to_edit and booking_to_edit["car"]["id"] != car["id"]:
# #         # Проверим, что новая машина доступна на выбранное время
# #         booking_time = booking_to_edit["time"]
# #         for booking in bookings:
# #             if booking["car"]["id"] == car["id"] and booking["time"] == booking_time:
# #                 await callback.answer(f"Машина {car['model']} уже забронирована на это время.")
# #                 return

# #         # Обновляем бронирование
# #         booking_to_edit["car"] = car
# #         save_bookings()

# #         await callback.answer(f"Вы успешно изменили машину на {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")
# #         await callback.message.answer(f"Бронирование обновлено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}.")

# #     await state.clear()

# # /cancel
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования для отмены:"
#     await message.answer(text)

# @dp.message(lambda m: m.text.isdigit())
# async def confirm_cancel(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     index = int(message.text) - 1
#     if index < 0 or index >= len(user_bookings):
#         await message.answer("Некорректный номер.")
#         return
#     b = user_bookings[index]
#     bookings.remove(b)
#     save_bookings()
#     await message.answer(f"Бронирование отменено: {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}")

# # /all_bookings (только для админов)
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа.")
#         return

#     if not bookings:
#         await message.answer("Нет бронирований.")
#         return

#     response = "Все бронирования:\n"
#     for i, b in enumerate(bookings, 1):
#         response += f"{i}. {b['car']['model']} — {b['time'].strftime('%Y-%m-%d %H:%M')} (user_id: {b['user_id']})\n"
#     await message.answer(response)

# # /get_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())


















# import logging
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.filters import Command
# from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
# from dotenv import load_dotenv
# import os
# import asyncio
# from datetime import datetime
# import json

# # Загрузка токена из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Логирование
# logging.basicConfig(level=logging.INFO)

# # Инициализация
# bot = Bot(token=TOKEN)
# dp = Dispatcher(storage=MemoryStorage())

# # Список админов
# ADMINS = [1805060245]

# # Список машин
# cars = [
#     {
#         "id": 1,
#         "model": "Toyota Corolla",
#         "available": True,
#         "description": "Надежный седан с автоматической коробкой передач.",
#         "photo_url": "https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg"
#     },
#     {
#         "id": 2,
#         "model": "Honda Civic",
#         "available": True,
#         "description": "Экономичный хэтчбек, отличный для учебы.",
#         "photo_url": "https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg"
#     },
#     {
#         "id": 3,
#         "model": "BMW 3 Series",
#         "available": False,
#         "description": "Премиум-класс, пока не доступна.",
#         "photo_url": "https://images.pexels.com/photos/1402787/pexels-photo-1402787.jpeg"
#     },
# ]

# # Работа с файлами бронирований
# def load_bookings():
#     if os.path.exists('bookings.json'):
#         with open('bookings.json', 'r') as f:
#             data = json.load(f)
#             for b in data:
#                 b["time"] = datetime.strptime(b["time"], "%Y-%m-%d %H:%M:%S")
#             return data
#     return []

# def save_bookings():
#     with open('bookings.json', 'w') as f:
#         json.dump([
#             {
#                 "car": b["car"],
#                 "time": b["time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "user_id": b["user_id"]
#             } for b in bookings
#         ], f, indent=4)

# bookings = load_bookings()

# # FSM
# class BookingState(StatesGroup):
#     choosing_car = State()
#     entering_time = State()

# class EditBookingState(StatesGroup):
#     choosing_booking = State()
#     entering_new_time = State()

# # /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Добро пожаловать в AutoSchoolBot! Для бронирования машины используйте /cars")

# # /cars
# @dp.message(Command("cars"))
# async def cmd_cars(message: types.Message, state: FSMContext):
#     available_cars = [c for c in cars if c["available"]]
#     if not available_cars:
#         await message.answer("Нет доступных машин.")
#         return

#     for car in available_cars:
#         markup = InlineKeyboardMarkup(inline_keyboard=[
#             [InlineKeyboardButton(text="Выбрать", callback_data=f"car_{car['id']}")]
#         ])
#         await bot.send_photo(
#             chat_id=message.chat.id,
#             photo=car["photo_url"],
#             caption=f"<b>{car['model']}</b>\n{car['description']}",
#             reply_markup=markup,
#             parse_mode="HTML"
#         )
#     await state.set_state(BookingState.choosing_car)

# # Выбор машины
# @dp.callback_query(F.data.startswith("car_"))
# async def car_chosen(callback: types.CallbackQuery, state: FSMContext):
#     car_id = int(callback.data.split("_")[1])
#     car = next((c for c in cars if c["id"] == car_id), None)
#     if not car:
#         await callback.answer("Машина не найдена.")
#         return

#     await state.update_data(car=car)
#     await bot.send_message(callback.from_user.id, "Укажите время бронирования (например, 2025-05-08 10:00):")
#     await state.set_state(BookingState.entering_time)
#     await callback.answer()

# # Ввод времени
# @dp.message(BookingState.entering_time)
# async def time_entered(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     car = data.get("car")
#     time_str = message.text

#     try:
#         booking_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат времени. Используйте YYYY-MM-DD HH:MM.")
#         return

#     for b in bookings:
#         if b["car"]["id"] == car["id"] and b["time"] == booking_time:
#             await message.answer("Эта машина уже забронирована на указанное время.")
#             return

#     bookings.append({
#         "car": car,
#         "time": booking_time,
#         "user_id": message.from_user.id
#     })
#     save_bookings()

#     await message.answer(f"Бронирование подтверждено: {car['model']} на {booking_time.strftime('%Y-%m-%d %H:%M')}")
#     for admin in ADMINS:
#         await bot.send_message(admin, f"Новое бронирование:\nМашина: {car['model']}\nВремя: {booking_time.strftime('%Y-%m-%d %H:%M')}\nUser ID: {message.from_user.id}")
#     await state.clear()

# # /my_bookings
# @dp.message(Command("my_bookings"))
# async def my_bookings(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     response = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         response += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     await message.answer(response)

# # /edit_booking
# @dp.message(Command("edit_booking"))
# async def edit_booking_start(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования, которое хотите изменить:"
#     await message.answer(text)
#     await state.set_state(EditBookingState.choosing_booking)

# @dp.message(EditBookingState.choosing_booking)
# async def choose_booking_to_edit(message: types.Message, state: FSMContext):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     try:
#         index = int(message.text) - 1
#         booking = user_bookings[index]
#     except:
#         await message.answer("Некорректный номер.")
#         return

#     await state.update_data(booking=booking)
#     await message.answer("Введите новое время (например, 2025-05-09 15:00):")
#     await state.set_state(EditBookingState.entering_new_time)

# @dp.message(EditBookingState.entering_new_time)
# async def enter_new_time(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     booking = data.get("booking")
#     try:
#         new_time = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат. Используйте YYYY-MM-DD HH:MM.")
#         return

#     # Проверка на занятость
#     for b in bookings:
#         if b is not booking and b["car"]["id"] == booking["car"]["id"] and b["time"] == new_time:
#             await message.answer("Это время уже занято для выбранной машины.")
#             return

#     booking["time"] = new_time
#     save_bookings()
#     await message.answer(f"Время бронирования обновлено: {booking['car']['model']} → {new_time.strftime('%Y-%m-%d %H:%M')}")
#     await state.clear()

# # /cancel
# @dp.message(Command("cancel"))
# async def cancel_booking(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     if not user_bookings:
#         await message.answer("У вас нет активных бронирований.")
#         return

#     text = "Ваши бронирования:\n"
#     for i, b in enumerate(user_bookings, 1):
#         text += f"{i}. {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}\n"
#     text += "\nВведите номер бронирования для отмены:"
#     await message.answer(text)

# @dp.message(lambda m: m.text.isdigit())
# async def confirm_cancel(message: types.Message):
#     user_bookings = [b for b in bookings if b["user_id"] == message.from_user.id]
#     index = int(message.text) - 1
#     if index < 0 or index >= len(user_bookings):
#         await message.answer("Некорректный номер.")
#         return
#     b = user_bookings[index]
#     bookings.remove(b)
#     save_bookings()
#     await message.answer(f"Бронирование отменено: {b['car']['model']} на {b['time'].strftime('%Y-%m-%d %H:%M')}")

# # /all_bookings (только для админов)
# @dp.message(Command("all_bookings"))
# async def all_bookings(message: types.Message):
#     if message.from_user.id not in ADMINS:
#         await message.answer("У вас нет доступа.")
#         return

#     if not bookings:
#         await message.answer("Нет бронирований.")
#         return

#     response = "Все бронирования:\n"
#     for i, b in enumerate(bookings, 1):
#         response += f"{i}. {b['car']['model']} — {b['time'].strftime('%Y-%m-%d %H:%M')} (user_id: {b['user_id']})\n"
#     await message.answer(response)

# # /get_id
# @dp.message(Command("get_id"))
# async def get_id(message: types.Message):
#     await message.answer(f"Ваш user_id: {message.from_user.id}")

# # Запуск
# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())















import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import WebAppInfo
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,  KeyboardButton, ReplyKeyboardMarkup, Message
from dotenv import load_dotenv
from datetime import timedelta
from aiohttp import web
import os
import asyncio
from datetime import datetime
import json

routes = web.RouteTableDef()

# Загрузка токена из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Список админов
ADMINS = [1805060245]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть Mini App",
            web_app=WebAppInfo(url="https://lazy-sites-guess.loca.lt")
        )]
    ])
    await message.answer("Добро пожаловать! Открой Mini App:", reply_markup=markup)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



















