import webcolors
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Follow, Ingredient, Recipe, RecipeCart,
                           RecipeFavorites, RecipeIngredient, RecipeTag, Tag,
                           User)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request_user_id = self.context.get('request').user.id
        queryset = Follow.objects.filter(
            author=obj.id,
            user=request_user_id
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

    def validate(self, data):
        try:
            webcolors.hex_to_name(data['color'])
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['user', 'author']

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        if Follow.objects.filter(
            user=data['user'],
            author=data['author']
        ).exists():
            raise serializers.ValidationError('Такая подписка уже существует')
        return data


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
        request_user_id = self.context.get('request').user.id
        queryset = Follow.objects.filter(
            author=obj.id,
            user=request_user_id
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

    def validate(self, data):
        if RecipeFavorites.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное'
            )
        return data


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeCart
        fields = ['user', 'recipe']

    def validate(self, data):
        if RecipeCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину'
            )
        return data


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
    image = Base64ImageField()

    def to_internal_value(self, data):
        tags_id = data.get('tags')
        internal_data = super().to_internal_value(data)
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

    def validate(self, data):
        tags = data.get('tags')
        if not tags and not self.partial:
            raise ValidationError(
                {'tags': ['Определите теги']},
                code='invalid',
            )
        else:
            for tag_id in tags:
                if not Tag.objects.filter(pk=tag_id).exists():
                    raise ValidationError(
                        {'tags': ['Некорректный идентификатор тега']},
                        code='invalid',
                    )
            if len(tags) != len(set(tags)):
                raise ValidationError(
                    {'tags': ['Неуникальные идентификаторы тегов']},
                    code='invalid',
                )
        ingredients = data.get('ingredients')
        if ingredients:
            ingredients = []
            for recipe_ingredient in ingredients:
                ingredient = recipe_ingredient['ingredient']
                if ingredient in ingredients:
                    raise serializers.ValidationError(
                        'Неуникальные ингредиенты'
                    )
                ingredients.append(ingredient)
        return data

    def get_is_favorited(self, obj):
        request_user_id = self.context.get('request').user.id
        queryset = RecipeFavorites.objects.filter(
            user=request_user_id,
            recipe=obj.id
        ).exists()
        return queryset

    def get_is_in_shopping_cart(self, obj):
        request_user_id = self.context.get('request').user.id
        queryset = RecipeCart.objects.filter(
            user=request_user_id,
            recipe=obj.id
        ).exists()
        return queryset

    def recipe_ingredient_create(self, recipe, recipe_ingredient_data):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                **ingredients
            ) for ingredients in recipe_ingredient_data]
        )

    def recipe_tag_create(self, recipe, tags):
        RecipeTag.objects.bulk_create(
            [RecipeTag(
                recipe=recipe,
                tag=get_object_or_404(Tag, id=tag)
            ) for tag in tags]
        )

    def create(self, validated_data):
        recipe_ingredient_data = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')

        instance = Recipe.objects.create(
            author=self.context.get('request').user,
            image=validated_data.pop('image'),
            **validated_data
        )
        self.recipe_ingredient_create(instance, recipe_ingredient_data)
        self.recipe_tag_create(instance, tags)
        return instance

    def update(self, instance, validated_data):
        recipeingredient_set = validated_data.pop('recipeingredient_set', None)
        if recipeingredient_set:
            instance.recipeingredient_set.all().delete()
            self.recipe_ingredient_create(instance, recipeingredient_set)
        tags = validated_data.pop('tags', None)
        if tags:
            instance.recipetag_set.all().delete()
            self.recipe_tag_create(instance, tags)
        super().update(instance, validated_data)
        return instance
