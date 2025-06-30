from django.db import models
import uuid

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

# Define category choices
MAIN_CATEGORIES = [
    ("World-News", "World-News"),
    ("Local-News", "Local-News"),
    ("Sport", "Sport"),
    ("Technology", "Technology"),
    ("Entertainment", "Entertainment"),
    ("Scientific", "Scientific"),
    ("Business", "Business"),
    ("Politics", "Politics"),
]

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
    
    # Add structured categories
    main_category = models.CharField(max_length=50, choices=MAIN_CATEGORIES)
    sub_category = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.header
