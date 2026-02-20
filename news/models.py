#file : news/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from multiselectfield import MultiSelectField
import uuid
from django.utils import timezone 
from django.contrib.auth.models import BaseUserManager
from django.core.mail import send_mail
from django.conf import settings



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
    notification_preferences = models.ManyToManyField("NewsCategory", blank=True, related_name="subscribed_users")
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
    image = models.URLField(max_length=500)
    header = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    source = models.CharField(max_length=255)
    comments = models.ManyToManyField(Comment, blank=True, related_name='news_posts')
    views = models.PositiveIntegerField(default=0)
    share_link = models.URLField(max_length=1000)
    video_link = models.URLField(blank=True, null=True, help_text="Optional video link for the news post.")
    
    # ✅ Replace MAIN_CATEGORIES with ForeignKey
    main_category = models.ForeignKey(
        "NewsCategory",
        on_delete=models.CASCADE,
        related_name="news_posts"
    )
    sub_category = models.CharField(max_length=250, blank=True)
   
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
    
    is_trending = models.BooleanField(default=False)
    trending_priority = models.PositiveSmallIntegerField(
        null=True, blank=True, unique=True,
        help_text="Priority from 1 (highest) to 30 (lowest) for trending news."
    )
    
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


class NewsCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    keywords = models.TextField(
        help_text="Comma-separated keywords to detect category relevance"
    )

    def keyword_list(self):
        return [k.strip().lower() for k in self.keywords.split(",") if k.strip()]

    def __str__(self):
        return self.name


class CategoryPlacement(models.Model):
    PLACEMENT_CHOICES = [
        ("header", "Header"),
        ("footer", "Footer"),
        ("side_nav", "Homepage Side Nav"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    main_category = models.ForeignKey(
        NewsCategory, on_delete=models.CASCADE, related_name="placements"
    )
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    priority = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("main_category", "placement")  # prevent duplicates

    def __str__(self):
        return f"{self.main_category.name} - {self.placement} (priority {self.priority})"

class CategoryVisit(models.Model):
    main_category = models.OneToOneField(
        NewsCategory,
        on_delete=models.CASCADE,
        related_name="visit_stats"
    )
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.main_category.name} - {self.views} views"


class NewsSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        ("with_image", "Fetch with image"),
        ("no_image", "Fetch without image"),
    ]

    name = models.CharField(max_length=255)
    website = models.URLField()
    rss = models.URLField()
    main_category = models.ForeignKey(
        NewsCategory,
        on_delete=models.CASCADE,
        related_name="sources"
    )

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default="with_image",
        help_text="Should the fetcher expect images from this source?"
    )

    def __str__(self):
        return f"{self.name} ({self.main_category.name})"


class Advertisement(models.Model):
    AD_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('text', 'Text'),
        ('html', 'HTML Code'),
    ]

    AD_SPACES = [
        ('home-top', 'Home Page - Top Banner'),
        ('blogview-left', 'Blog View - Left'),
        ('blogview-right-top', 'Blog View - Right - Top'),
        ('blogview-right-bottom', 'Blog View - Right - Bottom'),
        ('blogselect-sidebar', 'Blog Select - Sidebar'),
        ('blogselect-inline', 'Blog Select - Inline'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    ad_type = models.CharField(max_length=10, choices=AD_TYPES)
    ad_space = models.CharField(max_length=50, choices=AD_SPACES)
    media_url = models.URLField(blank=True, null=True)
    ad_text = models.TextField(blank=True, null=True)
    html_code = models.TextField(blank=True, null=True)
    redirect_url = models.URLField(blank=True, null=True)
    main_category = models.ForeignKey(
    "NewsCategory",
    on_delete=models.CASCADE,
    related_name="ads"
    )

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



class ContactUs(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)  # 👈 Add this field

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Add email to newsletter subscription
        if not NewsLetterSubscription.objects.filter(email=self.email).exists():
            NewsLetterSubscription.objects.create(email=self.email)

        # Send confirmation to the user
        send_mail(
            subject="Thanks for contacting us!",
            message="We received your message and will get back to you shortly.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.email],
            fail_silently=True,
        )

        # Notify admin
        send_mail(
            subject="New Contact Message Received",
            message=f"Name: {self.name}\nEmail: {self.email}\n\nMessage:\n{self.message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],  # Define this in settings.py
            fail_silently=True,
        )

    def __str__(self):
        return f"{self.name} - {self.email}"


class NewsLetterSubscription(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class NewsletterHistory(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients = models.JSONField()  # store list of emails

    def __str__(self):
        return f"{self.subject} ({self.sent_at})"

class VideoProject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    
    video_link = models.URLField(max_length=1000)  # YouTube / Facebook link
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_name} - {self.title}"