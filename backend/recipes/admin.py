import models
from django.contrib import admin


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)


class IngredientInRecipeAdmin(admin.StackedInline):
    model = models.IngredientInRecipe
    autocomplete_fields = ('ingredient',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeAdmin,)
    list_display = ('name', 'author__username', 'get_favorite_count')
    search_fields = ('author__username', 'name', 'tags')
    list_filter = ('pub_date', 'tags')

    @admin.display(
        description='Электронная почта автора'
    )
    def get_author(self, obj):
        return obj.author.email

    @admin.display(description='Тэги')
    def get_tags(self, obj):
        return ', '.join(str(tag) for tag in obj.tags.all())

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return '\n '.join([
            f'{item["ingredient__name"]} - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredient__name',
                'amount', 'ingredient__measurement_unit')])

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')


@admin.register(models.ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')
