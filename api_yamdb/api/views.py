from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters

from .mixin import CustomMixin
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, User
from .filters import TitleFilter
from .permissions import (AuthorOrModeratorOrAdmin,
                          AdminOrReadOnly, IsAdmin)
from .serializers import (CategorySerializer, GenreSerializer,
                          TitlesSerializer, ReviewSerializer,
                          CommentsSerializer, TitleCreateSerializer,
                          UserCreateSerializer, GetTokenSerializer,
                          UserSerializer, UpdateUserSerializer)


class CategoryViewSet(CustomMixin):
    """API для работы категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CustomMixin):
    """API для работы с моделью жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """API для работы произведений."""
    queryset = Title.objects.annotate(
        rating=Avg('review__score')
    )
    permission_classes = (AdminOrReadOnly,)
    filterset_class = TitleFilter
    serializer_class = TitlesSerializer
    ordering_fields = ('name',)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitlesSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """API для работы отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (
        AuthorOrModeratorOrAdmin, IsAuthenticatedOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().review.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentsViewSet(viewsets.ModelViewSet):
    """API для работы комментариев."""

    serializer_class = CommentsSerializer
    permission_classes = (
        AuthorOrModeratorOrAdmin, IsAuthenticatedOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class RegistrationNewUser(APIView):
    """API для работы регистрации пользователей."""

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, create = User.objects.get_or_create(
                username=serializer.validated_data.get('username'),
                email=serializer.validated_data.get('email'))
        except IntegrityError:
            return Response('Email либо username занят, укажите другой.',
                            status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Регистрация на сайте',
            message=f'токен для входа на сайт: {confirmation_code}',
            from_email=None,
            recipient_list=[user.email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetToken(APIView):
    """API для получения токена."""

    permission_classes = (AllowAny,)
    serializer_class = GetTokenSerializer

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data.get('username')
        )

        if default_token_generator.check_token(
                user, serializer.validated_data.get('confirmation_code')
        ):
            token = AccessToken.for_user(user)
            return Response({'token': str(token)}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """API для работы авторизации."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False,
            methods=['get', 'patch'],
            url_path='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UpdateUserSerializer,
            )
    def me(self, request):
        global serializer
        user = self.request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
