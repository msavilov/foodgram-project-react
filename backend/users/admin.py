from django.conf import settings
from django.contrib import admin
from django.contrib.admin import register

from .models import Follow, User


@register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'first_name',
                    'last_name',
                    'email',
                    'password')
    search_fields = ('username',
                     'first_name',
                     'last_name',
                     'email',)
    list_filter = ('username',
                   'email',)
    save_on_top = True


@register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'user',
                    'created',)
    search_fields = ('user',
                     'author',)
    list_per_page = settings.ITEM_PER_PAGE_ADMIN
    save_on_top = True
