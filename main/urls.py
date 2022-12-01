from cgitb import lookup
from xml.etree.ElementInclude import include
from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('posts', views.PostViewSet, basename='posts')
router.register('categories', views.CategoryViewSet)
router.register('carts', views.CartViewSet)
router.register('userprofiles', views.UserProfileViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.register('reviews', views.ReviewViewSet, basename='reviews')

posts_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('reviews', views.ReviewViewSet, basename='post-reviews')
posts_router.register('images', views.PostImageViewSet, basename='post-images')
posts_router.register('ingredients', views.PostIngredientViewSet, basename='post-ingredients')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

userprofiles_router = routers.NestedDefaultRouter(router, 'userprofiles', lookup='userprofile')
userprofiles_router.register('posts', views.UserProfilePostsViewSet, basename='userprofile-posts')

urlpatterns = router.urls + posts_router.urls + carts_router.urls + userprofiles_router.urls