import dotenv
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
import keyboards as kb
from filters import CarSelection, state_names
from database import save_application
from dotenv import load_dotenv
import os

ADMINS = [int(id_str) for id_str in os.environ.get('ADMINS', '').split(',') if id_str.strip()]

user = Router()



@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    # Очищаем состояние при старте
    await state.clear()
    await message.answer("Привет, это бот компании AutoClick, мы специализируемся на подборе и доставке автомобилей из Китая, Кореи и Японии. Что вас интересует сейчас?", reply_markup=kb.menu_start)


@user.callback_query(F.data.startswith("Ca"))
async def Car(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.purpose)
        await callback.answer()
        await callback.message.edit_text(
            "Вы хотите выбрать автомобиль по марке или по стране подбора?",
            reply_markup=kb.q0_country_or_marc
        )
        await state.set_state(CarSelection.marc_or_country)
    

@user.callback_query(F.data.startswith("q0_"))
async def q0_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Подбор автомобиля")
    if callback.data == "q0_marc":
        await callback.message.answer("Теперь выберите марку автомобиля", reply_markup=kb.q2_marc)
        await state.set_state(CarSelection.marc)
    elif callback.data == "q0_country":
        await callback.message.answer(
            "Выберите страну, из которой будет доставлен автомобиль",
            reply_markup=kb.q1_country
        )
        await state.set_state(CarSelection.country)


# ========== ОСНОВНЫЕ ОБРАБОТЧИКИ ==========

@user.callback_query(F.data.startswith("q1_"))
async def q1_country(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.country)
        await callback.message.answer("Теперь выберите марку автомобиля", reply_markup=kb.q2_marc)
        await state.set_state(CarSelection.marc)


@user.callback_query(F.data.startswith("q2_"))
async def q2_marc(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.marc)
        marc_name = callback.data.replace("q2_", "")
        models_keyboard = kb.q3_model_dinamic(marc_name)
        await callback.message.answer("Выберите модель", reply_markup=models_keyboard)
        await state.set_state(CarSelection.model)


@user.callback_query(F.data.startswith("q3_"))
async def q3_model(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.model)
        await callback.message.answer("Выберите тип КПП", reply_markup=kb.q4_type_kpp)
        await state.set_state(CarSelection.type_kpp)


@user.callback_query(F.data.startswith("q4_"))
async def q4_type_kpp(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.type_kpp)
        await callback.message.answer("Введите бюджет (в рублях)", reply_markup=None)
        await state.set_state(CarSelection.budget)


@user.message(CarSelection.budget)
async def process_budget(message: Message, state: FSMContext):
    await state.update_data({"Бюджет": message.text})
    await message.answer("Когда планируете покупку?", reply_markup=None)
    await state.set_state(CarSelection.timing)


@user.message(CarSelection.timing)
async def process_timing(message: Message, state: FSMContext):
    await state.update_data({"Когда планируете покупку": message.text})
    await message.answer(
        "Основные ответы получены! Хотите отправить заявку на подбор автомобиля сейчас или выбрать дополнительные характеристики?",
        reply_markup=kb.q7_dop_or_done
    )
    await state.set_state(CarSelection.contact)


@user.callback_query(F.data == "q7_Дальше")
async def q7_dop_or_done(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Выберите тип руля", reply_markup=kb.q8_wheel_type)
    await state.set_state(CarSelection.wheel_type)


@user.callback_query(F.data.startswith("q8_"))
async def q8_wheel_type(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.wheel_type)
        await callback.message.answer("Выберите тип кузова", reply_markup=kb.q9_body_type)
        await state.set_state(CarSelection.body_type)


@user.callback_query(F.data.startswith("q9_"))
async def q9_body_type(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.body_type)
        await callback.message.answer("Выберите год выпуска", reply_markup=kb.q10_year)
        await state.set_state(CarSelection.year)


@user.callback_query(F.data.startswith("q10_"))
async def q10_year(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.year)
        await callback.message.answer("Выберите вид топлива", reply_markup=kb.q11_fuel)
        await state.set_state(CarSelection.fuel)


@user.callback_query(F.data.startswith("q11_"))
async def q11_fuel(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.fuel)
        await callback.message.answer("Выберите объем двигателя", reply_markup=kb.q12_engine)
        await state.set_state(CarSelection.engine)


@user.callback_query(F.data.startswith("q12_"))
async def q12_engine(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.engine)
        await callback.message.answer("Выберите пробег", reply_markup=kb.q13_mileage)
        await state.set_state(CarSelection.mileage)


@user.callback_query(F.data.startswith("q13_"))
async def q13_mileage(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.mileage)
        await callback.message.answer("Выберите тип привода", reply_markup=kb.q14_drive_type)
        await state.set_state(CarSelection.drive_type)


@user.callback_query(F.data.startswith("q14_"))
async def q14_drive_type(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.drive_type)
        await callback.message.answer("Выберите цвет", reply_markup=kb.q15_color)
        await state.set_state(CarSelection.color)


@user.callback_query(F.data.startswith("q15_"))
async def q15_color(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.color)
        await callback.message.answer("Выберите комплектацию", reply_markup=kb.q16_complete)
        await state.set_state(CarSelection.complete)


@user.callback_query(F.data.startswith("q16_"))
async def q16_complete(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, Message) and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.complete)
        await callback.message.answer("Введите дополнительные пожелания", reply_markup=None)
        await state.set_state(CarSelection.dop)


