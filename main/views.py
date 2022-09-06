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
from .models import Category, Order, OrderItem, Post, Review, Cart, CartItem, UserProfile, PostImage
from .filters import PostFilter
from .serializers import AddCartItemSerializer, CartSerializer, CategorySerializer, CreateOrderSerializer, PostImageSerializer, PostSerializer, ReviewSerializer, CartItemSerializer, UpdateCartItemSerializer, UpdateOrderSerializer, UserProfileSerializer, OrderSerializer
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions, ViewUserProfileHistoryPermission

# Create your views here.


class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAdminUser]

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
    queryset = Post.objects.prefetch_related('images').all()
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

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(post_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Post cannot be deleted because it is associated with an order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)



class PostImageViewSet(ModelViewSet):
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}
    
    def get_queryset(self):
        return PostImage.objects.filter(post_id=self.kwargs['post_pk'])



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(posts_count=Count('posts')).all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

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
        return Review.objects.filter(post_id=self.kwargs['post_pk'])

    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk']}



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
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('post')

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}



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
        return Order.objects.filter(user_profile_id=user_profile_id)
