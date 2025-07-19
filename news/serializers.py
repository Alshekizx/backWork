from rest_framework import serializers
from .models import Advertisement, NewsPost, Comment, CustomUser, AdminAccount
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .constants import MAIN_CATEGORIES
from django.contrib.auth.hashers import make_password


class CustomUserCreateSerializer(BaseUserCreateSerializer):
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
    share_Link = serializers.SerializerMethodField(read_only=True)

    def get_share_Link(self, obj):
        return obj.share_link

    class Meta:
        model = NewsPost
        fields = '__all__'
        read_only_fields = ['share_Link']


class AdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'


class AdminAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    profile_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = AdminAccount
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'password',
            'email', 'date_of_birth', 'profile_image', 'user_type', 'manager'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        email = validated_data.pop('email')
        employee_id = validated_data['employee_id']
        full_name = f"{validated_data['first_name']} {validated_data['last_name']}"
        password = validated_data.pop('password')
        profile_image = validated_data.pop('profile_image', None)
        date_of_birth = validated_data.pop('date_of_birth')
        user_type = validated_data.get('user_type', 'employee')
        manager = validated_data.get('manager')  # Optional

        # Create the user
        user = CustomUser.objects.create_user(
            username=employee_id,
            email=email,
            password=password,
            full_name=full_name,
            date_of_birth=date_of_birth,
        )

        if profile_image:
            user.profile_picture = profile_image
            user.save()

        # Create admin account
        admin_account = AdminAccount.objects.create(
            user=user,
            employee_id=employee_id,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            date_of_birth=date_of_birth,
            profile_image=profile_image,
            user_type=user_type,
            manager=manager if user_type == 'employee' else None  # Only employees have managers
        )

        return admin_account


class LoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField()
    
class VisitStatsSerializer(serializers.Serializer):
    daily_visitors = serializers.IntegerField()
    monthly_visitors = serializers.IntegerField()
