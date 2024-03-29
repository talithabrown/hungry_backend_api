from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, UpdateModelMixin ,DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from .models import Category, Order, OrderItem, Post, Review, Cart, CartItem, UserProfile, PostImage, Ingredient
from .filters import PostFilter
from .serializers import AddCartItemSerializer, CartSerializer, CategorySerializer, CreateOrderSerializer, PostImageSerializer, PostSerializer, ReviewSerializer, CartItemSerializer, UpdateCartItemSerializer, UpdateOrderSerializer, UserProfileSerializer, OrderSerializer, PostIngredientSerializer
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewUserProfileHistoryPermission
import math
from django.db.models import Q
from functools import reduce

# Create your views here.


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    # permission_classes = [IsAdminUser]

    # def get_serializer_context(self):
    #     if self.request.method == 'POST':
    #         return {'user_id': self.request.body.user.id}
    #     return

    @action(detail=True, permission_classes=[ViewUserProfileHistoryPermission])
    def history(self, request, pk):
        return Response('ok')

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        userprofile = UserProfile.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = UserProfileSerializer(userprofile)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(userprofile, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)



class PostViewSet(ModelViewSet):
    # queryset = Post.objects.prefetch_related('images').prefetch_related('ingredients').select_related('user').all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PostFilter
    pagination_class = DefaultPagination
    # permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_update', 'ready_date_time']

    # def get_queryset(self):
    #     queryset = Post.objects.all()
    #     category_id = self.request.query_params.get('category_id')
    #     if category_id is not None:
    #         queryset = queryset.filter(categories=category_id)
    #     return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        user = UserProfile.objects.filter(pk=data['user']).first()
        if data['delivery'] == 'true':
            delivery = True
        else:
            delivery = False
        if data['pick_up'] == 'true':
            pick_up = True
        else:
            pick_up = False
        new_post = Post.objects.create(title=data['title'], description=data['description'], delivery=delivery, pick_up=pick_up, price=data['price'], ready_date_time=data['ready_date_time'], servings_available=data['servings_available'], location=data['location'], latitude=data['latitude'], longitude=data['longitude'], user=user)
        new_post.save()

        for category in data['categories']:
            cat_obj = Category.objects.get(pk=category)
            new_post.categories.add(cat_obj)
        
        serializer = PostSerializer(new_post)

        return Response(serializer.data)

        # serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        # serializer.is_valid(raise_exception=True)
        # order = serializer.save()
        # serializer = OrderSerializer(order)
        # return Response(serializer.data)

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(post_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Post cannot be deleted because it is associated with an order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Post.objects.prefetch_related('images').prefetch_related('ingredients').select_related('user').all()

        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        radius = self.request.query_params.get('radius')

        max_price = self.request.query_params.get('maxprice')
        min_price = self.request.query_params.get('minprice')
        delivery_options = self.request.query_params.get('deliveryoptions')
        categories = self.request.query_params.get('categories')
        search_words = self.request.query_params.get('searchwords')

        if (lat is not None) and (lon is not None) and (radius is not None):

            lat = float(lat)
            lon = float(lon)
            radius = float(radius)

            R = 3959  #earth's mean radius in miles
            sin = math.sin
            cos = math.cos
            acos = math.acos
            pi = math.pi

            minLat = lat - radius/R*180/pi
            maxLat = lat + radius/R*180/pi
            minLon = lon - radius/R*180/pi / cos(lat*pi/180)
            maxLon = lon + radius/R*180/pi / cos(lat*pi/180)

            queryset = queryset.filter(latitude__gt=minLat, latitude__lt=maxLat, longitude__gt=minLon, longitude__lt=maxLon)

        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if delivery_options is not None:
            if delivery_options == 'both':
                queryset = queryset.filter(delivery=True, pick_up=True)
            elif delivery_options == 'delivery':
                queryset = queryset.filter(delivery=True)
            elif delivery_options == 'pickup':
                queryset = queryset.filter(pick_up=True)
        if categories is not None:
            categories = categories.split(',')
            queryset = queryset.filter(categories__in=categories).distinct()
        if search_words is not None:
            search_words = search_words.split(',')
            queryset = queryset.filter(reduce(lambda x, y: x | y, [Q(title__icontains=word) for word in search_words]))


        return queryset

        # For latitudes use: Decimal(8,6), and longitudes use: Decimal(9,6)
        # http://127.0.0.1:8000/main/posts/?lat=34.465037&lon=-110.091227&radius=10


class UserProfilePostsViewSet(ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.prefetch_related('images').prefetch_related('ingredients').filter(user=self.kwargs['userprofile_pk'])


class PostImageViewSet(ModelViewSet):
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}
    
    def get_queryset(self):
        return PostImage.objects.filter(post_id=self.kwargs['post_pk'])



class PostIngredientViewSet(ModelViewSet):
    serializer_class = PostIngredientSerializer

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}
    
    def get_queryset(self):
        return Ingredient.objects.filter(post_id=self.kwargs['post_pk'])




class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(posts_count=Count('posts')).all()
    serializer_class = CategorySerializer
    #permission_classes = [IsAdminOrReadOnly]

    # def destroy(self, request, *args, **kwargs):
    #     if Post.objects.filter(category_id=kwargs['pk']).count() > 0:
    #         return Response({'error': 'Category cannot be deleted because it is associated with one or more posts'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     return super().destroy(request, *args, **kwargs)

    def destory(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.posts.count() > 0:
            return Response({'error': 'Category cannot be deleted because it is associated with one or more posts'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all().select_related('post')

        post_id = self.request.query_params.get('post')
        profile_id = self.request.query_params.get('profile')
        reviewer = self.request.query_params.get('reviewer')

        if post_id is not None:
            post_id = int(post_id)
            queryset = queryset.filter(post_id=post_id)
        elif profile_id is not None:
            profile_id = int(profile_id)
            queryset = queryset.filter(post__user=profile_id)
        elif reviewer is not None:
            reviewer = int(reviewer)
            queryset = queryset.filter(reviewer_user=reviewer)

        return queryset



class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.prefetch_related('items__post').all()



class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        # cart_id = Cart.objects.only('id').get(uuid=self.kwargs['cart_pk'])
        # return CartItem.objects.filter(cart_id=cart_id).select_related('post')
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('post').order_by('post__title')

    def get_serializer_context(self):
        # cart_id = Cart.objects.only('id').get(uuid=self.kwargs['cart_pk'])
        cart_id = self.kwargs['cart_pk']
        return {'cart_id': cart_id}



class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        
        user_profile_id = UserProfile.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(user_profile_id=user_profile_id).order_by('-placed_at')
