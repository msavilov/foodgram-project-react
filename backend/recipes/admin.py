from django.contrib import admin

from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag,
)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


class IngredientInRecipeAdmin(admin.StackedInline):
    model = IngredientInRecipe
    autocomplete_fields = ('ingredients',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeAdmin,)
    list_display = ('name', 'author', 'get_favorite_count')
    search_fields = ('author__username', 'name', 'tags__name')
    list_filter = ('pub_date', 'tags')
    save_on_top = True

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
            f'{item["ingredients__name"]} - {item["amount"]}'
            f' {item["ingredients__measurement_unit"]}.'
            for item in obj.recipes.values(
                'ingredients__name',
                'amount', 'ingredients__measurement_unit')])

    @admin.display(description='В избранном')
    def get_favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoppingCarsAdmin(admin.ModelAdmin):
    ordering = ('user',)
    search_fields = ('recipe', 'user')
