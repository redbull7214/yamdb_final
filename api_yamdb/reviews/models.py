from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb import settings
from .validators import validate_year, validate_score


class User(AbstractUser):
    """
    Переопределение стандартной модели User для
    добавления необходимых полей.
    """

    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ACCESS_RIGHTS_CHOICES = [
        (USER, USER),
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR)
    ]

    username = models.CharField(
        max_length=settings.USERS_USERNAME_MAX_LENGTH,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=settings.USERS_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.TextField(
        max_length=settings.USERS_FIRST_NAME_MAX_LENGTH,
        verbose_name='Имя',
        blank=True,
    )
    last_name = models.TextField(
        max_length=settings.USERS_LAST_NAME_MAX_LENGTH,
        verbose_name='Фамилия',
        blank=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        choices=ACCESS_RIGHTS_CHOICES,
        default=USER,
        verbose_name='Права доступа',
        max_length=max([len(x) for x, _ in ACCESS_RIGHTS_CHOICES]),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name()

    @property
    def access_moderator(self):
        return self.role == self.MODERATOR

    @property
    def access_administrator(self):
        return (
            self.role == self.ADMIN
            or self.is_staff
            or self.is_superuser
        )


class Classification(models.Model):
    """Абстрактная модель классификации произведений"""

    name = models.CharField(
        max_length=settings.CLASSIFICATION_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.CLASSIFICATION_SLUG_MAX_LENGTH,
        verbose_name='Идентификатор'
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(Classification):
    """Модель категории."""

    class Meta(Classification.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(Classification):
    """Модель жанра"""

    class Meta(Classification.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения"""

    name = models.CharField(
        max_length=settings.TITLE_NAME_MAX_LENGTH,
        verbose_name='Название',
    )
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        db_index=True,
        verbose_name='Год издания',
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genre',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class Feedback(models.Model):
    """Абстрактная модель обратной связи от пользователей"""

    text = models.CharField(
        max_length=settings.FEEDBACK_TEXT_MAX_LENGTH,
        verbose_name='Текст',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)


class Review(Feedback):
    """Модель отзыва на произведение"""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Отзыв на произведение',
    )
    score = models.PositiveSmallIntegerField(
        validators=[validate_score],
        default=1,
        verbose_name='Оценка',
    )

    class Meta(Feedback.Meta):
        default_related_name = 'review'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='One review of title from same author'
            )
        ]


class Comments(Feedback):
    """Модель комментария к отзыву"""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментарий к отзыву',
    )

    class Meta(Feedback.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
