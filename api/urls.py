from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryDestroy, CategoryListCreate, CommentViewSet,
                    GenreDestroy, GenreListCreate, #GetPatchYourProfile,
                    ReviewViewSet, TitleViewSet, UsersViewSet, confirm_email,
                    registration)


router = DefaultRouter()

router.register(r'users', UsersViewSet, basename='users')
router.register(r'titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='comments'
)

authorization = [
    path('email/', confirm_email),
    path('token/', registration),
]

urlpatterns = [
    path('v1/auth/', include(authorization)),
    path('v1/users/me/', UsersViewSet.as_view(
        actions={
            'get': 'profile',
            'patch': 'profile',
            'delete': 'profile',
        }
    )),
    path('v1/categories/', CategoryListCreate.as_view()),
    path('v1/categories/<str:slug>/', CategoryDestroy.as_view()),
    path('v1/genres/', GenreListCreate.as_view()),
    path('v1/genres/<str:slug>/', GenreDestroy.as_view()),
    path('v1/', include(router.urls)),
]
