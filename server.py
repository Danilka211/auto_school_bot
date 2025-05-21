from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Query
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import pathlib
import json
import os

TELEGRAM_BOT_TOKEN = "7946576799:AAHHd35iRAv317TGUY6dBAfG8f3VKEXuy1w"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


cars = [
    {"id": 1, "model": "Toyota Corolla", "description": "Удобный и экономичный седан. Простой в обслуживании, надёжный на любых дорогах.",
     "photo_url": "/static/toyota.webp", "available": True},
    {"id": 2, "model": "BMW 3 Series", "description": "Спортивный и стильный седан. Отличается динамичным управлением и высоким комфортом.",
     "photo_url": "/static/bmw.webp", "available": True},
    {"id": 3, "model": "Volkswagen Polo", "description": "Немецкое качество. Устойчив на дороге и прост в обслуживании.",
    "photo_url": "/static/polo.webp", "available": True},
    {"id": 4, "model": "Hyundai Solaris", "description": "Популярный учебный авто. Комфортный и манёвренный.",
    "photo_url": "/static/solaris.jpg", "available": True},
    {"id": 5, "model": "Kia Rio", "description": "Надёжный и экономичный седан. Лёгок в управлении.",
    "photo_url": "/static/kio.jpg", "available": True}
]

bookings = []
BOOKINGS_FILE = "bookings.json"
HOLIDAYS = ["2025-01-01",
"2025-01-02",
"2025-01-03", 
"2025-01-04", 
"2025-01-06", 
"2025-01-07",
"2025-01-08", 
"2025-03-08", 
"2025-05-01",
"2025-05-02",
"2025-05-03",
"2025-05-08",
"2025-05-09",
"2025-05-10",
"2025-06-12",
"2025-06-13",
"2025-06-14",
"2025-11-03",
"2025-11-04",
"2025-12-31"
]

def load_bookings():
    if os.path.exists(BOOKINGS_FILE):
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            bookings[:] = json.load(f)

def save_bookings():
    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, ensure_ascii=False, indent=4)

load_bookings()

@app.get("/holidays")
def get_holidays():
    return HOLIDAYS


BASE_DIR = pathlib.Path(__file__).parent.resolve()

@app.get("/")
async def get_index():
    index_path = BASE_DIR / "frontend" / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.get("/cars")
async def get_cars():
    return {"cars": cars}

class BookingRequest(BaseModel):
    car_id: int
    user_name: str
    user_id: int
    booking_date: str
    booking_start_time: str
    booking_end_time: str

class CancelBookingRequest(BaseModel):
    car_id: int
    user_name: str
    user_id: int
    booking_date: str
    booking_start_time: str
    booking_end_time: str

class UpdateBookingRequest(BaseModel):
    old_car_id: int
    old_date: str
    old_start_time: str
    old_end_time: str
    new_car_id: int
    new_date: str
    new_start_time: str
    new_end_time: str
    user_id: int
    user_name: str

@app.post("/update_booking")
async def update_booking(data: UpdateBookingRequest):
    # 1. Отменяем старое бронирование
    cancel_booking = next(
        (b for b in bookings 
         if b["user_id"] == data.user_id 
         and b["car_id"] == data.old_car_id 
         and b["booking_date"] == data.old_date
         and b["booking_start_time"] == data.old_start_time
         and b["booking_end_time"] == data.old_end_time),
        None
    )
    
    if not cancel_booking:
        raise HTTPException(status_code=404, detail="Старое бронирование не найдено")
    
    bookings.remove(cancel_booking)
    
    # 2. Создаем новое бронирование (с проверками)
    new_booking = {
        "car_id": data.new_car_id,
        "user_name": data.user_name,
        "user_id": data.user_id,
        "booking_date": data.new_date,
        "booking_start_time": data.new_start_time,
        "booking_end_time": data.new_end_time
    }
    
    # Проверяем доступность нового слота
    booking_start = datetime.strptime(f"{data.new_date} {data.new_start_time}", "%Y-%m-%d %H:%M")
    booking_end = datetime.strptime(f"{data.new_date} {data.new_end_time}", "%Y-%m-%d %H:%M")
    
    for b in bookings:
        if b["car_id"] == data.new_car_id and b["booking_date"] == data.new_date:
            existing_start = datetime.strptime(f"{b['booking_date']} {b['booking_start_time']}", "%Y-%m-%d %H:%M")
            existing_end = datetime.strptime(f"{b['booking_date']} {b['booking_end_time']}", "%Y-%m-%d %H:%M")
            
            if (booking_start < existing_end and booking_end > existing_start):
                raise HTTPException(
                    status_code=400,
                    detail="Машина уже забронирована в выбранный интервал времени."
                )
    
    # Добавляем новое бронирование
    selected_car = next((car for car in cars if car["id"] == data.new_car_id), None)
    if not selected_car:
        raise HTTPException(status_code=404, detail="Машина не найдена")
    
    new_booking.update({
        "model": selected_car["model"],
        "description": selected_car["description"],
        "photo_url": selected_car["photo_url"]
    })
    
    bookings.append(new_booking)
    save_bookings()
    
    return {"status": "success", "message": "Бронирование успешно обновлено"}

