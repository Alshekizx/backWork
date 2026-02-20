from rest_framework import serializers

from newsapi import settings
from .models import Advertisement, NewsPost, Comment, CustomUser, AdminAccount, ContactUs, NewsLetterSubscription, NewsletterHistory,NewsCategory, NewsSource, CategoryPlacement
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import datetime

class CategoryPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryPlacement
        fields = ["id", "placement", "priority", "main_category"]
        read_only_fields = ["main_category"]

        
class NewsCategorySerializer(serializers.ModelSerializer):
    placements = CategoryPlacementSerializer(many=True, required=False)

    class Meta:
        model = NewsCategory
        fields = ["id", "name", "keywords", "placements"]

    def create(self, validated_data):
        placements_data = validated_data.pop("placements", [])

        # Create the category
        main_category = NewsCategory.objects.create(**validated_data)

        if not placements_data:
            # Auto-generate placement if none is passed
            default_placement_id = main_category.id  # or CategoryPlacement.objects.count() + 1
            CategoryPlacement.objects.create(
                main_category=main_category,
                placement=default_placement_id,
                priority=1  # you can adjust priority logic
            )
        else:
            # If placements are provided, use them
            for placement in placements_data:
                CategoryPlacement.objects.create(main_category=main_category, **placement)

        return main_category

    def update(self, instance, validated_data):
        placements_data = validated_data.pop("placements", [])

        instance.name = validated_data.get("name", instance.name)
        instance.keywords = validated_data.get("keywords", instance.keywords)
        instance.save()

        # Reset placements on update
        instance.placements.all().delete()

        if not placements_data:
            default_placement_id = instance.id
            CategoryPlacement.objects.create(
                main_category=instance,
                placement=default_placement_id,
                priority=1
            )
        else:
            for placement in placements_data:
                CategoryPlacement.objects.create(main_category=instance, **placement)

        return instance


class CustomUserCreateSerializer(BaseUserCreateSerializer):
    # accept IDs for creation
    notification_preferences = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=NewsCategory.objects.all(),
        required=False
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = (
            "id", "username", "email", "password",
            "full_name", "profile_picture",
            "notification_preferences",
            "subscribe_newsletter", "date_of_birth",
        )


class CustomUserSerializer(BaseUserSerializer):
    # return full category details in responses
    notification_preferences = NewsCategorySerializer(many=True, read_only=True)

    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = (
            "id", "username", "email",
            "full_name", "profile_picture",
            "notification_preferences",
            "subscribe_newsletter", "date_of_birth",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class NewsPostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    share_Link = serializers.SerializerMethodField(read_only=True)
    main_category = serializers.SlugRelatedField(
        slug_field="name",
        queryset=NewsCategory.objects.all()
    )

    def get_share_Link(self, obj):
        request = self.context.get('request')
        if request:
            domain = request.build_absolute_uri('/')  # backend-aware domain
        else:
            domain = settings.FRONTEND_DOMAIN         # fallback to constant
        return f"{domain.rstrip('/')}/view/blogDetails/{obj.id}"

    class Meta:
        model = NewsPost
        fields = '__all__'
        read_only_fields = ['share_Link']


class NewsSourceSerializer(serializers.ModelSerializer):
    main_category = serializers.SlugRelatedField(
        slug_field="name",
        queryset=NewsCategory.objects.all()
    )

    class Meta:
        model = NewsSource
        fields = "__all__"

    

class AdvertisementSerializer(serializers.ModelSerializer):
    main_category = serializers.SlugRelatedField(
        slug_field="name",
        queryset=NewsCategory.objects.all()
    )

    class Meta:
        model = Advertisement
        fields = "__all__"



class AdminAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    date_of_birth = serializers.DateField(write_only=True)
    profile_image = serializers.ImageField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)

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
        password = validated_data.pop('password')
        profile_image = validated_data.pop('profile_image', None)
        date_of_birth = validated_data.pop('date_of_birth')
        user_type = validated_data.get('user_type', 'employee')
        manager = validated_data.get('manager')

        def generate_employee_id():
            today = datetime.date.today()
            prefix = f"EMP-{today.strftime('%Y%m%d')}"
            count = AdminAccount.objects.filter(employee_id__startswith=prefix).count() + 1
            return f"{prefix}-{count:04d}"

        # ✅ generate here if employee
        employee_id = validated_data.get('employee_id') or (
            generate_employee_id() if user_type == "employee" else None
        )

        full_name = f"{validated_data['first_name']} {validated_data['last_name']}"

        if CustomUser.objects.filter(username=employee_id).exists():
            raise serializers.ValidationError({"employee_id": "Employee ID already exists"})

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email already exists"})

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

        admin_account = AdminAccount.objects.create(
            user=user,
            employee_id=employee_id,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            date_of_birth=date_of_birth,
            profile_image=profile_image,
            user_type=user_type,
            manager=manager if user_type == 'employee' else None
        )

        return admin_account


class LoginSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    password = serializers.CharField()
    user_type = serializers.ChoiceField(choices=['manager', 'employee'])
    
class VisitStatsSerializer(serializers.Serializer):
    daily_visitors = serializers.IntegerField()
    monthly_visitors = serializers.IntegerField()


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ['id', 'name', 'email', 'message', 'seen','created_at']


class NewsLetterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLetterSubscription
        fields = ['id', 'email', 'date_subscribed']
        
class NewsletterHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterHistory
        fields = ['id', 'subject', 'sent_at', 'recipients']


class VideoProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProject
        fields = "__all__"