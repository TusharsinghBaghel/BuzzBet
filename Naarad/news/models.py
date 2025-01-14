from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Location(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    address  = models.CharField(max_length=255)
    def __str__(self):
        return self.address

class newsPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'news_posts')
    headline = models.CharField(max_length=255)
    content = models.TextField()
    photo = models.ImageField(upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    impact = models.FloatField(default=0.0)
    bet = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])  # Bet amount
    validity = models.FloatField(
        default = 0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null = True, blank = True)
    reacted_by = models.ManyToManyField(User, related_name='reactions', blank=True)
    def __str__(self):
        return self.headline

class Comment(models.Model):
    news_post = models.ForeignKey(newsPost, related_name = 'comments', on_delete = models.CASCADE)
    author = models.ForeignKey(User, related_name= 'comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    validity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        default = 0.0
    )

    def __Str__(self):
        return f'by {self.author.username} on {self.news_post.title}'