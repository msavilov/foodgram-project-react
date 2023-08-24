from django.conf import settings
from django.contrib import admin
from django.contrib.admin import register

from users.models import Subscribe, User


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


@register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'author',
                    'user',
                    'created',)
    search_fields = ('user',
                     'author',)
    list_per_page = settings.ITEM_PER_PAGE_ADMIN
    save_on_top = True
