# Generated by Django 4.1.1 on 2022-12-01 23:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_post_latitude_alter_post_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='reviewer_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='main.userprofile'),
        ),
    ]
