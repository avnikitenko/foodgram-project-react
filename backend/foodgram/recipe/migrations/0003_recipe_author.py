# Generated by Django 4.0.5 on 2022-06-19 13:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe', '0002_alter_ingredient_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(default=2, help_text='Автор рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='author_recipes', to=settings.AUTH_USER_MODEL, verbose_name='author'),
            preserve_default=False,
        ),
    ]