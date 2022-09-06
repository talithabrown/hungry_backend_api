from django.contrib import admin
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode
from . import models

# Register your models here.

@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'posts_count', 'orders_count']
    list_per_page = 20
    list_select_related = ['user']
    ordering = ['user__username']
    search_fields = ['first_name__istartswith', 'last_name__istartswith', 'username__istartswith']

    def posts_count(self, userprofile):
        url = (
            reverse('admin:main_post_changelist') 
            + '?'
            + urlencode({
                'userprofile__id': str(userprofile.id)
            })
            )
        return format_html('<a href="{}">{}</a>', url, userprofile.posts_count)

    def orders_count(self, userprofile):
        url = (
            reverse('admin:main_order_changelist') 
            + '?'
            + urlencode({
                'userprofile__id': str(userprofile.id)
            })
            )
        return format_html('<a href="{}">{}</a>', url, userprofile.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            posts_count=Count('post')
        ).annotate(
            orders_count=Count('order')
        )

    

@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_1', 'address_2', 'city', 'state', 'user_profile']
    list_per_page = 20
    search_fields = ['address_1__istartswith', 'city__istartswith', 'state__istartswith']
    autocomplete_fields = ['user_profile']


class PostImageInline(admin.TabularInline):
    model = models.PostImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'user_link']
    list_per_page = 20
    list_filter = ['categories']
    search_fields = ['title__istartswith']
    autocomplete_fields = ['user']
    inlines = [PostImageInline]

    def user_link(self, post):
        url = (
            reverse('admin:main_userprofile_changelist') 
            + '?'
            + urlencode({
                'post__id': str(post.id)
            })
            )
        return format_html('<a href="{}">{}</a>', url, post.user)

    class Media:
        css = {
            'all': ['main/styles.css']
        }

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    exclude = ['posts']
    list_display = ['title', 'posts_count']
    list_per_page = 20
    search_fields = ['title__istartswith']

    @admin.display(ordering='posts_count')
    def posts_count(self, category):
        return category.posts_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            posts_count=Count('posts')
        )

@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    exclude = ['posts']
    list_display = ['name']
    list_per_page = 20
    search_fields = ['name__istartswith']

@admin.register(models.Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'rating', 'reviewer_user']
    list_per_page = 20
    search_fields = ['title__istartswith', 'reviewer_user__istartswith']
    autocomplete_fields = ['post', 'reviewer_user']



class CartItemInline(admin.TabularInline):
    model = models.CartItem
    min_num = 1
    max_num = 10
    extra = 0
    autocomplete_fields = ['post']


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'id']
    list_per_page = 20
    search_fields = ['id__istartswith', 'created_at__istartswith']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['post']
    min_num = 1
    max_num = 10
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'placed_at', 'payment_status']
    list_per_page = 20
    search_fields = ['id__istartswith']
    autocomplete_fields = ['user_profile']
    inlines = [OrderItemInline]