@app.post("/choose_car")
async def choose_car(data: BookingRequest):
    # Проверка на выходные и праздники
    booking_date = datetime.strptime(data.booking_date, "%Y-%m-%d").date()
    if booking_date.weekday() == 6 or data.booking_date in HOLIDAYS:  # Воскресенье или праздник
        raise HTTPException(
            status_code=400,
            detail="Бронь в выходной день недоступна."
        )

    # Проверка на субботу (короткий день)
    if booking_date.weekday() == 5:  # Суббота
        if data.booking_start_time < "10:00" or data.booking_end_time > "18:00":
            raise HTTPException(
                status_code=400,
                detail="В субботу бронь доступна только с 10:00 до 18:00."
            )

    # Проверка на обеденный перерыв
    if data.booking_start_time == "12:00" and data.booking_end_time == "13:00":
        raise HTTPException(
            status_code=400,
            detail="Бронь на обеденный перерыв недоступна."
        )

    # Проверка лимита бронирований (3 на пользователя)
    user_bookings_count = sum(1 for b in bookings if b["user_id"] == data.user_id)
    if user_bookings_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Вы уже забронировали 3 машины. Отмените одну из них."
        )

    # Проверка корректности времени
    booking_start = datetime.strptime(f"{data.booking_date} {data.booking_start_time}", "%Y-%m-%d %H:%M")
    booking_end = datetime.strptime(f"{data.booking_date} {data.booking_end_time}", "%Y-%m-%d %H:%M")
    
    if booking_start < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Невозможно забронировать машину на прошедшее время."
        )

    if booking_start >= booking_end:
        raise HTTPException(
            status_code=400,
            detail="Время начала бронирования должно быть раньше времени окончания."
        )

    # Проверка пересечений с существующими бронированиями
    for b in bookings:
        if b["car_id"] == data.car_id and b["booking_date"] == data.booking_date:
            existing_start = datetime.strptime(f"{b['booking_date']} {b['booking_start_time']}", "%Y-%m-%d %H:%M")
            existing_end = datetime.strptime(f"{b['booking_date']} {b['booking_end_time']}", "%Y-%m-%d %H:%M")
            
            if (booking_start < existing_end and booking_end > existing_start):
                raise HTTPException(
                    status_code=400,
                    detail="Машина уже забронирована в выбранный интервал времени."
                )

    # Добавление бронирования
    selected_car = next((car for car in cars if car["id"] == data.car_id), None)
    if not selected_car:
        raise HTTPException(status_code=404, detail="Машина не найдена.")

    bookings.append({
        "car_id": data.car_id,
        "user_name": data.user_name,
        "user_id": data.user_id,
        "model": selected_car["model"],
        "description": selected_car["description"],
        "photo_url": selected_car["photo_url"],
        "booking_date": data.booking_date,
        "booking_start_time": data.booking_start_time,
        "booking_end_time": data.booking_end_time
    })

    save_bookings()

    return {
        "status": "success",
        "message": f"{selected_car['model']} забронирована на {data.booking_date} с {data.booking_start_time} до {data.booking_end_time}!"
    }

@app.post("/cancel_booking")
async def cancel_booking(data: CancelBookingRequest):
    booking = next(
        (b for b in bookings 
         if b["user_id"] == data.user_id 
         and b["car_id"] == data.car_id 
         and b["booking_date"] == data.booking_date
         and b["booking_start_time"] == data.booking_start_time),
        None
    )

    if booking:
        bookings.remove(booking)
        save_bookings()
        return {
            "status": "success",
            "message": f"Бронирование на {data.booking_date} с {data.booking_start_time} отменено."
        }

    raise HTTPException(status_code=404, detail="Бронирование не найдено.")

@app.get("/my_bookings")
async def get_bookings(user_id: int = Query(...)):
    user_bookings = [
        {
            "car_id": b["car_id"],
            "model": b["model"],
            "description": b["description"],
            "photo_url": b["photo_url"],
            "booking_date": b["booking_date"],
            "booking_start_time": b["booking_start_time"],
            "booking_end_time": b["booking_end_time"]
        }
        for b in bookings if b["user_id"] == user_id
    ]
    
    return {"status": "success", "bookings": user_bookings} if user_bookings else {"status": "error", "message": "Нет активных бронирований"}

@app.get("/car_bookings")
async def get_car_bookings(car_id: int = Query(...), date: str = Query(None)):
    """Возвращает все бронирования для указанной машины (опционально - на конкретную дату)"""
    car_bookings = []
    for booking in bookings:
        if booking["car_id"] == car_id:
            if date is None or booking["booking_date"] == date:
                car_bookings.append({
                    "booking_date": booking["booking_date"],
                    "booking_start_time": booking["booking_start_time"],
                    "booking_end_time": booking["booking_end_time"]
                })
    
    return car_bookings