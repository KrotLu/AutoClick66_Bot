import requests
import keyword
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import read_xl as xl


menu_start = InlineKeyboardMarkup(
inline_keyboard=[
        [InlineKeyboardButton(text="Понять стоимость", callback_data="Ca_Понять стоимость"),  ],
        [InlineKeyboardButton(text="Сориентироваться на будущую покупку", callback_data="Ca_Сориентироваться")],
        [InlineKeyboardButton(text="Подобрать автомобиль", callback_data="Ca_Подобрать автомобиль")]
    ]
)

q0_country_or_marc = InlineKeyboardMarkup(
  inline_keyboard=[
    [InlineKeyboardButton(text="По марке", callback_data="q0_marc")],
    [InlineKeyboardButton(text="По стране", callback_data="q0_country")]]
)
  

q1_country_builder = InlineKeyboardBuilder()
q1_country_builder.add(
  InlineKeyboardButton(text="Japan", callback_data="q1_Japan"),
  InlineKeyboardButton(text="China", callback_data="q1_China"),
  InlineKeyboardButton(text="Korea", callback_data="q1_Korea"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q1_country_builder.adjust(3,1)
q1_country = q1_country_builder.as_markup()

q2_marc_builder = InlineKeyboardBuilder()
marc_list = xl.car_menu.get_marc()
if len(marc_list) > 12:
    marc_list = marc_list[:12]
for m in marc_list:
    q2_marc_builder.add(InlineKeyboardButton(text=m, callback_data=f"q2_{m}"))
q2_marc_builder.add(InlineKeyboardButton(text="✏️ Свой вариант", callback_data="Свой вариант"))
q2_marc_builder.add(InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear"))
q2_marc_builder.adjust(3, 3, 3, 3, 1, 1)
q2_marc = q2_marc_builder.as_markup()

def q3_model_dinamic(marc):
  # динамическое создание кнопок для моделей в зависимости от выбранной марки
  q3_model_dinamic_builder = InlineKeyboardBuilder() 
  models_list = xl.car_menu.get_models(marc)
  if len(models_list) > 9:
    models_list = models_list[:9]
  for m in models_list:
    q3_model_dinamic_builder.add(InlineKeyboardButton(text=m, callback_data=f"q3_{m}"))
  q3_model_dinamic_builder.add(
    InlineKeyboardButton(text="✏️ Свой вариант", callback_data="Свой вариант"),
    InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
  )
  q3_model_dinamic_builder.adjust(3, 3, 3, 1, 1)
  return q3_model_dinamic_builder.as_markup()

q4_type_kpp_builder = InlineKeyboardBuilder()
q4_type_kpp_builder.add(
  InlineKeyboardButton(text="Механика", callback_data="q4_механика"),
  InlineKeyboardButton(text="Автомат", callback_data="q4_автомат"),
  InlineKeyboardButton(text="Робот", callback_data="q4_робот"),
  InlineKeyboardButton(text="Вариатор", callback_data="q4_вариатор"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q4_type_kpp_builder.adjust(2, 2, 1)
q4_type_kpp = q4_type_kpp_builder.as_markup()

#на 5-6 вопрос пользователь отвечает вручную

q7_dop_or_done = InlineKeyboardMarkup(
  inline_keyboard=[
    [InlineKeyboardButton(text="Отправить заявку", callback_data="Done")],
    [InlineKeyboardButton(text="Дополнительные пожелания", callback_data="q7_Дальше")]]
)

q8_wheel_type_builder = InlineKeyboardBuilder()
q8_wheel_type_builder.add(
  InlineKeyboardButton(text="Левый", callback_data="q8_левый"),
  InlineKeyboardButton(text="Правый", callback_data="q8_правый"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q8_wheel_type_builder.adjust(2, 1)
q8_wheel_type = q8_wheel_type_builder.as_markup()

q9_body_type_builder = InlineKeyboardBuilder()
q9_body_type_builder.add(

  InlineKeyboardButton(text="Седан", callback_data="q9_Седан"),
  InlineKeyboardButton(text="Пикап", callback_data="q9_Пикап"),
  InlineKeyboardButton(text="Купе", callback_data="q9_Купе"),
  
  InlineKeyboardButton(text="Универсал", callback_data="q9_Универсал"),
  InlineKeyboardButton(text="Минивэн", callback_data="q9_Минивэн"),
  
  InlineKeyboardButton(text="Хетчбэк", callback_data="q9_Хетчбэк"),
  InlineKeyboardButton(text="Кроссовер", callback_data="q9_Кроссовер"),

  InlineKeyboardButton(text="✏️ Свой вариант", callback_data="Свой вариант"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q9_body_type_builder.adjust(3, 2, 2, 1, 1)
q9_body_type = q9_body_type_builder.as_markup()


q10_year_builder = InlineKeyboardBuilder()
q10_year_builder.add(
  InlineKeyboardButton(text="До 3 лет (2024-2026)", callback_data="q10_2024-2026"),
  InlineKeyboardButton(text="3-5 лет (2021-2024)", callback_data="q10_2021-2024"),
  InlineKeyboardButton(text="Выше 3 лет (2010-2021)", callback_data="q10_2010-2021)"),
  InlineKeyboardButton(text="✏️ Свой вариант", callback_data="Свой вариант"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q10_year_builder.adjust(1, 1, 1, 1, 1)
q10_year = q10_year_builder.as_markup()



q11_fuel_builder = InlineKeyboardBuilder()
q11_fuel_builder.add(
  InlineKeyboardButton(text="Бензин", callback_data="q11_бензин"),
  InlineKeyboardButton(text="Дизель", callback_data="q11_дизель"),
  InlineKeyboardButton(text="Гибрид", callback_data="q11_гибрид"),
  InlineKeyboardButton(text="Электро", callback_data="q11_электро"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q11_fuel_builder.adjust(2, 2, 1)
q11_fuel = q11_fuel_builder.as_markup()


q12_engine_builder = InlineKeyboardBuilder()
q12_engine_builder.add(
  InlineKeyboardButton(text="0.7", callback_data="q12_0.7"),
  InlineKeyboardButton(text="1.0", callback_data="q12_1.0"),
  InlineKeyboardButton(text="1.2", callback_data="q12_1.2"),
  InlineKeyboardButton(text="1.5", callback_data="q12_1.5"),
  InlineKeyboardButton(text="1.6", callback_data="q12_1.6"),
  InlineKeyboardButton(text="1.8", callback_data="q12_1.8"),
  InlineKeyboardButton(text="2.0", callback_data="q12_2.0"),
  InlineKeyboardButton(text="2.2", callback_data="q12_2.2"),
  InlineKeyboardButton(text="2.5", callback_data="q12_2.5"), 
  InlineKeyboardButton(text="3.0", callback_data="q12_3.0"),
  InlineKeyboardButton(text="3.5", callback_data="q12_3.5"),
  InlineKeyboardButton(text="Пропустить", callback_data="q12_Пропущено"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear"))
q12_engine_builder.adjust(4, 5, 3, 1)
q12_engine = q12_engine_builder.as_markup()




q13_mileage_builder = InlineKeyboardBuilder()
q13_mileage_builder.add(
  InlineKeyboardButton(text="До 50 000 км", callback_data="q13_50т км"),
  InlineKeyboardButton(text="До 100 000 км", callback_data="q13_100т км"),
  InlineKeyboardButton(text="До 150 000 км", callback_data="q13_150т км"),
  InlineKeyboardButton(text="Выше 150 000 км", callback_data="q13_выше 150т км"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q13_mileage_builder.adjust(1, 1, 1, 1, 1)
q13_mileage = q13_mileage_builder.as_markup()

q14_drive_type_builder = InlineKeyboardBuilder()
q14_drive_type_builder.add(
  InlineKeyboardButton(text="Передний", callback_data="q14_передний"),
  InlineKeyboardButton(text="Задний", callback_data="q14_задний"),
  InlineKeyboardButton(text="Полный", callback_data="q14_полный"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q14_drive_type_builder.adjust(3, 1)
q14_drive_type = q14_drive_type_builder.as_markup()

q15_color_builder = InlineKeyboardBuilder()
q15_color_builder.add(
  InlineKeyboardButton(text="Черный", callback_data="q15_черный"),
  InlineKeyboardButton(text="Белый", callback_data="q15_белый"),
  InlineKeyboardButton(text="Красный", callback_data="q15_красный"),
  
  InlineKeyboardButton(text="Серебристый", callback_data="q15_серебристый"),
  InlineKeyboardButton(text="Синий", callback_data="q15_синий"),
  
  InlineKeyboardButton(text="Зеленый", callback_data="q15_зеленый"),
  InlineKeyboardButton(text="Коричневый", callback_data="q15_коричневый"),
 
  InlineKeyboardButton(text="✏️ Свой вариант", callback_data="Свой вариант"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q15_color_builder.adjust(3, 2, 2, 1, 1)
q15_color = q15_color_builder.as_markup()

q16_complete_builder = InlineKeyboardBuilder()
q16_complete_builder.add(
  InlineKeyboardButton(text="Базовая", callback_data="q16_базовая"),
  InlineKeyboardButton(text="Средняя", callback_data="q16_средняя"),
  InlineKeyboardButton(text="Максимальная", callback_data="q16_максимальная"),
  InlineKeyboardButton(text="Спортивная", callback_data="q16_cпортивная"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q16_complete_builder.adjust(2, 2, 1)
q16_complete = q16_complete_builder.as_markup()

q17_contact_builder = InlineKeyboardBuilder()
q17_contact_builder.add(
  InlineKeyboardButton(text="Добавить контакт", callback_data="q16_contact"),
  InlineKeyboardButton(text="Пропустить", callback_data="q16_"),
  InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")
)
q17_contact_builder.adjust(2, 2, 1)
q17_contact = q16_complete_builder.as_markup()

send_request = InlineKeyboardMarkup(
  inline_keyboard=[
    [InlineKeyboardButton(text="Отправить заявку", callback_data="Done")],
    [InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")]]
)

admin_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📋 Последние заявки", callback_data="admin_last_applications")],
        [InlineKeyboardButton(text="📥 Скачать все заявки (CSV)", callback_data="admin_export_csv")],
        [InlineKeyboardButton(text="🔄 Начать сначала", callback_data="clear")]
    ]
)
