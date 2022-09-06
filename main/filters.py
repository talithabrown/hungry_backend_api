from django_filters.rest_framework import FilterSet
from .models import Post

class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'categories': ['iexact'],
            'price': ['lt', 'gt'],
            # 'delivery': [''],
            # 'pick_up': [],
            # 'ready_date_time': ['date'],
            'servings_available': ['gt'],
            # 'location': [],
            # 'last_update': []

        }