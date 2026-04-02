from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

"""
1. Марка, модель (хетчбэк/седан):
2. Год выпуска (от и до):
3. Двигатель (объем и тип топлива):
4. Тип КПП:
5. Пробег, км (от и до):
6. Привод (передний, задний, полный):
7. Цвет, комплектация и дополнительные пожелания:
8. Бюджет, в который планируете уложиться:
9. Когда планируете покупку?
"""


# Пример для класса States в aiogram
class CarSelection(StatesGroup):
    # Словарь с State и названиями на русском языке
    purpose = State()
    marc_or_country = State()  # 0. выбор по марке или по стране
    country = State()  # 1.0 Страна из которой привезут автомобиль
    marc = State()  # 2 Марка
    model = State()  # 3.модель
    type_kpp = State()  # 4. Тип КПП
    budget = State()  # 5. Бюджет
    timing = State()  # 6. Когда планируете покупку?
    contact = State()  # 7. Отправить заявку\Дополнительные пожелания

    wheel_type = State()  # 8. Руль (левый, правый)
    body_type = State()  # 9. Тип кузова
    year = State()  # 10. Год выпуска (от и до)
    fuel = State()  # 11. Топливо (тип топлива)
    engine = State()  # 12. Объем двигателя
    mileage = State()  # 13. Пробег, км (от и до)
    drive_type = State()  # 14. Привод (передний, задний, полный)
    color = State()  # 15. Цвет
    complete = State()  # 16.комплектация
    dop = State()  # 17 коммениарий


state_names = {
    CarSelection.purpose: "Цель обращения",
    CarSelection.country: "Страна",
    CarSelection.marc: "Марка",
    CarSelection.model: "Модель",
    CarSelection.type_kpp: "Тип КПП",
    CarSelection.budget: "Бюджет",
    CarSelection.timing: "Когда планируете покупку",
    CarSelection.contact: "Контакт",
    CarSelection.wheel_type: "Руль",
    CarSelection.body_type: "Тип кузова",
    CarSelection.year: "Год выпуска",
    CarSelection.fuel: "Топливо",
    CarSelection.engine: "Объем двигателя",
    CarSelection.mileage: "Пробег",
    CarSelection.drive_type: "Привод",
    CarSelection.color: "Цвет",
    CarSelection.complete: "Комплектация",
    CarSelection.dop: "Дополнительные пожелания",
}
