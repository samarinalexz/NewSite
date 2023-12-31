# Generated by Django 5.0 on 2023-12-28 13:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('board', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='author',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='board',
            name='cat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='posts', to='board.category', verbose_name='Категории'),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='board.board'),
        ),
        migrations.AddField(
            model_name='board',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tags', to='board.tagpost', verbose_name='Теги'),
        ),
        migrations.AddIndex(
            model_name='board',
            index=models.Index(fields=['-time_create'], name='board_board_time_cr_f1b136_idx'),
        ),
    ]
