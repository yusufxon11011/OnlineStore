from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.admin_inline_keyboards import make_category_list, make_product_list, make_ad_list
from states.admin_states import CategoryStates, ProductStates, AdStates
from utils.database import Database
from utils.my_commands import commands_admin, commands_user

commands_router = Router()
db = Database(DB_NAME)


@commands_router.message(CommandStart())
async def start_handler(message: Message):
    if message.from_user.id in admins:
        await message.bot.set_my_commands(commands=commands_admin)
        await message.answer("Welcome admin, please choose command from commands list")
    else:
        await message.bot.set_my_commands(commands=commands_user)
        await message.answer("Let's start registration")


@commands_router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("All actions canceled, you may continue sending commands")


# With this handler admin can add new category
@commands_router.message(Command('new_category'))
async def new_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.newCategory_state)
    await message.answer("Please, send new category name ...")


# Functions for editing category name
@commands_router.message(Command('edit_category'))
async def edit_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.updCategory_state_list)
    await message.answer(
        text="Choose category name which you want to change...",
        reply_markup=make_category_list()
    )

@commands_router.message(Command('del_category'))
async def del_category_handler(message: Message, state: FSMContext):
    await state.set_state(CategoryStates.delCategory_state)
    await message.answer(
        text="Choose category name which you want to delete...",
        reply_markup=make_category_list()
    )

@commands_router.message(Command('del_product'))
async def del_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.delProduct_state)
    await message.answer(
        text="Write product name which you want to delete...",
        reply_markup=make_product_list()
    )

@commands_router.message(Command('new_product'))
async def new_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.newProduct_state)
    await message.answer("Please, send new product name ...")


@commands_router.callback_query(CategoryStates.updCategory_state_list)
async def callback_category_edit(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cat_name=callback.data)
    await state.set_state(CategoryStates.updCategory_state_new)
    await callback.message.answer(f"Please, send new name for category '{callback.data}'")
    await callback.message.delete()


@commands_router.message(CategoryStates.updCategory_state_new)
async def set_new_category_name(message: Message, state: FSMContext):
    new_cat = message.text
    st_data = await state.get_data()
    old_cat = st_data.get('cat_name')
    res = db.upd_category(message.text, old_cat)
    if res['status']:
        await message.answer("Category name successfully changed")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])

@commands_router.message(Command('edit_product'))
async def edit_product_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.updProduct_state_list)
    await message.answer(
        text="Choose product name which you want to change...",
        reply_markup=make_product_list()
    )

@commands_router.message(Command('edit_ad'))
async def edit_ad_handler(message: Message, state: FSMContext):
    await state.set_state(ProductStates.updProduct_state_list)
    await message.answer(
        text="Choose ad name which you want to change...",
        reply_markup=make_ad_list()
    )

@commands_router.message(Command('del_ad'))
async def del_ad_handler(message: Message, state: FSMContext):
    await state.set_state(AdStates.delAd_state)
    await message.answer(
        text="Write ad name which you want to delete...",
        reply_markup=make_ad_list()
    )

@commands_router.message(Command('search_ad'))
async def search_ad_handler(message: Message, state: FSMContext):
    await state.set_state(AdStates.searchAd_state)
    await message.answer(
        text="Write the name of the ad you want to search for...",
        reply_markup=make_ad_list()
    )