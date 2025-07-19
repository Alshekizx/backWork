from rest_framework import serializers
from .models import Advertisement, EmployeeAccount, ManagerAccount, NewsPost, Comment, CustomUser
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .constants import MAIN_CATEGORIES
from .models import ManagerAccount, EmployeeAccount
from django.contrib.auth.hashers import make_password

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
        
class ManagerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerAccount
        fields = '__all__'

class EmployeeAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAccount
        fields = '__all__'
class ManagerSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ManagerAccount
        fields = [
            'employee_id', 'first_name', 'last_name',
            'email', 'date_of_birth', 'profile_image', 'password'
        ]

    def create(self, validated_data):
        # Create the associated CustomUser
        user = CustomUser.objects.create_user(
            username=validated_data['employee_id'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=f"{validated_data['first_name']} {validated_data['last_name']}",
            hashed_pw=make_password(validated_data['password'])
        )

        # Create ManagerAccount
        manager = ManagerAccount.objects.create(
            user=user,
            employee_id=validated_data['employee_id'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            date_of_birth=validated_data['date_of_birth'],
            profile_image=validated_data.get('profile_image'),
            password=validated_data['password'],  # hashed manually if needed
            hashed_pw=make_password(validated_data['password'])
        )

        return manager
class LoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField()