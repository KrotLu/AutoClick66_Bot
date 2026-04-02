from pandas import read_excel, DataFrame

excel_data = read_excel('Bd_marc_model.xlsx')
data = DataFrame(excel_data)
data_str= data.astype(str)

marc = data_str.iloc[0:,1:2]
model = data_str.iloc[0:,3:4]



class CarMenu:
    def __init__(self, file_path):
        # Читаем файл
        self.df = read_excel(file_path)

        # Фильтруем строки с "+"
        self.filtered_df = self.df[self.df['Популярное'] == '+']

        # Получаем уникальные марки
        self.marc = self.filtered_df['Марка'].unique().tolist()

        # Получаем словарь марка -> [модели]
        self.models_by_marc = self.filtered_df.groupby('Марка')['Модель'].apply(list).to_dict()

    def get_marc(self):
        """Возвращает список марок с +"""
        return self.marc

    def get_models(self, marc):
        """Возвращает список моделей для конкретной марки (только с +)"""
        return self.models_by_marc.get(marc, [])

    def show_all(self):
        """Выводит всю информацию"""
        for marc in self.marc:
            models = self.get_models(marc)
            print(f"{marc}: {', '.join(models)}")

# Использование
car_menu = CarMenu('Bd_marc_model.xlsx')

# Получить все марки
#marc = car_menu.get_marc()
#print(f"Марки: {marc}")
#print(type(marc[0]))

# Получить модели для конкретной марки
#renault_models = car_menu.get_models(marc[0])
#print(f"Модели {marc[0]}: {renault_models}")
#print(type(renault_models[0]))

# Показать всё
