from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField
import uuid
from .constants import MAIN_CATEGORIES

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    subscribe_newsletter = models.BooleanField(default=False)
    notification_preferences = MultiSelectField(choices=MAIN_CATEGORIES, blank=True)
    post_read_history = models.ManyToManyField("NewsPost", blank=True, related_name="read_by_users")
    comment_history = models.ManyToManyField("Comment", blank=True, related_name="commented_by_users")
    profile_picture = models.URLField(blank=True, null=True)
    time_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.full_name or "Anonymous User"


    
class Source(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField()

    def __str__(self):
        return self.name

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    profile_pic = models.URLField()
    comment = models.TextField()
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.comment[:30]}..."

class NewsPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.URLField()
    header = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    source = models.CharField(max_length=255)
    comments = models.ManyToManyField(Comment, blank=True, related_name='news_posts')
    views = models.PositiveIntegerField(default=0)
    share_link = models.URLField()
    main_category = models.CharField(max_length=50, choices=MAIN_CATEGORIES)
    sub_category = models.CharField(max_length=100, blank=True)
    
    is_top_news = models.BooleanField(default=False)
    top_news_priority = models.PositiveSmallIntegerField(
        null=True, blank=True, unique=True,
        help_text="Priority from 1 (highest) to 20 (lowest) for top news."
    )

    def __str__(self):
        return self.header

