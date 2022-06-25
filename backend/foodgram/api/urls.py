from django.urls import include, path
from rest_framework import routers

from .views import (
    FollowViewSet, IngredientViewSet, RecipeViewSet,
    TagViewSet, cart_favorite_view, download_cart,
    follow_view
)


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(
    r'users/subscriptions',
    FollowViewSet,
    basename='subscriptions'
)
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/<int:pk>/subscribe/', follow_view, name='modify_subs'),
    path('recipes/<int:pk>/favorite/', cart_favorite_view, name='modify_favs'),
    path(
        'recipes/<int:pk>/shopping_cart/',
        cart_favorite_view,
        name='modify_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        download_cart,
        name='download_cart'
    ),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
