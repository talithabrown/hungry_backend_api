# Generated by Django 4.1.1 on 2022-10-21 18:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_userprofile_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='posts',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='post',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='main.post'),
            preserve_default=False,
        ),
    ]
