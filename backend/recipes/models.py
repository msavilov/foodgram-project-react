from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from ..core import constants

User = get_user_model()


class Ingredient(models.Model):
    """Модель Ингредиент"""
    name = models.CharField(
        'Название ингредиента',
        max_length=constants.MAX_LEN_RECIPES,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=constants.MAX_LEN_RECIPES,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Tag(models.Model):
    """Модель Тег"""
    name = models.CharField(
        'Название',
        max_length=constants.MAX_LEN_RECIPES,
        unique=True,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=constants.LEN_HEX_CODE,
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        max_length=constants.MAX_LEN_RECIPES,
        unique=True,
        validators=validators.RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Введено некорректное значение поля name'),
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепт"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
    )
    image = models.ImageField(
        'Ссылка на картинку на сайте',
        upload_to='static/recipe/',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=constants.MAX_LEN_RECIPES,
    )
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[validators.MinValueValidator(
            constants.MIN_COOKING_TIME,
            message=(f'Минимальное время приготовления: '
                     f'{constants.MIN_COOKING_TIME} минута!')),
                    ]
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.name}, {self.name}'


class IngredientInRecipe(models.Model):
    """Модель количества ингридиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField(
        default=constants.MIN_INGREDIENT_AMOUNT,
        validators=(
            validators.MinValueValidator(
                constants.MIN_INGREDIENT_AMOUNT,
                message=(f'Минимальное количество ингредиентов'
                         f'`{constants.MIN_INGREDIENT_AMOUNT}` !')
            ),
        ),
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_and_ingredient'),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'


class RecipeUser(models.Model):
    """Абстрактный класс для Favorite и ShoppingList"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        abstract = True
        ordering = ('recipe', 'user')


class Favorite(RecipeUser):
    """Модель Избранное"""
    class Meta(RecipeUser.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = models.UniqueConstraint(
            fields=['recipe', 'user'],
            name='unique_favorite_user',
        )

    def __str__(self):
        return (f'Пользователь {self.user.username} '
                f'добавил {self.recipe} в избранное.')


class ShoppingList(RecipeUser):
    """Модель Список покупок"""
    class Meta(RecipeUser.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_list_user'
            ),
        )

    def __str__(self):
        return (f'Пользователь {self.user} '
                f'добавил {self.recipe.name} в покупки.')
