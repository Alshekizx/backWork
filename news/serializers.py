from rest_framework import serializers
from .models import NewsPost, Comment

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