@user.message(CarSelection.dop)
async def process_dop(message: Message, state: FSMContext):
    await state.update_data({"Дополнительные пожелания": message.text})
    await message.answer("Отлично! Данные сохранены. Отправить заявку?", reply_markup=kb.send_request)


# ========== УНИВЕРСАЛЬНАЯ ФУНКЦИЯ СОХРАНЕНИЯ ==========

async def update_user_data(callback: CallbackQuery, state: FSMContext, current_state: State):
    """
    Универсальная функция сохранения данных.
    Сохраняет сразу на русском языке в словарь вида {название_поля: значение}

    Args:
        callback: объект callback
        state: состояние FSM
        current_state: текущее состояние (например CarSelection.country)
        field_name: русское название поля (например "Страна")
        value: значение для сохранения (например "Japan")
        state_names: словарь соответствия состояний и русских названий
    """
    if not callback.data or callback.data == "clear":
        return None

    # Извлекаем значение из callback_data (начиная с 6 символа, после "q1_", "q2_" и т.д.)
    # Например: "q1_Japan" -> "Japan", "q2_Toyota" -> "Toyota"
    # "q4_механика" -> "механика", "q9_Седан" -> "Седан"
    value = callback.data.split("_", 1)[1] if "_" in callback.data else callback.data

    # Получаем русское название поля из state_names
    field_name = state_names.get(current_state.state, current_state.state)

    # Сохраняем в виде {русское_название: значение}
    await state.update_data({field_name: value})

    await callback.answer(f"✅ Вы выбрали {value}")

    if isinstance(callback.message, Message):
        try:
            await callback.message.edit_text(f"✅ {field_name}: {value}")
        except Exception:
            pass

    return value


# ========== КНОПКА "СВОЙ ВАРИАНТ" ==========

