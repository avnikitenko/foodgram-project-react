# Generated by Django 4.0.5 on 2022-06-19 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Название', max_length=200, unique=True, verbose_name='name'),
        ),
    ]