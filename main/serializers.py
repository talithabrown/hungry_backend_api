from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import Cart, CartItem, Order, OrderItem, Post, PostImage, Review, UserProfile, Category, Ingredient

class UserProfileSerializer(serializers.ModelSerializer):
    #eventually I will take the user_id from the request body instead
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user_id', 'bio', 'phone', 'birth_date', 'is_seller']



class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image']

    def create(self, validated_data):
        post_id = self.context['post_id']
        return PostImage.objects.create(post_id=post_id, **validated_data)


class PostIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']



class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    ingredients = PostIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'description', 'delivery', 'pick_up', 'price', 'price_with_tax', 'ready_date_time', 'servings_available', 'location', 'last_update', 'ingredients', 'user', 'images']
    
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    # # user = serializers.StringRelatedField()
    # # user = UserProfileSerializer()
    # user = serializers.HyperlinkedRelatedField(
    #     queryset=UserProfile.objects.all(),
    #     view_name='user-profile-detail'
    # )

    def calculate_tax(self, post: Post):
        return post.price * Decimal(1.1)



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'posts_count']

    posts_count = serializers.IntegerField(read_only=True)



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'title', 'text', 'created', 'updated', 'reviewer_user']

    def create(self, validated_data):
        post_id = self.context['post_id']
        return Review.objects.create(post_id=post_id, **validated_data)



class SimplePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields =['id', 'title', 'price']



class CartItemSerializer(serializers.ModelSerializer):
    post = SimplePostSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.post.price

    class Meta:
        model = CartItem
        fields = ['id', 'post', 'quantity', 'total_price']

    # def create(self, validated_data):
    #     cart_id = self.context['cart_id']
    #     return CartItem.objects.create(cart_id=cart_id, **validated_data)



class CartSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart:Cart):
        return sum([item.quantity * item.post.price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['uuid', 'items', 'total_price']



class AddCartItemSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        if not Post.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No post with the given id was found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        post_id = self.validated_data['post_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, post_id=post_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'post_id', 'quantity']



class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']



class OrderItemSerializer(serializers.ModelSerializer):
    post = SimplePostSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'post', 'unit_price', 'quantity']



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user_profile', 'placed_at', 'payment_status', 'items']



class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']



class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            user_profile = UserProfile.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(user_profile=user_profile)

            cart_items = CartItem.objects \
                                .select_related('post') \
                                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    post=item.post,
                    unit_price = item.post.price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(sender=self.__class__, order=order)

            return order


# This is an example of overriding the validate method. This should go in a serializer class.
# def validate(self, data):
#     if data['password'] != data['confirm_password']:
#         return serializers.ValidationError('Passwords do not match')
#     return data

# This is an example of overriding the create method. This should go in a serializer class.
# def create(self, validated_data):
#   post = Post(**validated_data)
#   post.fieldyouwanttoadd = 1
#   post.save()
#   return post
