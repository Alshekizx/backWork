from django.contrib import admin
from .models import (
    NewsPost, Comment, Source, CustomUser,
    ContactUs, NewsLetterSubscription,
    VideoProject  # ✅ ADD THIS
)
from django.contrib.auth.admin import UserAdmin


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('header', 'main_category', 'sub_category', 'date', 'source')
    list_filter = ('main_category', 'date')


admin.site.register(Comment)
admin.site.register(Source)
admin.site.register(CustomUser, UserAdmin)


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')


admin.site.register(NewsLetterSubscription)


# 🎥 Video Admin Panel
@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    list_display = ("project_name", "title", "uploaded_at")
    search_fields = ("project_name", "title")
    list_filter = ("uploaded_at",)