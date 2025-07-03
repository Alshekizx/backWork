from django.contrib import admin
from .models import NewsPost, Comment, Source, CustomUser
from django.contrib.auth.admin import UserAdmin

@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('header', 'main_category', 'sub_category', 'date', 'source')
    list_filter = ('main_category', 'date')

admin.site.register(Comment)
admin.site.register(Source)

admin.site.register(CustomUser, UserAdmin)