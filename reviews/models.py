from django.conf import settings
from django.db import models

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey('main.Product', on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField(max_length=1000)
    advantages = models.TextField(blank=True)
    disadvantages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ['product', 'author']  # один користувач — один відгук на товар
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product} — {self.author} ({self.rating}/5)'

    def get_rating_display_stars(self) -> str:
        # Юнікод-зірочки для виводу в шаблонах
        return '★' * int(self.rating) + '☆' * (5 - int(self.rating))
