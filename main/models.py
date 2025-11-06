# main/models.py
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Avg, Count

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("main:product_list_by_category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='products',
        null=True, blank=True
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    # НОВЕ поле з форматуванням:
    detailed_description = RichTextUploadingField(
        blank=True,
        help_text="Детальний опис товару з форматуванням (CKEditor)"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True)
    views = models.IntegerField(default=0)
    featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("main:product_detail", args=[self.id, self.slug])

    def get_average_rating(self):
        value = self.reviews.filter(is_active=True).aggregate(avg=Avg('rating'))['avg']
        return round(value or 0, 2)

    def get_reviews_count(self):
        return self.reviews.filter(is_active=True).count()

    def get_rating_distribution(self):
        dist = {i: 0 for i in range(1, 6)}
        qs = self.reviews.filter(is_active=True).values('rating').annotate(c=Count('rating'))
        for row in qs:
            dist[row['rating']] = row['c']
        return dist
