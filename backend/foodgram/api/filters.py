import django_filters
from recipe.models import Tag

flag_choises = ((0, False), (1, True))


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.ChoiceFilter(
        method='get_is_favorited',
        choices=flag_choises
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        method='get_is_in_shopping_cart',
        choices=flag_choises
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        lookup_type="eq"
    )
    author = django_filters.NumberFilter()

    def get_is_favorited(self, queryset, field_name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value == '1':
            filter_ids = self.request.user.recipes_in_fav.values_list(
                'id'
            )
            return queryset.filter(id__in=filter_ids)
        if value == '0':
            filter_ids = self.request.user.recipes_in_fav.values_list(
                'id'
            )
            return queryset.exclude(id__in=filter_ids)
        return queryset.none()

    def get_is_in_shopping_cart(self, queryset, field_name, value):
        if not self.request.user.is_authenticated:
            return queryset.none()
        if value == '1':
            filter_ids = self.request.user.recipes_in_cart.values_list(
                'id'
            )
            return queryset.filter(id__in=filter_ids)
        if value == '0':
            filter_ids = self.request.user.recipes_in_cart.values_list(
                'id'
            )
            return queryset.exclude(id__in=filter_ids)
        return queryset.none()
