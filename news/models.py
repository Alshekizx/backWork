from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField
import uuid
from .constants import MAIN_CATEGORIES
from django.utils import timezone 
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)
   

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
    time_joined = models.DateTimeField(default=timezone.now)
    objects = CustomUserManager()
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

class AdminAccount(models.Model):
    USER_TYPES = [
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="account_profile")
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image = models.URLField(blank=True, null=True)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)

    # Nullable: only applicable for employees
    manager = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='employees',
        null=True,
        blank=True,
        limit_choices_to={'user_type': 'manager'},
        help_text="Assign a manager if user_type is 'employee'"
    )

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name} ({self.user_type})"


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
   
    daily_visitors = models.IntegerField(default=0)
    monthly_visitors = models.IntegerField(default=0)
    last_visited = models.DateField(null=True, blank=True)
    
    created_by_employee = models.ForeignKey(
        AdminAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': 'employee'},
        related_name='news_created'
    )
    updated_by_employee = models.ForeignKey(
        AdminAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='news_updates',
        limit_choices_to={'user_type': 'employee'}
    )

    updated_at = models.DateTimeField(auto_now=True)

    is_top_news = models.BooleanField(default=False)
    top_news_priority = models.PositiveSmallIntegerField(
        null=True, blank=True, unique=True,
        help_text="Priority from 1 (highest) to 20 (lowest) for top news."
    )
    
    # ✅ Trending News Fields
    is_trending = models.BooleanField(default=False)
    trending_priority = models.PositiveSmallIntegerField(
        null=True, blank=True, unique=True,
        help_text="Priority from 1 (highest) to 30 (lowest) for trending news."
    )
    # ✅ New Field
    
    is_posted = models.BooleanField(default=False, help_text="Mark as posted or unposted.")
    def update_visit_counts(self):
        today = timezone.now().date()
        if self.last_visited != today:
            self.daily_visitors = 1
            if self.last_visited and self.last_visited.month != today.month:
                self.monthly_visitors = 1
            else:
                self.monthly_visitors += 1
            self.last_visited = today
        else:
            self.daily_visitors += 1
            self.monthly_visitors += 1
        self.save()
        
    def __str__(self):
        return self.header
    


class Advertisement(models.Model):
    AD_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
        ('html', 'HTML Code'),
    ]

    AD_SPACES = [
        ('home-top', 'Home Page - Top Banner'),
        ('blogview-top', 'Blog View - Top'),
        ('blogview-bottom', 'Blog View - Bottom'),
        ('blogselect-sidebar', 'Blog Select - Sidebar'),
        ('blogselect-inline', 'Blog Select - Inline'),
    ]
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    ad_type = models.CharField(max_length=10, choices=AD_TYPES)
    ad_space = models.CharField(max_length=50, choices=AD_SPACES)
    media_url = models.URLField(blank=True, null=True)
    ad_text = models.TextField(blank=True, null=True)
    html_code = models.TextField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100, choices=MAIN_CATEGORIES)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_employee = models.ForeignKey(
        AdminAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': 'employee'},
        related_name='ads_created'
    )
    updated_by_employee = models.ForeignKey(
        AdminAccount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'user_type': 'employee'},
        related_name='ad_updates'
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



