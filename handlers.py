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
import json
from pathlib import Path

load_dotenv()

ADMINS = [int(id_str) for id_str in os.environ.get('ADMINS', '').split(',') if id_str.strip()]
ADMINS_MAX = [int(id_str) for id_str in os.environ.get('ADMINS_MAX', '').split(',') if id_str.strip()]

# Файл для хранения MAX chat_id администраторов (user_id → chat_id)
_MAX_CHAT_IDS_FILE = Path(__file__).parent / "max_admin_chats.json"

def _load_max_chat_ids() -> dict:
    if _MAX_CHAT_IDS_FILE.exists():
        try:
            return {int(k): int(v) for k, v in json.loads(_MAX_CHAT_IDS_FILE.read_text()).items()}
        except Exception:
            pass
    return {}

def _save_max_chat_ids(mapping: dict):
    try:
        _MAX_CHAT_IDS_FILE.write_text(json.dumps({str(k): v for k, v in mapping.items()}))
    except Exception:
        pass

_max_admin_chat_ids: dict = _load_max_chat_ids()

user = Router()

@user.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    _remember_max_admin_chat(message)
    await message.answer(
        "Привет, это бот компании AutoClick, мы специализируемся на подборе и доставке автомобилей из Китая, Кореи и Японии. Что вас интересует сейчас?",
        reply_markup=kb.menu_start
    )

@user.callback_query(F.data.startswith("Ca"))
async def Car(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
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
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.country)
        await callback.message.answer("Теперь выберите марку автомобиля", reply_markup=kb.q2_marc)
        await state.set_state(CarSelection.marc)

@user.callback_query(F.data.startswith("q2_"))
async def q2_marc(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.marc)
        marc_name = callback.data.replace("q2_", "")
        models_keyboard = kb.q3_model_dinamic(marc_name)
        await callback.message.answer("Выберите модель", reply_markup=models_keyboard)
        await state.set_state(CarSelection.model)

@user.callback_query(F.data.startswith("q3_"))
async def q3_model(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.model)
        await callback.message.answer("Выберите тип КПП", reply_markup=kb.q4_type_kpp)
        await state.set_state(CarSelection.type_kpp)

