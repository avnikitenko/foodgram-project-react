from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipe.models import (
    Follow, Ingredient, Recipe, RecipeCart,
    RecipeFavorites, RecipeIngredient, RecipeTag, Tag,
    User
)


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Follow.objects.filter(
            author=obj.id, user=request_user
        ).exists()
        return queryset


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }

    def validate_email(self, value):
        value_email = value.lower()
        if User.objects.filter(email=value_email).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже зарегистрирован"
            )
        return value_email


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def validate_author(self, value):
        following_user = get_object_or_404(User, username=value)
        user = get_object_or_404(User, id=self.initial_data['user'])
        if user == following_user:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        if Follow.objects.filter(
            user=user,
            author=following_user
        ).exists():
            raise serializers.ValidationError('Такая подписка уже существует')
        return value


class FollowUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Follow.objects.filter(
            author=obj.id, user=request_user
        ).exists()
        return queryset

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            recipes = Recipe.objects.filter(author=obj)[:int(recipes_limit)]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = ShortRecipeSerializer(instance=recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeFavorites
        fields = ['user', 'recipe']

    def validate_recipe(self, value):
        user = get_object_or_404(User, id=self.initial_data['user'])
        if RecipeFavorites.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return value


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeCart
        fields = ['user', 'recipe']

    def validate_recipe(self, value):
        user = get_object_or_404(User, id=self.initial_data['user'])
        if RecipeCart.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return value


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
        read_only=False
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['amount', 'id', 'name', 'measurement_unit']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True, read_only=False
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def to_internal_value(self, data):  # в post-методе теги задаются списком
        tags_id = data.get('tags')
        internal_data = super().to_internal_value(data)
        if tags_id is None:
            raise ValidationError(
                {'tags': ['Определите теги']},
                code='invalid',
            )
        for id in tags_id:
            try:
                Tag.objects.get(pk=id)
            except Tag.DoesNotExist:
                raise ValidationError(
                    {'tags': ['Некорректный идентификатор тега']},
                    code='invalid',
                )
        if len(data.get('tags')) != len(set(data.get('tags'))):
            raise ValidationError(
                {'tags': ['Неуникальные идентификаторы тегов']},
                code='invalid',
            )
        internal_data['tags'] = tags_id
        return internal_data

    class Meta:
        model = Recipe
        fields = [
            'id', 'name', 'image', 'text', 'cooking_time', 'tags',
            'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart'
        ]
        read_only_fields = ['id']

    def validate_ingredients(self, value):
        ingredients = []
        for i in value:
            ingredient = i.get('ingredient')
            if ingredient in ingredients:
                raise serializers.ValidationError('Неуникальные ингредиенты')
            ingredients.append(ingredient)
        return value

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user.id
        queryset = RecipeFavorites.objects.filter(
            user=request_user,
            recipe=obj.id
        ).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user.id
        queryset = RecipeCart.objects.filter(
            user=request_user,
            recipe=obj.id
        ).exists()
        return queryset

    def create(self, validated_data):
        instance = Recipe.objects.create(
            name=validated_data.get('name'),
            text=validated_data.get('text'),
            author=self.context.get('request').user,
            image=validated_data.get('image'),
            cooking_time=validated_data.get('cooking_time')
        )
        for i in validated_data.get('recipeingredient_set'):
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=i.get('ingredient'),
                amount=i.get('amount')
            )
        for t in validated_data.get('tags'):
            tag = Tag.objects.get(pk=t)
            RecipeTag.objects.create(
                recipe=instance,
                tag=tag
            )
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.author = self.context.get('request').user
        instance.image = validated_data.get('image')
        instance.cooking_time = validated_data.get('cooking_time')

        instance.recipeingredient_set.all().delete()
        for i in validated_data.get('recipeingredient_set'):
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=i.get('ingredient'),
                amount=i.get('amount')
            )
        instance.recipetag_set.all().delete()
        for t in validated_data.get('tags'):
            tag = Tag.objects.get(pk=t)
            RecipeTag.objects.create(
                recipe=instance,
                tag=tag
            )
        return instance
