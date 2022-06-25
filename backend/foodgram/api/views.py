import re

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework_csv.renderers import CSVRenderer

from .mixins import ListViewSet
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    CartSerializer, FavoriteSerializer, FollowSerializer,
    FollowUserSerializer, IngredientSerializer,
    RecipeSerializer, ShortRecipeSerializer,
    TagSerializer
)
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
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)
        return queryset


@api_view(['POST', 'DELETE'])
def follow_view(request, pk):
    if request.method == 'POST':
        serializer = FollowSerializer(
            data={'user': request.user.id, 'author': pk}
        )
        if serializer.is_valid():
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
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    following_user = get_object_or_404(User, id=pk)
    follow = Follow.objects.filter(
        user=request.user,
        author=following_user
    )
    if not follow:
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
        if re.compile(
            r"^(\w|\W)+favorite/$"
        ).match(request.stream.path):
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': pk})
        elif re.compile(
            r"^(\w|\W)+shopping_cart/$"
        ).match(request.stream.path):
            serializer = CartSerializer(
                data={'user': request.user.id, 'recipe': pk}
            )
        if serializer.is_valid():
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
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    recipe = get_object_or_404(Recipe, id=pk)
    if re.compile(
        r"^(\w|\W)+favorite/$"
    ).match(request.stream.path):
        existsObject = RecipeFavorites.objects.filter(
            user=request.user,
            recipe=recipe
        )
        mask = 'избранном'
    elif re.compile(
        r"^(\w|\W)+shopping_cart/$"
    ).match(request.stream.path):
        existsObject = RecipeCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        mask = 'корзине'
    if not existsObject:
        return Response(
            {'errors': f'Рецепт отсутствует в {mask}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    existsObject.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class CartRender(CSVRenderer):
    header = ['name', 'sum', 'measurement_unit']


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
    content = [{'name': ingredient['name'],
                'sum': ingredient['all_amt'],
                'measurement_unit': ingredient['measurement_unit']}
               for ingredient in ingredients]
    return Response(content)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        if not self.request.user.is_authenticated and (
            is_favorited == '1'
            or is_in_shopping_cart == '1'
        ):
            return Recipe.objects.none()
        if self.request.user.is_authenticated:
            if is_favorited == '1':
                filter_ids = self.request.user.recipes_in_fav.values_list(
                    'id'
                )
                queryset = queryset.filter(id__in=filter_ids)
            if is_favorited == '0':
                filter_ids = self.request.user.recipes_in_fav.values_list(
                    'id'
                )
                queryset = queryset.exclude(id__in=filter_ids)
            if is_in_shopping_cart == '1':
                filter_ids = self.request.user.recipes_in_cart.values_list(
                    'id'
                )
                queryset = queryset.filter(id__in=filter_ids)
            if is_in_shopping_cart == '0':
                filter_ids = self.request.user.recipes_in_cart.values_list(
                    'id'
                )
                queryset = queryset.exclude(id__in=filter_ids)
        if author:
            author = User.objects.get(pk=int(author))
            if not author:
                return Recipe.objects.none()
            queryset = queryset.filter(author=author)
        if tags:
            for tag_slug in tags:
                try:
                    tag_id = Tag.objects.values_list(
                        'id',
                        flat=True
                    ).get(
                        slug=tag_slug
                    )
                except Exception:
                    return Recipe.objects.none()
                for recipe in queryset:
                    if not recipe.tags.filter(pk=tag_id).exists():
                        queryset = queryset.exclude(id=recipe.id)
        return queryset
