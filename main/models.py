from enum import unique
from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4
from .validators import validate_file_size

# Create your models here.


class UserProfile(models.Model):
    # first_name = models.CharField(max_length=255)
    # last_name = models.CharField(max_length=255, null=True, blank=True)
    # username = models.CharField(max_length=255, unique=True)
    # password = models.CharField(max_length=255)
    # email = models.EmailField(max_length=255, unique=True)
    bio = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles/images', validators=[validate_file_size], null=True)
    # address

    def __str__(self) -> str:
        return f'{self.user.username} ({self.user.first_name} {self.user.last_name})'

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

    @admin.display(ordering='user__username')
    def username(self):
        return self.user.username    

    class Meta:
        permissions = [
            ('view_history', 'Can view history')
        ]

# class ProfileImage(models.Model):
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='image')
#     image = models.ImageField(upload_to='profiles/images', validators=[validate_file_size])

class Address(models.Model):
    address_1 = models.CharField(max_length=255)
    address_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=5)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='address')

    def __str__(self) -> str:
        if self.address_2:
            return f'{self.address_1} {self.address_2}, {self.city} {self.state}'
        return f'{self.address_1}, {self.city} {self.state}'

    class Meta:
        ordering = ['address_1']



class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    delivery = models.BooleanField()
    pick_up = models.BooleanField()
    price = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    ready_date_time = models.DateTimeField()
    servings_available = models.IntegerField(validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=20, decimal_places=17)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # categories
    # ingredients
    # reviews
    # images

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']



class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/images', validators=[validate_file_size])



class Category(models.Model):
    title = models.CharField(max_length=255)
    posts = models.ManyToManyField(Post, related_name='categories', blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']



class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='ingredients')

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ['name']



class Review(models.Model):
    rating = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reviews')
    reviewer_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']



class Order(models.Model):

    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed')
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=5, decimal_places=2)



class Cart(models.Model):
    #
    # id = models.UUIDField(primary_key=True, default=uuid4)
    id = models.UUIDField(default=uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # items


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'post']]

