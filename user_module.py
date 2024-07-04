from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                           KeyboardButton, ReplyKeyboardMarkup, CallbackQuery)
from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import requests
from pyhoroscope import horoscope
from text import introduction, keys_text_answer
from identifications import bot_token, sasha_id, vera_id
bot = Bot(token= bot_token)
from identifications import answers_for_key, keys, keys_keys


class UserManager:
    def __init__(self):
        self.user_id_command = None
    
    def set_user_id(self, user_id):
        self.user_id_command = user_id
    
    def get_user_id(self):
        return self.user_id_command
user_manager = UserManager()

good_list = [sasha_id, vera_id]
#user_id_command = 811028066
class UserState(StatesGroup):
    waiting_for_input  = State()
    waiting_for_input_key = State()
    offer = State()

router = Router()

button_1 = KeyboardButton(text='Ключи')
button_2 = KeyboardButton(text='Пойти на свидание')
button_3 = KeyboardButton(text='Поднять настроение')
button_4 = KeyboardButton(text='Получить гороскоп')
button_5 = KeyboardButton(text='Предложить функционал')

Keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1], [button_2], [button_3], [button_5]], resize_keyboard=True)

button_empty_1 = KeyboardButton(text='Вернуться в главное меню')
Empty_keyboard = ReplyKeyboardMarkup(keyboard=[[button_empty_1]], resize_keyboard=True)

button_key1 = InlineKeyboardButton(text='первый ключ', callback_data='button_key1')
button_key2 = InlineKeyboardButton(text='второй ключ', callback_data='button_key2')
button_key3 = InlineKeyboardButton(text='третий ключ', callback_data='button_key3')
button_key4 = InlineKeyboardButton(text='четвертый ключ', callback_data='button_key4')
button_key5 = InlineKeyboardButton(text='пятый ключ', callback_data='button_key5')
button_key6 = InlineKeyboardButton(text='шестой ключ', callback_data='button_key6')

keyboard_keys = InlineKeyboardMarkup(
    inline_keyboard=[[button_key1], [button_key2], [button_key3], [button_key4], [button_key5], [button_key6]]
)

@router.message(Command(commands= ['start']))
async def process_start_command(message: Message):
    user_manager.set_user_id(message.from_user.id)
    if int(user_manager.get_user_id()) in good_list:
        await message.answer(text=introduction, reply_markup=Keyboard)
    else:
        message.answer(text='У Вас нет доступа к данному боту.')

@router.message(F.text == 'Ключи')
async def process_keys(message: Message):
    await message.answer(text='Список ключей', reply_markup=keyboard_keys)

@router.message(F.text == 'Предложить функционал')
async def process_meeting(message: Message, state: FSMContext):
    await message.answer(text='Введите предложение по улучшению бота или интересующий вас вопрос', reply_markup=Empty_keyboard)
    await state.set_state(UserState.offer)

@router.callback_query(F.text == 'Предложить функционал')
async def process_button_key(callback_query: CallbackQuery, state: FSMContext):
    meeting_place = callback_query.data
    await callback_query.message.answer(f"Введите предложение по улучшению бота, функционала или интересующий вас вопрос")
    await state.set_state(UserState.offer)
    await state.update_data(meeting_place=meeting_place)
        
@router.message(UserState.offer)
async def process_user_input_key1(message: Message, state: FSMContext):
    user_input = message.text
    if user_input != 'Вернуться в главное меню':
        await message.answer(f"Спасибо! Данные направлены Александру!", reply_markup=Keyboard)
        chat_id = sasha_id
        await bot.send_message(chat_id=chat_id, text=user_input)
    else:
        await message.answer(f"Ждем твоих предложений)))", reply_markup=Keyboard)
    await state.set_state(None)
    await state.clear()

@router.message(F.text == 'Пойти на свидание')
async def process_meeting(message: Message, state: FSMContext):
    await message.answer(text='Введите дату время и место встречи', reply_markup=Empty_keyboard)
    await state.set_state(UserState.waiting_for_input)

