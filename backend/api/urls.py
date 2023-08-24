from rest_framework import routers
from django.urls import path, include

from api.views import (
    IngredientsViewSet,
    RecipesViewSet,
    SetPasswordView,
    TagsViewSet,
    UserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('tags', TagsViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('users/set_password/', SetPasswordView, name='set_password'),
    path('auth/', include('djoser.urls.authtoken'), name='auth'),
]
