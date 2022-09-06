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

posts_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('reviews', views.ReviewViewSet, basename='post-reviews')
posts_router.register('images', views.PostImageViewSet, basename='post-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + posts_router.urls + carts_router.urls