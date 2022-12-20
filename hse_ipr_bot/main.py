import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import config
import data
from random import randint
from random import shuffle
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.bot_token)
dp = Dispatcher(bot, storage=storage)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

chose_menu = [types.KeyboardButton('create group'),
              types.KeyboardButton('enter key'),
              types.KeyboardButton('enter name'),
              types.KeyboardButton('find santa for everyone!'),
              types.KeyboardButton('show recipient')]

for item in chose_menu:
    markup.add(item)


# treads class
class Treads(StatesGroup):
    read_id = State()
    read_name = State()
    shuffle = State()
    write_name = State()


# for each group create key, enter key, enter name, create destribution, show whom to give present, (maybe create databese)
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = "- To create a group use 'create group' button \n \n" \
           "- Firstly enter your name \n \n" \
           "- Secondly enter you group name \n \n" \
           "- If you are sure, that everyone you wanted entered the group, you can press 'find santa for everyone!'" \
           " button to find the santa for everyone \n \n" \
           "- After that you should press 'show recipient' to see the person who's santa you are"
    await message.answer(text, reply_markup=markup)


@dp.message_handler(commands=['help'])
async def helper(message: types.Message):
    text = "- To create a group use 'create group' button \n \n" \
           "- Firstly enter your name \n \n" \
           "- Secondly enter you group name \n \n" \
           "- If you are sure, that everyone you wanted entered the group, you can press 'find santa for everyone!'" \
           " button to find the santa for everyone \n \n" \
           "- After that you should press 'show recipient' to see the person who's santa you are"
    await message.answer(text, reply_markup=markup)


@dp.message_handler(content_types='text', text='create group')
# @dp.message_handler(commands=['create_group'])
async def new_group(message: types.Message):
    id = randint(0, 1000000)
    while id in data.groups_list:
        id = randint(0, 1000000)
    data.groups_list.add(id)
    data.group[id] = []
    await message.answer("group id is: " + str(id), reply_markup=markup)


#####################################################
# entering group id

@dp.message_handler(content_types='text', text='enter key')
async def ask_for_key(message: types.Message):
    await message.answer("write id of a group you want to enter: ")
    await Treads.read_id.set()


@dp.message_handler(state=Treads.read_id)
async def reading_key(message: types.Message, state: FSMContext):
    id_str = message.text
    user_id = message.from_user.id

    if id_str.isdigit():
        if int(id_str) in data.groups_list:
            data.group[int(id_str)].append(user_id)
            data.id_group[int(user_id)] = int(id_str)
            await message.answer("you now in group: " + id_str, reply_markup=markup)
        else:
            await message.answer("unexisting group id", reply_markup=markup)
    else:
        await message.answer("invalid group id, please try again", reply_markup=markup)
    await state.finish()


#####################################################
# reading the name

@dp.message_handler(content_types='text', text='enter name')
async def ask_for_key(message: types.Message):
    await message.answer('enter your name')
    await Treads.read_name.set()


@dp.message_handler(state=Treads.read_name)
async def reading_name(message: types.Message, state: FSMContext):
    name = message.text
    user_id = message.from_user.id

    data.names[int(user_id)] = name
    await message.answer("your santa will see you as: " + name, reply_markup=markup)
    await state.finish()


#############################################################
# finding the santa
@dp.message_handler(content_types='text', text='find santa for everyone!')
async def santa_finding(message: types.Message):
    shuffle(data.group[data.id_group[message.from_user.id]])
    await message.answer("ready!", reply_markup=markup)
    # await message.answer('enter group id ')
    # await Treads.shuffle.set()


@dp.message_handler(state=Treads.shuffle)
async def reading_group_ti_shuffle(message: types.Message, state: FSMContext):
    id_str = message.text
    if int(id_str) in data.groups_list:
        shuffle(data.group[int(id_str)])
        await message.answer("ready!", reply_markup=markup)
    else:
        await message.answer("unexisting group id", reply_markup=markup)

    await state.finish()


#####################################################
# finding recipient
@dp.message_handler(content_types='text', text='show recipient')
async def giving_name(message: types.Message):
    group_id = data.id_group[message.from_user.id]
    for i, name_id in enumerate(data.group[group_id]):
        if name_id == message.from_user.id:
            if i + 1 == len(data.group[group_id]):
                await message.answer("you are to give the present to: " + data.names[data.group[group_id][0]])
            else:
                await message.answer("you are to give the present: " + data.names[data.group[group_id][i + 1]])
    # await message.answer('enter group id')
    # await Treads.write_name.set()


@dp.message_handler(state=Treads.write_name)
async def reading_group_ti_shuffle(message: types.Message, state: FSMContext):
    id_str = message.text
    if int(id_str) in data.groups_list:
        for i, name_id in enumerate(data.group[int(id_str)]):
            if name_id == message.from_user.id:
                if i + 1 == len(data.group[int(id_str)]):
                    await message.answer("you are to give the present to: " + data.names[data.group[int(id_str)][0]])
                else:
                    await message.answer("you are to give the present: " + data.names[data.group[int(id_str)][i + 1]])
    else:
        await message.answer("unexisting group id", reply_markup=markup)

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
