# Generated by Django 4.1 on 2022-08-29 19:19

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_userprofile_main_userpr_last_na_c3be3e_idx'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['address_1']},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['title']},
        ),
        migrations.AlterField(
            model_name='address',
            name='address_2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='categories', to='main.post'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='posts',
            field=models.ManyToManyField(blank=True, related_name='ingredients', to='main.post'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orderitems', to='main.post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='review',
            name='text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
