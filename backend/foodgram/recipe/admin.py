from django.contrib import admin
from django.db.models import Count

from .models import (
    Follow, Ingredient, Recipe, RecipeCart,
    RecipeFavorites, RecipeIngredient, RecipeTag, Tag,
    User
)


class UserAdmin(admin.ModelAdmin):

    list_filter = [
        'username', 'email', 'last_name', 'first_name'
    ]
    list_display = [
        'username', 'email', 'last_name', 'first_name', 'is_staff'
    ]


class RecipeAdmin(admin.ModelAdmin):
    list_filter = ['name', 'author', 'tags']
    list_display = ['name', 'author', 'is_favorite_count']

    def get_queryset(self, request):
        qs = super(RecipeAdmin, self).get_queryset(request)
        return qs.annotate(user_favorites_cnt=Count('user_favorites'))

    def is_favorite_count(self, inst):
        return inst.user_favorites_cnt
    is_favorite_count.admin_order_field = 'user_favorites_cnt'


class IngredientAdmin(admin.ModelAdmin):
    list_filter = ['name']


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Follow)
admin.site.register(RecipeFavorites)
admin.site.register(RecipeCart)
