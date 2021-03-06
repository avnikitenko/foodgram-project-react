# Generated by Django 4.0.5 on 2022-06-26 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_remove_follow_unique_follow_alter_tag_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='recipecart',
            options={'verbose_name': 'Рецепт в корзине', 'verbose_name_plural': 'Рецепты в корзинах'},
        ),
        migrations.AlterModelOptions(
            name='recipefavorites',
            options={'verbose_name': 'Рецепт в списке избранных', 'verbose_name_plural': 'Рецепты в списках избранных'},
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Связь рецепта с ингредиентом', 'verbose_name_plural': 'Связь рецептов с ингредиентами'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'verbose_name': 'Связь рецепта с тегом', 'verbose_name_plural': 'Связь рецептов с тегами'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тег', 'verbose_name_plural': 'Теги'},
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='recipecart',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='recipefavorites',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='recipetag',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
        migrations.AddConstraint(
            model_name='recipecart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipefavorites',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_recipe_favorites'),
        ),
        migrations.AddConstraint(
            model_name='recipeingredient',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredient'),
        ),
        migrations.AddConstraint(
            model_name='recipetag',
            constraint=models.UniqueConstraint(fields=('recipe', 'tag'), name='unique_recipe_tag'),
        ),
    ]
