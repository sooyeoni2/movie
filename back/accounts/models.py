from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    genres = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}의 프로필"
    

class User(AbstractUser):
    pass


class Review(models.Model):
    """영화 리뷰"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    movie_id = models.IntegerField() 
    movie_title = models.CharField(max_length=200) 
    rating = models.IntegerField() 
    content = models.TextField()  
    likes = models.IntegerField(default=0)  
    dislikes = models.IntegerField(default=0)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.movie_title}"


class Comment(models.Model):
    """리뷰에 대한 댓글"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.review.movie_title}"


class ReviewLike(models.Model):
    """리뷰 좋아요/싫어요"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE
    )
    is_like = models.BooleanField()
    
    class Meta:
        unique_together = ['user', 'review']
    
    def __str__(self):
        return f"{self.user.username} - {self.review.movie_title} ({'좋아요' if self.is_like else '싫어요'})"

