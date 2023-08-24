import base64

from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework import serializers

from recipes.models import ShoppingList


class Base64ImageField(serializers.ImageField):
    """Декодировка изображения"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            form, img = data.split(';base64,')
            ext = form.split('/')[-1]
            data = ContentFile(base64.b64decode(img), name='temp.' + ext)
        return super().to_internal_value(data)


def collect_shopping_cart(request):
    """Создание списка покупок"""
    shopping_cart = ShoppingList.objects.filter(user=request.user).all()
    shopping_list = {}
    for item in shopping_cart:
        for recipe_ingredient in item.recipe.recipe_ingredients.all():
            name = recipe_ingredient.ingredient.name
            measuring_unit = recipe_ingredient.ingredient.measurement_unit
            amount = recipe_ingredient.amount
            if name not in shopping_list:
                shopping_list[name] = {
                    'name': name,
                    'measurement_unit': measuring_unit,
                    'amount': amount
                }
            else:
                shopping_list[name]['amount'] += amount
    content = (
        [f'{item["name"]} ({item["measurement_unit"]}) '
         f'- {item["amount"]}\n'
         for item in shopping_list.values()]
    )
    filename = 'shopping_list.txt'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        f'attachment; filename={0}'.format(filename)
    )
    return response
