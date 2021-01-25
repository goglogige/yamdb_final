from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from api_yamdb.settings import EMAIL_HOST_USER
from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permissions import IsAdministrator, IsAuthorOrIsStaffPermission, ReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          EmailSerializer, GenreSerializer, ReviewSerializer,
                          TitleListSerializer, TitlePostSerializer,
                          EmailCodeSerializer, UserSerializer)


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def confirm_email(request):
    serializer = EmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    user = User.objects.get_or_create(email=email)[0]
    confirmation_code = PasswordResetTokenGenerator().make_token(user)
    send_mail(
        'Confirmation code',
        f'You confirmation code: {confirmation_code}',
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return Response(
        {'message': f'Your confirmation code sent to {email}'},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    serializer = EmailCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data['email']
    user = User.objects.get(email=email)
    confirmation_code = serializer.data['confirmation_code']
    if not PasswordResetTokenGenerator().check_token(user, confirmation_code):
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
    token = RefreshToken.for_user(user).access_token
    return Response(
        {'token': f'{token}'},
        status=status.HTTP_200_OK
    )


class UsersViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdministrator]
    lookup_field = 'username'

    def get_permissions(self):
        if self.action is 'profile':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=['GET', 'PATCH', 'DELETE']
    )
    def profile(self, request):
        if request.method == 'GET':
            user = request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PATCH':
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryListCreate(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated & IsAdminUser | ReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']


class CategoryDestroy(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = 'slug'


class GenreListCreate(generics.ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated & IsAdminUser | ReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name']


class GenreDestroy(generics.DestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = [IsAuthenticated & IsAdminUser | ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleListSerializer
        return TitlePostSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrIsStaffPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user,
            title=title
        )

    def partial_update(self, request, *args, **kwargs):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        get_object_or_404(
            title.reviews,
            pk=self.kwargs.get('pk'),
            title=title
        )
        return super().partial_update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrIsStaffPermission]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        review = get_object_or_404(
            title.reviews,
            pk=self.kwargs.get('review_id'),
            title=title
        )
        serializer.save(
            author=self.request.user,
            review=review
        )

    def partial_update(self, request, *args, **kwargs):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        review = get_object_or_404(
            title.reviews,
            pk=self.kwargs.get('review_id'),
            title=title
        )
        get_object_or_404(
            review.comments,
            pk=self.kwargs.get('pk'),
            review=review
        )
        return super().partial_update(request, *args, **kwargs)
