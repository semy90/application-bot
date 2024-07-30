from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.callback_data.delete_page_factory import DelCallbackData
from bot.callback_data.page_factory import PageCallbackData
from bot.filters import AdminFilter
from database.gateway import Database, ContactGateway

search_router = Router(name=__name__)


class TagState(StatesGroup):
    waiting = State()


@search_router.callback_query(F.data == 'search_application', AdminFilter())
async def search_application(query: CallbackQuery, state: FSMContext):
    back_button = InlineKeyboardBuilder()
    back_button.add(InlineKeyboardButton(text="Отменить", callback_data="cancel_application_send"))
    await query.message.answer("Введите номер обращения: ",
                               reply_markup=back_button.as_markup())
    await state.set_state(TagState.waiting)


@search_router.message(TagState.waiting, AdminFilter())
async def handle_feedback_message(message: Message, state: FSMContext, session_maker: async_sessionmaker):
    app = ContactGateway(session_maker())
    text = message.text

    if not text.isdigit():
        await message.answer("Попробуйте повторно и введите ТОЛЬКО цифры")
        await state.clear()
        return

    cur_application = await app.get_application_by_tag(int(text))

    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text="Удалить", callback_data=DelCallbackData(page=0, id=int(text)).pack()))
    try:
        await message.answer(
            f"Обращение от пользователя:\n\n{cur_application['text']}\n\nНомер обращения: {cur_application['id']}\nusername : @{cur_application['username']}, ID: {cur_application['user_id']}",
            reply_markup=button.as_markup()

        )
    except TypeError:
        await message.answer(
            "Обращения не существует!"
        )

    await state.clear()


@search_router.callback_query(F.data == "cancel_application_send", AdminFilter())
async def cancel_feedback(query: CallbackQuery, state: FSMContext):
    await query.message.answer('Отменено!')
    await state.clear()