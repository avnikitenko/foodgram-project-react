from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.settings import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT


User = get_user_model()


class Tag(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='name',
        help_text='Название'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='hex_color',
        help_text='Цвет в HEX',
        blank=True,
        null=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='code',
        help_text='Уникальный слаг'
    )


class Ingredient(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='name',
        help_text='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='measurement_unit',
        help_text='Единицы измерения'
    )


class Recipe(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='name',
        help_text='Название'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/'
    )
    text = models.TextField(
        verbose_name='description',
        help_text='Описание'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_COOKING_TIME)
        ],
        verbose_name='cooking_time',
        help_text='Время приготовления (в минутах)'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ingredients',
        help_text='Ингредиенты в рецепте'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='tags',
        help_text='Тэги рецепта'
    )
    user_favorites = models.ManyToManyField(
        User,
        through='RecipeFavorites',
        related_name='recipes_in_fav',
        verbose_name='user_favorites',
        help_text='Пользователи, добавившие рецепт в избранное'
    )
    user_carts = models.ManyToManyField(
        User,
        through='RecipeCart',
        related_name='recipes_in_cart',
        verbose_name='user_carts',
        help_text='Пользователи, добавившие рецепт в корзину'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_recipes',
        verbose_name='author',
        help_text='Автор рецепта'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipes',
        help_text='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ingredient',
        help_text='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[
            MinValueValidator(MIN_INGREDIENT_AMOUNT)
        ],
        verbose_name='amount',
        help_text='Количество ингредиента в рецепте'
    )

    class Meta:
        unique_together = ['recipe', 'ingredient']


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        help_text='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='tag',
        help_text='Тэг'
    )

    class Meta:
        unique_together = ['recipe', 'tag']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ['user', 'author']


class RecipeFavorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        help_text='Рецепт в избранном'
    )

    class Meta:
        unique_together = ['user', 'recipe']


class RecipeCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='user',
        help_text='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='recipe',
        help_text='Рецепт в корзине'
    )

    class Meta:
        unique_together = ['user', 'recipe']
