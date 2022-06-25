# Generated by Django 4.0.5 on 2022-06-25 08:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0005_alter_recipe_image'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='unique_follow',
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Название', max_length=200, unique=True, verbose_name='name'),
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together={('user', 'author')},
        ),
        migrations.AlterUniqueTogether(
            name='recipecart',
            unique_together={('user', 'recipe')},
        ),
        migrations.AlterUniqueTogether(
            name='recipefavorites',
            unique_together={('user', 'recipe')},
        ),
        migrations.AlterUniqueTogether(
            name='recipeingredient',
            unique_together={('recipe', 'ingredient')},
        ),
        migrations.AlterUniqueTogether(
            name='recipetag',
            unique_together={('recipe', 'tag')},
        ),
    ]