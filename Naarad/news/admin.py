from django.contrib import admin
from .models import newsPost, Comment
# Register your models here.
admin.site.register(newsPost)
admin.site.register(Comment)
