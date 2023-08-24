from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель Ингредиент"""
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_LEN_RECIPES,
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=settings.MAX_LEN_RECIPES,
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
        max_length=settings.MAX_LEN_RECIPES,
        unique=True,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=settings.LEN_HEX_CODE,
        unique=True,
    )
    slug = models.SlugField(
        'Slug',
        max_length=settings.MAX_LEN_RECIPES,
        unique=True,
        validators=[validators.RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Введено некорректное значение поля name')],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепт"""
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LEN_RECIPES,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    image = models.ImageField('Фото блюда',)
    text = models.TextField('Описание рецепта',)
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[validators.MinValueValidator(
            settings.MIN_COOKING_TIME,
            message=(f'Минимальное время приготовления: '
                     f'{settings.MIN_COOKING_TIME} минута!')),
                    ]
    )
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.username}, {self.name}'


class IngredientInRecipe(models.Model):
    """Модель количества ингридиентов в рецепте"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredients = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='amount_ingredient',
    )
    amount = models.PositiveIntegerField(
        default=settings.MIN_INGREDIENT_AMOUNT,
        validators=[
            validators.MinValueValidator(
                settings.MIN_INGREDIENT_AMOUNT,
                message=(f'Минимальное количество ингредиентов'
                         f'`{settings.MIN_INGREDIENT_AMOUNT}` !')
            ),
        ],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredients'],
                name='unique_recipe_and_ingredient'),
        ]

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'


class Favorite(models.Model):
    """Модель списка избранного"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='favorite')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='favorite')
    constraints = (models.UniqueConstraint(
        fields=['recipe', 'user'],
        name='unique_favorite_user'))

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-id',)

    def __str__(self):
        return (f'Пользователь {self.user.username} '
                f'добавил {self.recipe.name} в избранное.')


class ShoppingCart(models.Model):
    """Модель списка избранного"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт',
                               related_name='shopping_cart')
    constraints = (models.UniqueConstraint(
        fields=['recipe', 'user'],
        name='unique_shopping_cart_user'))

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-id',)

    def __str__(self):
        return (f'Пользователь {self.user} '
                f'добавил {self.recipe.name} в покупки.')