@router.callback_query(F.text == 'Пойти на свидание')
async def process_button_key(callback_query: CallbackQuery, state: FSMContext):
    meeting_place = callback_query.data
    await callback_query.message.answer(f"Введите дату время и место встречи", reply_markup=Empty_keyboard)
    await state.set_state(UserState.waiting_for_input)
    await state.update_data(meeting_place=meeting_place)

@router.message(UserState.waiting_for_input)
async def process_user_input_key1(message: Message, state: FSMContext):
    user_input = message.text
    if user_input != 'Вернуться в главное меню':
        await message.answer(f"Спасибо! Данные направлены Александру!\nДля отмены или переноса свидания свяжитесь с партнером.", reply_markup=Keyboard)
        chat_id = sasha_id
        await bot.send_message(chat_id=chat_id, text=user_input)
    else:
        await message.answer(f"Как надумаешь, пиши)))", reply_markup=Keyboard)
    await state.set_state(None)
    await state.clear()

@router.callback_query(F.data.startswith("button_key"))
async def process_button_key(callback_query: CallbackQuery, state: FSMContext):
    key_number = int(callback_query.data[-1])
    await callback_query.message.answer(f"Для получения доступа к {keys[f'key{key_number}']} ключу введите ответ на вопрос")
    await state.set_state(UserState.waiting_for_input_key)
    await state.update_data(key_number=key_number)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )

@router.message(UserState.waiting_for_input_key)
async def process_user_input_key1(message: Message, state: FSMContext):
    user_input = message.text
    data = await state.get_data()
    key_number = data.get("key_number")
    if user_input == answers_for_key[f'key{key_number}']:
        await message.answer(f"Поздравляю ты ввела правильный ответ.\nКлюч_{key_number} запомни его или запиши: {keys_keys[key_number]}\n\n{keys_text_answer["key"+str(key_number)]}")
        global Keyboard
        Keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_1], [button_2], [button_3], [button_4], [button_5]], resize_keyboard=True)
        keyboard_keys.inline_keyboard.pop(int(key_number)-1)
        await message.answer(text="Добавлена новая кнопка в главное меню-Получить гороскоп!!!", reply_markup=Keyboard)
        await state.set_state(None)
        await state.clear()
    else:
        await message.answer(f"Неправильный ответ для {key_number} ключа")
        await state.set_state(None)
        await state.clear()

@router.message(F.text == "Поднять настроение")
async def process_cheer_up(message: Message):
    photo = await fetch_cat_image()
    if photo:
         await message.answer_photo(photo)
    else:
        await message.answer("Попробуй снова)))")

async def fetch_cat_image():
    url = 'https://api.thecatapi.com/v1/images/search'
    cat_response = requests.get(url)
    if cat_response.status_code == 200:
        cat_link = cat_response.json()[0]['url']
        return cat_link
    else:
        return 0
    
'''def transfer(mytext):
    #mname = "Helsinki-NLP/opus-mt-en-ru"

    tokenizer = AutoTokenizer.from_pretrained('./model/en-ru-local')
    model = AutoModelForSeq2SeqLM.from_pretrained('./model/en-ru-local')

    #tokenizer.save_pretrained('./model/en-ru-local')
    #model.save_pretrained('./model/en-ru-local')
    while True:
        inputs = tokenizer(mytext, return_tensors="pt")
        output = model.generate(**inputs, max_new_tokens=100)
        out_text = tokenizer.batch_decode(output, skip_special_tokens=True)
        return out_text[0]'''
    
async def send_message(bot, chat_id=vera_id, key_horoscope="daily_horoscope", greeting = "Доброе утро, солнце)\n"):
    #chat_id = sasha_id
    vera = horoscope.Horoscope('aries')
    text = getattr(vera, key_horoscope)()
    #text = transfer(text) #  перевод текста
    await bot.send_message(chat_id=chat_id, text=greeting+text)

