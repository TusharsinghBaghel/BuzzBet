from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import JSONField  # if using PostgreSQL
from news.models import newsPost
from accounts.models import Profile


class PostInteraction(models.Model):
    post = models.ForeignKey('news.newsPost', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE)
    validity = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    impact = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} - {self.post}' 
    
class TrainingRun(models.Model):
    run_date = models.DateTimeField(auto_now_add=True)
    global_bias = models.FloatField(default=0.0)
    hyperparameters = JSONField(default=dict)  # e.g., {"lambda_i": 0.05, "lambda_f": 0.01, "latent_dim": 20}
    training_loss = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"TrainingRun {self.id} at {self.run_date}"
    

class NewsPostLatentProfile(models.Model):
    post = models.OneToOneField(newsPost, on_delete=models.CASCADE)
    intercept = models.FloatField(default=0.0)
    latent_factors = JSONField(default=list)  # Store as a list of floats
    birdwatch_status = models.CharField(max_length=20, blank=True, default="unknown")  # New field for classification

    def __str__(self):
        return f"Latent factors for {self.post.headline}"

class UserLatentProfile(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    intercept = models.FloatField(default=0.0)
    latent_factors = JSONField(default=list)  # Store as list of floats (latent vector)

    def __str__(self):
        return f"Latent factors for {self.user.username}"
    

