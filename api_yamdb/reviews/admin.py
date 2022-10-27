from django.contrib import admin

from .models import Review, Comments, User, Category, Genre, Title


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'bio',
        'role',
        'email',
    )
    fields = ('username',
              'email',
              'first_name',
              'last_name',
              'bio',
              'role',
              )
    empty_value_display = '-пусто-'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'score',
        'author',
        'pub_date',
    )
    fields = ('text',
              'score',
              'author',
              'pub_date',
              )
    empty_value_display = '-пусто-'


@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'review',
        'author',
    )
    fields = ('text',
              'pub_date',
              'review',
              'author',
              )
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    fields = ('name',
              'slug',
              )
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
    )
    fields = ('name',
              'slug',
              )
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'year',
        'description',
    )
    empty_value_display = '-пусто-'
