import asyncio
import logging
from os import getenv
from dotenv import load_dotenv

from aiogram.client.session.aiohttp import AiohttpSession

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, InlineKeyboardMarkup, CallbackQuery
from states import WaterStates

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
PROXY = "http://127.0.0.1:3066"

session = AiohttpSession(proxy=PROXY)

bot = Bot(token=BOT_TOKEN, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='🥤 Выпил стакан (250 мл)')],
            [KeyboardButton(text='📊 Мой прогресс'),
             KeyboardButton(text='🔄 Сброс')]
        ],
        resize_keyboard=True,
        input_field_placeholder='Выберите действия из меню'
    )
    return keyboard

@router.message(Command('start'))
async def cmd_start(message:Message):
    await message.answer(
        text='Привет! Я твой помощник по подсчету дневной нормы потребления воды 🐳\n\n Открой меню и выбери нужное действие.',
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == '🥤 Выпил стакан (250 мл)')
async def add_glass(message: Message, state: FSMContext):
    data = await state.get_data()
    current = data.get('my_progress', 0)
    new_progress = current + 250
    await state.update_data(my_progress=new_progress)
    await message.answer(f'Записано💫\n\n Итого {new_progress} мл. ')

@router.message(F.text == '📊 Мой прогресс')
async def view_progress(message: Message, state: FSMContext):
    data = await state.get_data()
    progress = data.get('my_progress', 0)
    if progress > 2000:
        await message.answer(f'Твой прогресс за день: \n\nКоличество выпитой воды: {progress} мл. \n\nПоздравляю! Твоя дневная норма выполнена! ✅')
    else:
        await message.answer(f'Твой прогресс за день: \n\nКоличество выпитой воды: {progress} мл.')

@router.message(F.text == '🔄 Сброс')
async def clean_progress(message: Message, state:FSMContext):
    await state.clear()
    await message.answer('Твой счетчик воды обнулен 🫗')

async def main():
    logger = logging.getLogger(__name__)
    logger.info('Бот готов к работе!')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())