button_horoscope1 = InlineKeyboardButton(text='Гороскоп на сегодня', callback_data='horoscope_daily_horoscope')
button_horoscope2 = InlineKeyboardButton(text='Гороскоп на завтра', callback_data='horoscope_tomorrow_horoscope')
button_horoscope3 = InlineKeyboardButton(text='Гороскоп на неделю', callback_data='horoscope_weekly_horoscope')
button_horoscope4 = InlineKeyboardButton(text='Любовный гороскоп на сегодня', callback_data='horoscope_daily_love')
button_horoscope5 = InlineKeyboardButton(text='Любовный гороскоп на завтра', callback_data='horoscope_love_tomorrow')
button_horoscope6 = InlineKeyboardButton(text='Любовный гороскоп на неделю', callback_data='horoscope_love_weekly')
button_horoscope5 = InlineKeyboardButton(text='Карьерный гороскоп на сегодня', callback_data='horoscope_daily_carrer')
button_horoscope6 = InlineKeyboardButton(text='Карьерный гороскоп на завтра', callback_data='horoscope_tomorrow_carrer')
button_horoscope6 = InlineKeyboardButton(text='Карьерный гороскоп на неделю', callback_data='horoscope_weekly_carrer')

keyboard_horoscope = InlineKeyboardMarkup(
    inline_keyboard=[[button_horoscope1], [button_horoscope2], [button_horoscope3], [button_horoscope4], [button_horoscope5], [button_horoscope6]]
)

@router.message(F.text == "Получить гороскоп")
async def proces_horoscope(message: Message, bot: Bot):
    await message.answer(text='Выбери необходимый гороскоп', reply_markup=keyboard_horoscope)

@router.message(F.text == "Получить гороскоп")
async def process_cheer_up(message: Message, bot: Bot):
    user_id = 544595768
    await send_message(bot, chat_id=user_id)


@router.callback_query(F.data.startswith("horoscope_"))
async def process_button_key(callback_query: CallbackQuery, bot: Bot):
    key_horoscope = callback_query.data[10:]
    user_id = callback_query.from_user.id
    await send_message(bot, chat_id = user_id, key_horoscope=key_horoscope, greeting='')
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )


'''
⬜⬜⬜⬜⬜⬜⬛⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜⬜⬜
⬜⬜⬜⬜⬛⬛🟥⬛⬛🟥🟥🟥🟥⬛⬛⬜⬜⬜⬜      Первый вопрос!!!
⬜⬜⬜⬛🟥🟥⬛⬛🟥🟥🟥🟥🟥🟥🟥⬛⬜⬜⬜      Какого числа произошла наша первая встреча.
⬜⬛🟥🟥⬛⬛⬛⬛🟥🟥🟥🟥🟥🟥🟥🟥🟥⬛⬜      Вставь ответ в телеграмм бот после нажатия на кнопку ключи->первый ключ в формате dd.mm.yyyy
⬜⬛🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥🟥🟥⬛⬜
⬛🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥🟥🟥⬛
⬛🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥🟥⬛
⬛🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥⬛
⬛🟥🟥🟥⬛⬛⬛⬛⬛🟥🟥⬛⬛⬛⬛⬛⬛🟥⬛
⬛🟥🟥🟥⬛⬛⬛⬛⬛🟥🟥⬛⬛⬛⬛⬛⬛🟥⬛
⬛🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥⬛
⬛🟥🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥⬛🟥⬛
⬜⬛⬛🟥🟥🟥⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥⬛⬛⬜
⬜⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥🟥🟥⬛⬜
⬜⬜⬛⬛⬛⬛⬛⬛⬛⬛⬛🟥🟥🟥🟥🟥⬛⬜⬜
⬜⬜⬜⬛🟥🟥⬛⬛⬛🟥🟥🟥🟥🟥🟥⬛⬜⬜⬜
⬜⬜⬜⬜⬛⬛🟥🟥🟥🟥🟥🟥🟥⬛⬛⬜⬜⬜⬜
⬜⬜⬜⬜⬜⬜⬛⬛⬛⬛⬛⬛⬛⬜⬜⬜⬜⬜⬜
'''
    









