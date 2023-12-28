from datetime import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from users.models import User


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Board.Status.PUBLISHED)


class Board(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=250, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='slug',
                            validators=[
                                MinLengthValidator(5, message='Минимум 5 символов'),
                                MaxLengthValidator(100, message='Максимум 100 символов'),
                            ])
    img = models.ImageField(upload_to='uploads/%Y/%m/%d/', default=None,
                              blank=True, null=True, verbose_name='Картинки')
    upload = models.FileField(upload_to='uploads/%Y/%m/%d/', default=None,
                              blank=True, null=True, verbose_name='Файлы')
    content = models.TextField(blank=True, verbose_name='Текст статьи')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    is_published = models.BooleanField(choices=tuple(map(lambda x: (bool(x[0]), x[1]), Status.choices)),
                                       default=Status.DRAFT, verbose_name='Опубликовать')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Категории')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags', verbose_name='Теги')
    author = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='posts', null=True, default=None)

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объявления, информация, новости'
        verbose_name_plural = 'Объявления, информация, новости'
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    #def save(self, *args, **kwargs):
     #   self.slug = slugify(translit_to_eng(self.title))
       # super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')


class Comment(models.Model):
    post = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(username=username, email=self.normalize_email(email),)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password,)
        user.is_admin = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


@property
def is_staff(self):
    return self.is_admin
