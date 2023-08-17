from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from ..core import constants


class User(AbstractUser):
    """Модель для пользователя."""

    class Roles(models.TextChoices):
        """Класс для роли пользователя."""
        USER = 'user'
        ADMIN = 'admin'

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=constants.MAX_LEN_USER_FIELD,
        unique=True,
        validators=RegexValidator(
            regex=r'^[\w.@+-]+\z',
            message='Введено некорректное значение поля username'),
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=constants.MAX_LEN_EMAIL,
        db_index=True,
        unique=True,
        help_text='Введите адрес электронной почты',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=constants.MAX_LEN_USER_FIELD,
        help_text='Введите своё имя.',
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=constants.MAX_LEN_USER_FIELD,
        help_text='Введите свою фамилию.',
    )
    password = models.CharField(
        'Пароль',
        max_length=constants.MAX_LEN_USER_FIELD,
        help_text='Введите пароль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def is_admin(self):
        return (self.is_staff or self.is_superuser
                or self.role == User.Roles.ADMIN)

    @property
    def is_user(self):
        return self.is_user or self.role == User.Roles.USER

    def __str__(self):
        return f'{self.username}: {self.email}.'


class Follow(models.Model):
    """Модель для подписчика"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ('-id',)
        constraints = models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow',
        )

    def __str__(self):
        return (f'Пользователь {self.user.username}'
                f' подписался на {self.author.username}')