@user.callback_query(F.data.startswith("q4_"))
async def q4_type_kpp(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
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
    await message.answer("В какой город нужно доставить автомобиль?")
    await state.set_state(CarSelection.city)

@user.message(CarSelection.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data({"Город доставки": message.text})
    await message.answer(
        "Рекомендуем добавить контакт для связи",
        reply_markup=kb.send_contact
    )
    await state.set_state(CarSelection.tel)

@user.callback_query(F.data.startswith("cnt_"))
async def request_contact(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "cnt_contact":
        is_max = type(callback).__name__ == 'MaxCallbackQuery'
        if is_max:
            await callback.message.answer(
                "Пожалуйста, введите ваш номер телефона в ответном сообщении:"
            )
        else:
            await callback.message.answer(
                "Пожалуйста, введите ваш номер телефона\n"
                "Либо нажмите на кнопку: Отправить контакт",
                reply_markup=kb.contact
            )
    else:
        await callback.message.answer(
            "Основные ответы получены! Хотите отправить заявку на подбор автомобиля сейчас или выбрать дополнительные характеристики?",
            reply_markup=kb.q7_dop_or_done
        )

@user.message(F.contact)
async def handle_contact(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == CarSelection.tel.state:
        phone = message.contact.phone_number
        await state.update_data({"Телефон": phone})
        await message.answer("✅ Контакт сохранён.", reply_markup=None)
        await message.answer(
            "Основные ответы получены! Хотите отправить заявку на подбор автомобиля сейчас или выбрать дополнительные характеристики?",
            reply_markup=kb.q7_dop_or_done
        )
    else:
        await message.answer(
            "Подскажите, что вас интересует сейчас?",
            reply_markup=kb.menu_start
        )

@user.callback_query(F.data == "q7_Дальше")
async def q7_dop_or_done(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Выберите тип руля", reply_markup=kb.q8_wheel_type)
    await state.set_state(CarSelection.wheel_type)

@user.callback_query(F.data.startswith("q8_"))
async def q8_wheel_type(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.wheel_type)
        await callback.message.answer("Выберите тип кузова", reply_markup=kb.q9_body_type)
        await state.set_state(CarSelection.body_type)

@user.callback_query(F.data.startswith("q9_"))
async def q9_body_type(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.body_type)
        await callback.message.answer("Выберите год выпуска", reply_markup=kb.q10_year)
        await state.set_state(CarSelection.year)

@user.callback_query(F.data.startswith("q10_"))
async def q10_year(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.year)
        await callback.message.answer("Выберите вид топлива", reply_markup=kb.q11_fuel)
        await state.set_state(CarSelection.fuel)

@user.callback_query(F.data.startswith("q11_"))
async def q11_fuel(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.fuel)
        await callback.message.answer("Выберите объем двигателя", reply_markup=kb.q12_engine)
        await state.set_state(CarSelection.engine)

@user.callback_query(F.data.startswith("q12_"))
async def q12_engine(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.engine)
        await callback.message.answer("Выберите пробег", reply_markup=kb.q13_mileage)
        await state.set_state(CarSelection.mileage)

@user.callback_query(F.data.startswith("q13_"))
async def q13_mileage(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.mileage)
        await callback.message.answer("Выберите тип привода", reply_markup=kb.q14_drive_type)
        await state.set_state(CarSelection.drive_type)

@user.callback_query(F.data.startswith("q14_"))
async def q14_drive_type(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.drive_type)
        await callback.message.answer("Выберите цвет", reply_markup=kb.q15_color)
        await state.set_state(CarSelection.color)

@user.callback_query(F.data.startswith("q15_"))
async def q15_color(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.color)
        await callback.message.answer("Выберите комплектацию", reply_markup=kb.q16_complete)
        await state.set_state(CarSelection.complete)

@user.callback_query(F.data.startswith("q16_"))
async def q16_complete(callback: CallbackQuery, state: FSMContext):
    if callback.message is not None and callback.data and callback.data != "clear":
        await update_user_data(callback, state, CarSelection.complete)
        await callback.message.answer("Введите дополнительные пожелания", reply_markup=None)
        await state.set_state(CarSelection.dop)

# ========== УНИВЕРСАЛЬНАЯ ФУНКЦИЯ СОХРАНЕНИЯ ==========

async def update_user_data(callback: CallbackQuery, state: FSMContext, current_state: State):
    if not callback.data or callback.data == "clear":
        return None

    value = callback.data.split("_", 1)[1] if "_" in callback.data else callback.data
    field_name = state_names.get(current_state.state, current_state.state)
    await state.update_data({field_name: value})
    await callback.answer(f"✅ Вы выбрали {value}")

    if callback.message is not None:
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
    field_name = state_names.get(current_state, current_state)

    if field_name is None:
        await callback.answer("Нет активного состояния", show_alert=True)
        return

    await callback.message.answer(f"Введите {field_name.lower()}:")

# ========== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (только для состояний без отдельных хендлеров) ==========

@user.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        field_name = state_names.get(current_state, current_state)
        await state.update_data({field_name: message.text})
        await message.answer(f"✅ {field_name}: {message.text}")

        # Переходы для состояний, у которых нет отдельных хендлеров
        if current_state == CarSelection.marc.state:
            await message.answer("Введите модель", reply_markup=None)
            await state.set_state(CarSelection.model)
        elif current_state == CarSelection.model.state:
            await message.answer("Выберите тип коробки передач", reply_markup=kb.q4_type_kpp)
            await state.set_state(CarSelection.type_kpp)
        elif current_state == CarSelection.body_type.state:
            await message.answer("Выберите год выпуска", reply_markup=kb.q10_year)
            await state.set_state(CarSelection.year)
        elif current_state == CarSelection.year.state:
            await message.answer("Выберите вид топлива", reply_markup=kb.q11_fuel)
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
            await message.answer(
                "Отлично! Данные для заявки сохранены. Отправить заявку?",
                reply_markup=kb.send_request
            )
        # остальные состояния (budget, timing, city, tel, dop_or_done) уже обрабатываются отдельными хендлерами
    else:
        if message.text.lower() == "привет":
            await message.answer(
                "Привет! Как дела? Подскажите, что вас интересует сейчас?",
                reply_markup=kb.menu_start
            )
        else:
            await message.answer(
                "Не понимаю, вас. Подскажите, что вас интересует сейчас?",
                reply_markup=kb.menu_start
            )

# ========== ФУНКЦИИ ДЛЯ ОТЧЁТОВ ==========

def generate_user_report(user_data: dict, user) -> str:
    report_lines = [
        "📝 Ваша заявка на подбор автомобиля",
        "=" * 35,
        "",
        "👤 Клиент:",
        f"• Имя: {user.full_name}",
        "",
        "🚗 Параметры подбора:",
    ]

    for field_name, value in user_data.items():
        if value and value != "—":
            report_lines.append(f"• {field_name}: {value}")

    report_lines.extend([
        "",
        "=" * 35,
        "✅ Менеджер свяжется с вами в ближайшее время!"
    ])

    return "\n".join(report_lines)

def generate_manager_report(user_data: dict, user, platform: str = 'telegram') -> str:
    if hasattr(user, 'full_name') and user.full_name:
        full_name = user.full_name
    else:
        first = getattr(user, 'first_name', '')
        last = getattr(user, 'last_name', '')
        full_name = f"{first} {last}".strip()
        if not full_name:
            full_name = "Пользователь"

    if platform == 'max':
        user_link = f'<a href="max://user/{user.id}">{full_name}</a>'
        report_lines = [
            "📝 Новая заявка на подбор автомобиля",
            "=" * 35,
            "",
            "👤 Информация о клиенте:",
            f"• Имя: {user_link}",
            "",
            "🚗 Параметры подбора:",
        ]
    else:
        user_link = f'<a href="tg://user?id={user.id}">{full_name}</a>'
        username = f"@{user.username}" if user.username else "не указан"
        report_lines = [
            "📝 Новая заявка на подбор автомобиля",
            "=" * 35,
            "",
            "👤 Информация о клиенте:",
            f"• Имя: {user_link}",
            f"• Username: {username}",
            f"• Telegram ID: {user.id}",
            "",
            "🚗 Параметры подбора:",
        ]

    for field_name, value in user_data.items():
        if value and value != "—":
            report_lines.append(f"• {field_name}: {value}")

    report_lines.extend([
        "",
        "=" * 35,
        "✅ Свяжитесь с клиентом в ближайшее время!"
    ])

    return "\n".join(report_lines)

def convert_db_row_to_user_data(row: dict) -> dict:
    user_data = {}
    for russian_name in state_names.values():
        db_key = russian_name.replace(" ", "_")
        if db_key in row and row[db_key]:
            user_data[russian_name] = row[db_key]
    return user_data

def _remember_max_admin_chat(message):
    from_user = getattr(message, 'from_user', None)
    if from_user is None:
        return
    user_id = getattr(from_user, 'id', None)
    if user_id not in ADMINS_MAX:
        return
    chat = getattr(message, 'chat', None)
    chat_id = getattr(chat, 'id', None) if chat else None
    if chat_id is None and hasattr(message, '_chat_id_for_send'):
        chat_id = message._chat_id_for_send()
    if chat_id and _max_admin_chat_ids.get(user_id) != chat_id:
        _max_admin_chat_ids[user_id] = chat_id
        _save_max_chat_ids(_max_admin_chat_ids)
        print(f"✅ MAX-администратор {user_id} → chat_id={chat_id} сохранён")

async def _notify_admin(callback, text: str):
    is_max = not hasattr(type(callback), 'bot') or getattr(callback, 'bot', None) is None

    if is_max:
        admins = ADMINS_MAX if ADMINS_MAX else []
        if not admins:
            return

        max_bot = getattr(callback.message, '_bot', None)
        if not max_bot and hasattr(callback, 'bot') and callback.bot is not None:
            max_bot = callback.bot
            print("🔍 Используем callback.bot как max_bot")
        if not max_bot:
            print("⚠️ MAX бот не найден ни в callback.message._bot, ни в callback.bot")
            return

        for admin_id in admins:
            try:
                chat_id = _max_admin_chat_ids.get(admin_id)
                if chat_id:
                    await max_bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        format="html"
                    )
                else:
                    print(f"⚠️ MAX-администратор {admin_id} ещё не писал боту. Попросите его отправить /start боту в MAX.")
            except Exception as e:
                print(f"Ошибка отправки уведомления MAX-админу {admin_id}: {e}")
    else:
        admins = ADMINS if ADMINS else []
        if not admins:
            return

        for admin_id in admins:
            try:
                await callback.bot.send_message(
                    admin_id,
                    text,
                    parse_mode="html"
                )
            except Exception as e:
                print(f"Ошибка отправки уведомления TG-админу {admin_id}: {e}")

# ========== КНОПКА "ОТПРАВИТЬ" ==========

@user.callback_query(F.data == "Done")
async def done(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    app_id = save_application(user_data, callback.from_user)

    is_max = not hasattr(type(callback), 'bot') or getattr(callback, 'bot', None) is None
    platform = 'max' if is_max else 'telegram'

    user_report = generate_user_report(user_data, callback.from_user)
    manager_report = generate_manager_report(user_data, callback.from_user, platform=platform)
    manager_report = f"🆔 ID заявки: {app_id}\n\n{manager_report}"

    await callback.message.edit_text(user_report, reply_markup=None)
    await _notify_admin(callback, manager_report)
    await state.clear()

# ========== КНОПКА "ОЧИСТИТЬ" ==========

@user.callback_query(F.data == "clear")
async def clear(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Вы начали сначала")
    await state.clear()
    if callback.message is not None:
        await callback.message.answer(
            "Начинаем заново. Подскажите, что вас интересует сейчас?",
            reply_markup=kb.menu_start
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
