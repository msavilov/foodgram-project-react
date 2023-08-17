import csv

from django.core.management.base import BaseCommand

from ...models import Ingredient


class Command(BaseCommand):
    """Выгрузка первоначальных данных в DB-проекта"""
    def handle(self, *args, **options):
        try:
            with open('./data/ingredients.csv', encoding='utf-8') as file:
                file_reader = csv.reader(file)
                for row in file_reader:
                    name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit)
            print('Импорт данных произведён успешно')
        except IOError as err:
            print(f'Ошибка импорта: {err}')
