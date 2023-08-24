from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet


from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPagePagination
from api.permissions import AdminOrReadOnly, AuthorOrReadOnly
from api.serializers import (
    IngredientSerializer,
    FavoriteOrSubscribeSerializer,
    RecipeSerializer,
    FollowerSerializer,
    TagSerializer,
    UserSerializer,
    UserPasswordSerializer
)
from api.services import collect_shopping_cart
from recipes.models import Favorite, Ingredient, Recipe, ShoppingList, Tag
from users.models import Follow

User = get_user_model()


class UserViewSet(DjoserUserViewSet):
    """Пользователи и подписки"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    @action(methods=['POST', 'DELETE'], detail=True,)
    def subscribe(self, request, user_id):
        """Активация/деактивация подписки"""
        author = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValueError('Нельзя подписаться на себя самого')
            serializer = FollowerSerializer(
                Follow.objects.create(user=request.user, author=author),
                context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if Follow.objects.filter(user=request.user,
                                     author=author).exists():
                Follow.objects.filter(user=request.user,
                                      author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Подписка уже существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Список подписок пользователя"""
        serializer = FollowerSerializer(
            self.paginate_queryset(Follow.objects.filter(user=request.user)),
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class SetPasswordView(APIView):
    @staticmethod
    def post(request):
        """Изменение пароля"""
        serializer = UserPasswordSerializer(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Пароль изменен!'},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'error': 'Введите верные данные!'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RecipesViewSet(viewsets.ModelViewSet):
    """Список рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,)

    @staticmethod
    def new_favorite_or_cart(model, user, user_id):
        recipe = get_object_or_404(Recipe, id=user_id)
        model.objects.create(user=user, recipe=recipe)
        serializer = FavoriteOrSubscribeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def remove_favorite_or_cart(model, user, user_id):
        obj = model.objects.filter(user=user, recipe__id=user_id)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт не найден'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, user_id=None):
        """Добавить/удаление рецепта из избранных"""
        if request.method == 'POST':
            return self.new_favorite_or_cart(Favorite,
                                             request.user, user_id)
        return self.remove_favorite_or_cart(Favorite,
                                            request.user, user_id)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, user_id=None):
        """Добавление/удаление рецепта в список покупок"""
        if request.method == 'POST':
            return self.new_favorite_or_cart(
                ShoppingList, request.user, user_id)
        return self.remove_favorite_or_cart(ShoppingList,
                                            request.user, user_id)

    @action(detail=False, methods=['GET'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивание корзины продуктов"""
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return collect_shopping_cart(request)


class TagsViewSet(ReadOnlyModelViewSet):
    """Список тэгов"""
    queryset = Tag.objects.all()
    permission_classes = (AdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet):
    """Список ингридиентов"""
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None