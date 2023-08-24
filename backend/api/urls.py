from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet, SetPasswordView,
                       TagViewSet, UsersViewSet)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UsersViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('users/set_password/', SetPasswordView, name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