@user.callback_query(F.data == "Свой вариант")
async def user_version(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()

    # Получаем русское название поля
    field_name = state_names.get(current_state, current_state)

    await callback.message.answer(f"Введите {field_name.lower()}:")


# ========== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ==========

@user.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    # Получаем текущее состояние
    current_state = await state.get_state()

    # Если есть активное состояние - обрабатываем как ответ на вопрос
    if current_state is not None:
        # Получаем русское название поля
        field_name = state_names.get(current_state, current_state)

        # Сохраняем введённое значение с русским ключом
        await state.update_data({field_name: message.text})

        await message.answer(f"✅ {field_name}: {message.text}")

        # Переход к следующему шагу в зависимости от состояния
        if current_state == CarSelection.marc.state:
            await message.answer("Введите модель", reply_markup=None)
            await state.set_state(CarSelection.model)
        elif current_state == CarSelection.model.state:
            await message.answer("Выберите тип коробки передач", reply_markup=kb.q4_type_kpp)
            await state.set_state(CarSelection.type_kpp)
        elif current_state == CarSelection.budget.state:
            await message.answer("Когда планируете покупку?", reply_markup=None)
            await state.set_state(CarSelection.timing)
        elif current_state == CarSelection.timing.state:
            await message.answer(
                "Основные ответы получены! Хотите отправить заявку на подбор автомобиля сейчас или выбрать дополнительные характеристики?",
                reply_markup=kb.q7_dop_or_done
            )
            await state.set_state(CarSelection.contact)
        elif current_state == CarSelection.body_type.state:
            await message.answer("Выберите год выпуска", reply_markup=kb.q10_year)
            await state.set_state(CarSelection.year)
        elif current_state == CarSelection.year.state:
            await message.answer("Выберите тип топлива", reply_markup=kb.q11_fuel)
            await state.set_state(CarSelection.fuel)
        elif current_state == CarSelection.engine.state:
            await message.answer("Выберите пробег", reply_markup=kb.q13_mileage)
            await state.set_state(CarSelection.mileage)
        elif current_state == CarSelection.mileage.state:
            await message.answer("Выберите тип привода", reply_markup=kb.q14_drive_type)
            await state.set_state(CarSelection.drive_type)
        elif current_state == CarSelection.color.state:
            await message.answer("Выберите комплектацию", reply_markup=kb.q16_complete)
            await state.set_state(CarSelection.complete)
        elif current_state == CarSelection.dop.state:
            await message.answer("Отлично! Данные сохранены. Отправить заявку?", reply_markup=kb.send_request)
    else:
        # Если нет активного состояния - показываем стартовое меню
        if message.text.lower() == "привет":
            await message.answer("Привет! Как дела? Подскажите, что вас интересует сейчас?", reply_markup=kb.menu_start)
        else:
            await message.answer(
                "Не понимаю, вас. Подскажите, что вас интересует сейчас?",
                reply_markup=kb.menu_start
            )



# ========== ФУНКЦИИ ДЛЯ ОТЧЁТОВ ==========

def generate_user_report(user_data: dict, user) -> str:
    """
    Формирует краткий отчёт для пользователя (без username и ID)
    """
    report_lines = [
        "📝 **Ваша заявка на подбор автомобиля**",
        "=" * 35,
        "",
        "👤 **Клиент:**",
        f"• Имя: {user.full_name}",
        "",
        "🚗 **Параметры подбора:**",
    ]

    # Проходим по всем сохранённым данным
    for field_name, value in user_data.items():
        if value and value != "—":
            report_lines.append(f"• **{field_name}:** {value}")

    report_lines.extend([
        "",
        "=" * 35,
        "✅ Менеджер свяжется с вами в ближайшее время!"
    ])

    return "\n".join(report_lines)



def convert_db_row_to_user_data(row: dict) -> dict:
    """
    Преобразует строку из базы данных в формат user_data
    используя state_names для ключей
    """
    user_data = {}

    for russian_name in state_names.values():
        db_key = russian_name.replace(" ", "_")
        if db_key in row and row[db_key]:
            user_data[russian_name] = row[db_key]

    return user_data


def generate_manager_report(user_data: dict, user) -> str:
    """
    Формирует полный отчёт для менеджера (с username и ID)
    """
    report_lines = [
        "📝 **Новая заявка на подбор автомобиля**",
        "=" * 35,
        "",
        "👤 **Информация о клиенте:**",
        f"• Имя: {user.full_name}",
        f"• Username: @{user.username if user.username else 'не указан'}",
        f"• Telegram ID: {user.id}",
        "",
        "🚗 **Параметры подбора:**",
    ]

    for field_name, value in user_data.items():
        if value and value != "—":
            report_lines.append(f"• **{field_name}:** {value}")

    report_lines.extend([
        "",
        "=" * 35,
        "✅ Свяжитесь с клиентом в ближайшее время!"
    ])

    return "\n".join(report_lines)


# ========== КНОПКА "ОТПРАВИТЬ" ==========

@user.callback_query(F.data == "Done")
async def done(callback: CallbackQuery, state: FSMContext):
    # Получаем все собранные данные (уже на русском!)
    user_data = await state.get_data()

    # Сохраняем заявку в базу данных
    app_id = save_application(user_data, callback.from_user)

    # Формируем отчёт для пользователя
    user_report = generate_user_report(user_data, callback.from_user)

    # Формируем отчёт для менеджера
    manager_report = generate_manager_report(user_data, callback.from_user)
    manager_report = f"🆔 **ID заявки:** {app_id}\n\n{manager_report}"

    # Показываем краткий отчёт пользователю
    await callback.message.edit_text(
        user_report,
        reply_markup=None
    )

      # замените на реальный ID
    await callback.bot.send_message(ADMINS[0], manager_report)

    await state.clear()
    
# ========== КНОПКА "ОЧИСТИТЬ" ==========

@user.callback_query(F.data == "clear")
async def clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы начали сначала")
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.answer("Начинаем заново. Подскажите, что вас интересует сейчас?", reply_markup=kb.menu_start)


# ========== АДМИН-КОМАНДЫ ==========

@user.message(Command("admin"))
async def admin_panel(message: Message):
    """Панель администратора"""
    if message.from_user.id not in ADMINS:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    #count = get_applications_count()

    await message.answer(
        f"👑 **Панель администратора**\n\n"
        f"📊 **Всего заявок:** \n\n"
        f"**Доступные команды:**\n"
        f"• `/last_applications` — последние 10 заявок (кратко)\n"
        f"• `/last_applications 5` — последние N заявок\n"
        f"• `/application 5` — подробная заявка по ID\n"
        f"• `/export` — скачать все заявки в CSV\n\n"
        f"Также можно использовать:\n"
        f"• `/last_applications all` — все заявки (осторожно, много!)"
    )
        
        


# ========== HELP ==========

@user.message(Command("help"))
async def help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Я могу помочь подобрать автомобиль!\n\n"
        "Команды:\n"
        "/start - начать подбор\n"
        "/help - помощь\n\n"
        "Или просто нажмите кнопку 'Подобрать автомобиль' в меню.",
        reply_markup=kb.menu_start
    )