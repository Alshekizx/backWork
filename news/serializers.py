from rest_framework import serializers
from .models import NewsPost, Comment, CustomUser
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer

# Your category choices for validation
MAIN_CATEGORIES = [
    "World-News", "Local-News", "Sport",
    "Technology", "Entertainment", "Scientific",
    "Business", "Politics",
]

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    # Explicitly define notification_preferences to accept list from JSON
    notification_preferences = serializers.ListField(
        child=serializers.ChoiceField(choices=MAIN_CATEGORIES),
        required=False
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password',
            'full_name', 'profile_picture', 'notification_preferences',
            'subscribe_newsletter', 'date_of_birth',
        )
        
class CustomUserSerializer(BaseUserSerializer):
    notification_preferences = serializers.ListField(
        child=serializers.ChoiceField(choices=MAIN_CATEGORIES),
        required=False
    )

    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password',
            'full_name', 'profile_picture', 'notification_preferences',
            'subscribe_newsletter', 'date_of_birth',
        )

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        

class NewsPostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    shareLink = serializers.URLField(source="share_link")

    class Meta:
        model = NewsPost
        fields = '__all__'
