from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator
from api_yamdb import settings
from reviews.models import Category, Genre, Title, Review, Comments, User
from reviews.validators import validate_score, validate_year, validate_username


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели отзыв."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    score = serializers.IntegerField(
        validators=[validate_score],
    )

    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'POST':
            title_id = self.context.get('view').kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)
            if title.review.filter(author=request.user).exists():
                raise ValidationError('Вы не можете добавить более'
                                      'одного отзыва на произведение')
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comments
        read_only_fields = ('review',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели категория."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели жанры."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitlesSerializer(serializers.ModelSerializer):
    """Сериализатор для модели тайтл. Для получения."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(many=False)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = ('genre', 'category', 'rating',)


class TitleCreateSerializer(TitlesSerializer):
    """Сериализатор для модели тайтл. Для создания."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    year = serializers.IntegerField(
        validators=[validate_year],
    )


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для модели пользователь. Создание пользователя."""

    username = serializers.CharField(
        required=True,
        max_length=settings.USERS_USERNAME_MAX_LENGTH)
    email = serializers.EmailField(
        required=True,
        max_length=settings.USERS_EMAIL_MAX_LENGTH)

    def validate_username(self, value):
        return validate_username(value)


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для модели получение токена."""

    username = serializers.CharField(
        required=True,
        max_length=settings.USERS_USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField()

    def validate_username(self, value):
        return validate_username(value)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователь."""

    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )

    class Meta:
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        model = User


class UpdateUserSerializer(UserSerializer):
    """Сериализатор для обновления модели пользователь."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
        read_only_fields = ('role',)
