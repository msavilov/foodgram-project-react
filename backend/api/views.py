from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (IngredientInRecipe, Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import IngredientSearchFilter, RecipesFilter
from api.pagination import LimitPagePagination
from api.permissions import AdminOrAuthor, AdminOrReadOnly
from api.serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeForFollowersSerializer,
                          RecipeSerializer, TagSerializer, UserPasswordSerializer, 
                          UsersSerializer)

from users.models import Subscribe, User

class UsersViewSet(UserViewSet):
    """Вьюсет для модели пользователей."""
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny, )

    def subscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        if self.request.user == follower:
            return Response({'message': 'Нельзя подписаться на себя'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow = Subscribe.objects.get_or_create(user=self.request.user,
                                              author=follower)
        serializer = FollowSerializer(follow[0])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, serializer, id=None):
        follower = get_object_or_404(User, id=id)
        Subscribe.objects.filter(user=self.request.user,
                              author=follower).delete()
        return Response({'message': 'Вы успешно отписаны'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, serializer, id):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serializer, id)
        return self.subscribed(serializer, id)

    @action(detail=False, methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, serializer):
        following = Subscribe.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(following)
        serializer = FollowSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели тэгов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = (AdminOrAuthor,)
    pagination_class = LimitPagePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'retrieve':
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            Favorite.objects.create(user=request.user,
                                    recipe=recipe)
            serializer = RecipeForFollowersSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(Favorite,
                                    user=request.user,
                                    recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт успешно удален из избранного'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            ShoppingCart.objects.create(user=request.user,
                                        recipe=recipe)
            serializer = RecipeForFollowersSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(ShoppingCart,
                                    user=request.user,
                                    recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт успешно удален из списка покупок'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=user).values(
                'ingredients__name',
                'ingredients__measurement_unit').annotate(
                    amount=Sum('amount'))
        data = ingredients.values_list('ingredients__name',
                                       'ingredients__measurement_unit',
                                       'amount')
        shopping_cart = 'Список покупок:\n'
        for name, measure, amount in data:
            shopping_cart += (f'{name.capitalize()} {amount} {measure},\n')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = (
            f'attachment; filename={0}'.format(filename)
            )
        return response


class SetPasswordView(APIView):
    def post(self, request):
        """Изменить пароль."""
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
