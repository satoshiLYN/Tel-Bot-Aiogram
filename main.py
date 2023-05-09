from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
from defDB import BotDB
from ryba import quotes
from sticker import stickers
import os
import random

BotDB = BotDB('ryba.db')

START_COMMAND = """
/start - начать работу
/paste - поделиться мудростью
/moss - выдать мох
/mosswallet - узнать номер своего кошелька с мохом и счет
/mosstrans - отправить свой мох кому-нибудь
"""

load_dotenv()
storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN_API'))
dp = Dispatcher(bot, storage=storage)


class MossTrans(StatesGroup):
    wallet = State()
    countMoss = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
        wallet = int(''.join(map(str, random.sample("0123456789", 5))))
        if wallet < 10000:
            wallet = wallet * 10
        while BotDB.wallet_exists(wallet):
            wallet = int(''.join(map(str, random.sample("0123456789", 5))))
            while wallet < 10000:
                wallet = wallet * 10
        BotDB.add_wallet(wallet, message.from_user.id)
    await message.bot.send_message(message.from_user.id, START_COMMAND)


@dp.message_handler(commands=['moss'])
async def moss_command(message: types.Message):
    await message.answer(text="""это вам подарок мох 🦠
больше у меня нечего нет""")
    BotDB.add_moss(message.from_user.id)
    await message.answer(text="Мха накоплено: " + BotDB.moss_from_userid(message.from_user.id) +
                         "\nОбщий фонд мохов: " + BotDB.moss_cum())


@dp.message_handler(commands=['mosswallet'])
async def mosswallet(message: types.Message):
    await message.answer(text="Номер кошелька: " + BotDB.get_wallet(message.chat.id) +
                         "\nМха накоплено: " + BotDB.moss_from_userid(message.from_user.id))


@dp.message_handler(commands=['mosstrans'])
async def mosstrans(message: types.Message):
    await message.answer(text="Напишите номер кошелька, куда отправить ваш мох")
    await MossTrans.wallet.set()


@dp.message_handler(state=MossTrans.wallet)
async def mosstrans2(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer(text="Вы ввели не цифры или дробное число, введите заново.")
        return
    numwallet = int(message.text)
    if not BotDB.check_wallet(numwallet):
        await message.answer(text="Такого кошелька нет, введите заново.")
        return
    else:
        await state.update_data(numwallet=numwallet)
        await message.answer("Отлично! Теперь введите количество пересылаемого моха.")
        await MossTrans.next()


@dp.message_handler(state=MossTrans.countMoss)
async def mosstrans3(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except ValueError:
        await message.answer(text="Вы ввели не цифры или дробное число, введите заново.")
        return
    nummoss = int(message.text)
    data = await state.get_data()
    if nummoss < 0:
        await message.answer(text="Ну и ну! Вы разочаровали партию своим решением скрасть мох.")
        if nummoss < (-5):
            await message.answer(text="Ваши рутьки не могут унести больше 5 мохов из чужого кармана. " +
                                      "Введите число заново. \nМожно одуматься красть.")
            return
        elif int(BotDB.moss_from_wallet(int(data['numwallet']))) + nummoss < 0:
            await message.answer(
                text="У пользователя нет столько моха... Введите число заново. Можно одуматься красть.")
            return
        else:
            await state.update_data(nummoss=nummoss)
            data = await state.get_data()
            BotDB.trans_moss(int(data['numwallet']), int(data['nummoss']), message.chat.id)
            await message.answer(text="Мох успешно скраден." +
                                 "\nУ вас " + BotDB.moss_from_userid(message.from_user.id) + "🦠")
            await bot.send_message(int(BotDB.get_chat(int(data['numwallet']))),
                                   "Ну и ну! У вас украли мох :( 🦠" + str(nummoss))
            await state.finish()
    elif int(BotDB.moss_from_userid(message.from_user.id)) - nummoss < 0:
        await message.answer(text="У вас не хватает моха, введите заново.")
        return
    else:
        await state.update_data(nummoss=nummoss)
        data = await state.get_data()
        BotDB.trans_moss(int(data['numwallet']), int(data['nummoss']), message.chat.id)
        await message.answer(text="Мох успешно доставлен." +
                             "\nОсталось " + BotDB.moss_from_userid(message.from_user.id) + "🦠")
        await bot.send_message(int(BotDB.get_chat(int(data['numwallet']))), "Вам прислали мох 🦠 +" + str(nummoss))
        await state.finish()


@dp.message_handler(commands=['paste'])
async def paste_command(message: types.Message):
    await message.answer(text=random.choice(quotes))


@dp.message_handler(commands=['admincmd'])
async def admin_command(message: types.Message):
    text = message.text
    text_res = text.replace('/admincmd', '')
    max_id = int(BotDB.max_id())
    i = 1
    while i <= max_id:
        await bot.send_message(int(BotDB.userid_from_id(i)), """В данный момент над ботом проводятся технические работы.
Просьба не крутить мохи, чтобы не потерять их.
Пометка админа:""" + text_res)
        i += 1


@dp.message_handler(commands=['admincmdstop'])
async def admin_command2(message: types.Message):
    max_id = int(BotDB.max_id())
    i = 1
    while i <= max_id:
        await bot.send_message(int(BotDB.userid_from_id(i)), "Работы завершены. Ботом можно пользоваться.")
        i += 1


@dp.message_handler(content_types=[types.ContentType.STICKER])
async def echo_sticker(message: types.Message):
    await bot.send_sticker(message.from_user.id, sticker=random.choice(stickers))


@dp.message_handler(content_types=[
    types.ContentType.ANIMATION,
    types.ContentType.PHOTO,
    types.ContentType.DOCUMENT,
    types.ContentType.VOICE
]
)
async def echo_uncontent_a(message: types.Message):
    await message.answer(text='рыба не поняла.......')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(text=random.choice(quotes))


if __name__ == '__main__':
    executor.start_polling(dp)
