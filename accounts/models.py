from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='User')
    bio = models.TextField('About', blank=True)
    avatar = models.ImageField('Profile image', upload_to='avatars/%Y/%m/%d/', blank=True, null=True)
    birth_date = models.DateField('Date of birth', blank=True, null=True)
    location = models.CharField('Location', max_length=100, blank=True)
    website = models.URLField('Website', blank=True)
    created_at = models.DateTimeField('Created', auto_now_add=True)
    updated_at = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f'Profile for {self.user.username}'
