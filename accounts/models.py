from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Користувач')
    bio = models.TextField('Біографія', blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    birth_date = models.DateField('Дата народження', blank=True, null=True)
    location = models.CharField('Місто', max_length=100, blank=True)
    website = models.URLField('Веб-сайт', blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'

    def __str__(self):
        return f'Профіль {self.user.username}'
