from django.conf import settings
from django.contrib.auth import (
    authenticate,
    get_user_model,
    password_validation)
from django.contrib.auth.hashers import make_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, validators
from rest_framework.generics import get_object_or_404

from api.services import Base64ImageField
from recipes.models import (Ingredient, IngredientInRecipe, Favorite,
                              Recipe, ShoppingList, Tag)
from users.models import Follow

User = get_user_model()


class CreateUserSerializer(UserCreateSerializer):
    """Сериализатор регистрации пользователей"""
    username = serializers.CharField(validators=[validators.UniqueValidator(
        queryset=User.objects.all())])
    email = serializers.EmailField(validators=[validators.UniqueValidator(
        queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('id', 'username', 'password',
                  'first_name', 'last_name', 'email')
        extra_kwargs = {'password': {'write_only': True}}


class UsersSerializer(UserSerializer):
    """Сериализатор данных о пользователе"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """ Проверка подписки"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=obj.id).exists()
        return False


class UserPasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля"""
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                'Неверный логин или пароль пользователя',
                code='authorization')
        return current_password

    @staticmethod
    def validate_new_password(new_password):
        password_validation.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для Tag"""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для Ingredient"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для IngredientInRecipe"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            validators.UniqueTogetherValidator(
                queryset=IngredientInRecipe.objects.all(),
                fields=('ingredient', 'recipe'),
            )
        ]


class FavoriteOrSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного или подписок"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FollowerSerializer(serializers.ModelSerializer):
    """Сериализатор для подписчика"""
    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('id', 'username', 'first_name', 'last_name', 'email'
                  'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('is_subscribed', 'recipes_count',)

    def validate(self, data):
        """ Проверка данных"""
        user_id = data['user_id']
        author_id = data['author_id']
        if user_id == author_id:
            raise serializers.ValidationError({
                'errors': 'Нельзя подписаться на самого себя'
            })
        if Follow.objects.filter(user=user_id,
                                 author=author_id).exists():
            raise serializers.ValidationError({
                'errors': 'Подписка уже существует'
            })
        data['user'] = get_object_or_404(User, id=user_id)
        data['author'] = get_object_or_404(User, id=author_id)
        return data

    @staticmethod
    def get_is_subscribed(obj):
        """ Проверка подписки"""
        return Follow.objects.filter(
            user=obj.user, author=obj.author).exists()

    def get_recipes(self, obj):
        """Получение рецептов автора"""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = FavoriteOrSubscribeSerializer(recipes, many=True)
        return serializer.data

    @staticmethod
    def get_recipes_count(obj):
        """Подсчет рецептов автора. """
        return Recipe.objects.filter(author=obj.author).count()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор Recipe"""
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True
    )
    cooking_time = serializers.IntegerField()
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'tags', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    @staticmethod
    def create_ingredients(recipe, ingredients):
        """ Создание ингредиентов в промежуточной таблице"""
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(recipe=recipe,
             ingredient_id=ingredient.get('id'),
             amount=ingredient.get('amount'))
             for ingredient in ingredients])

    def create(self, validated_data):
        """ Создание рецепта"""
        image = validated_data.pop('image')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """ Обновление рецепта. """
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self.create_ingredients(
            recipe=instance,
            ingredients=validated_data.pop('ingredients')
        )
        super().update(instance, validated_data)
        return instance

    def to_internal_value(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        data = super().to_internal_value(data)
        data['tags'] = tags
        data['ingredients'] = ingredients
        return data

    def get_is_favorited(self, obj):
        """Проверка рецепта в списке избранного"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка рецепта в корзине покупок"""
        user = self.context.get('request').user
        if not user or user.is_anonymous:
            return False
        return ShoppingList.objects.filter(recipe=obj,
                                           user=user).exists()

    def validate(self, data):
        """Валидация различных данных на уровне сериализатора"""
        ingredients = data.get('ingredients')
        errors = []
        if not ingredients:
            errors.append('Добавьте минимум один ингредиент для рецепта.')
        added_ingredients = []
        for ingredient in ingredients:
            if int(ingredient['amount']) < settings.MIN_INGREDIENT_AMOUNT:
                errors.append(
                    f'Количество ингредиента с id {ingredient["id"]} должно '
                    f'быть целым и не меньше '
                    f'{settings.MIN_INGREDIENT_AMOUNT}.'
                )
            if ingredient['id'] in added_ingredients:
                errors.append(
                    'Дважды один тот же ингредиент в рецепт поместить нельзя.'
                )
            added_ingredients.append(ingredient['id'])
        tags = data.get('tags')
        if len(tags) > len(set(tags)):
            errors.append('Один и тот же тэг нельзя применять дважды.')
        cooking_time = float(data.get('cooking_time'))
        if cooking_time < settings.MIN_COOKING_TIME:
            errors.append(f'Минимальное время приготовления: '
                          f'{settings.constants.MIN_COOKING_TIME}')
        if errors:
            raise serializers.ValidationError({'errors': errors})
        data['ingredients'] = ingredients
        data['tags'] = tags
        return data
