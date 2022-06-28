from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import resolve
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListViewSet
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    CartSerializer, FavoriteSerializer, FollowSerializer,
    FollowUserSerializer, IngredientSerializer,
    RecipeSerializer, ShortRecipeSerializer,
    TagSerializer
)
from .utils import CartRender
from recipe.models import (
    Follow, Ingredient, Recipe, RecipeCart,
    RecipeFavorites, RecipeIngredient, Tag, User
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAdminOrReadOnly]


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = IngredientFilter


@api_view(['POST', 'DELETE'])
def follow_view(request, pk):
    if request.method == 'POST':
        serializer = FollowSerializer(
            data={'user': request.user.id, 'author': pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        following_user = get_object_or_404(User, id=pk)
        user_serializer = FollowUserSerializer(
            following_user,
            context={'request': request}, many=False
        )
        return Response(
            user_serializer.data,
            status=status.HTTP_201_CREATED
        )
    following_user = get_object_or_404(User, id=pk)
    follow = Follow.objects.filter(
        user=request.user,
        author=following_user
    )
    if not follow.exists():
        return Response(
            {'errors': 'Подписки не существует'},
            status=status.HTTP_400_BAD_REQUEST
        )
    follow.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(ListViewSet):
    serializer_class = FollowUserSerializer

    def get_queryset(self):
        following_users = Follow.objects.filter(
            user=self.request.user
        ).values_list('author')
        return User.objects.filter(id__in=following_users)


@api_view(['POST', 'DELETE'])
def cart_favorite_view(request, pk):
    if request.method == 'POST':
        if resolve(request.path_info).url_name == 'modify_favs':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': pk})
        elif resolve(request.path_info).url_name == 'modify_cart':
            serializer = CartSerializer(
                data={'user': request.user.id, 'recipe': pk}
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipe = get_object_or_404(Recipe, id=pk)
        recipe_serializer = ShortRecipeSerializer(
            recipe,
            context={'request': request},
            many=False
        )
        return Response(
            recipe_serializer.data,
            status=status.HTTP_201_CREATED
        )
    recipe = get_object_or_404(Recipe, id=pk)
    if resolve(request.path_info).url_name == 'modify_favs':
        removing_object = RecipeFavorites.objects.filter(
            user=request.user,
            recipe=recipe
        )
        mask = 'избранном'
    elif resolve(request.path_info).url_name == 'modify_cart':
        removing_object = RecipeCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        mask = 'корзине'
    if not removing_object.exists():
        return Response(
            {'errors': f'Рецепт отсутствует в {mask}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    removing_object.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@renderer_classes([CartRender])
def download_cart(request):
    recipes_in_cart = RecipeCart.objects.filter(
        user=request.user
    ).values_list('recipe')
    ingredients = RecipeIngredient.objects.filter(
        recipe__in=recipes_in_cart
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        name=F('ingredient__name'),
        measurement_unit=F('ingredient__measurement_unit'),
        all_amt=Sum('amount')
    )
    content = [{
        'name': ingredient['name'],
        'sum': ingredient['all_amt'],
        'measurement_unit': ingredient['measurement_unit']
    } for ingredient in ingredients]
    response = HttpResponse(
        request.accepted_renderer.render(content),
        content_type="text/csv"
    )
    response['Content-Disposition'] = 'attachment; filename="cart.csv"'
    return response


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrReadOnly]
    filterset_class = RecipeFilter
