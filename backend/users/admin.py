from django.contrib import admin
from django.contrib.admin import register

from ..core import costants
from .models import Follow, User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',)
    search_fields = ('username',
                     'first_name',
                     'last_name',
                     'email',)
    list_filter = ('first_name',
                   'email',)
    save_on_top = True


@register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'user',
                    'created',)
    search_fields = ('user__email',
                     'author__email',)
    list_per_page = costants.PER_PAGE
    save_on_top = True
