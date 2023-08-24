from django.core.management import BaseCommand

from ...models import Tag


class Command(BaseCommand):
    """Создание набора тегов в DB-проекта"""
    def handle(self, *args, **kwargs):
        try:
            tags = (('Завтрак', '#FF6600', 'breakfast'),
                    ('Обед', '#FF0000', 'dinner'),
                    ('Ужин', '#009900', 'supper'))
            for tag in tags:
                name, color, slug = tag
                Tag.objects.get_or_create(
                    name=name,
                    color=color,
                    slug=slug,
                )
            print('Теги добавлены успешно')
        except IOError as err:
            print(f'Ошибка при добавлении тегов: {err}')
