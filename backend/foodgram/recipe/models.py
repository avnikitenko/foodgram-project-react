from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.settings import MIN_COOKING_TIME, MIN_INGREDIENT_AMOUNT


User = get_user_model()


class Tag(models.Model):
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

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='name',
        help_text='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='measurement_unit',
        help_text='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measrement_unit'
            )
        ]


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='name',
        help_text='Название'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/',
        blank=True  # !!! убрать
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


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
        verbose_name = 'Связь рецепта с ингредиентом'
        verbose_name_plural = 'Связь рецептов с ингредиентами'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


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
        verbose_name = 'Связь рецепта с тегом'
        verbose_name_plural = 'Связь рецептов с тегами'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag'
            )
        ]


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
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]


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
        verbose_name = 'Рецепт в списке избранных'
        verbose_name_plural = 'Рецепты в списках избранных'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_favorites'
            )
        ]


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
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзинах'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_cart'
            )
        ]
