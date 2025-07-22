from .serializers import AdminAccountSerializer, AdvertisementSerializer, CustomUserSerializer, NewsPostSerializer, CommentSerializer

from .models import AdminAccount, Advertisement, CustomUser, NewsPost,NewsPost, Advertisement
from rest_framework.response import Response
from rest_framework import status,generics
from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.permissions import BasePermission,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .serializers import LoginSerializer
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta

from news import models
import traceback
import logging



# ✅ List all posts, with optional search, category, date filtering
class NewsPostListView(generics.ListCreateAPIView):
    serializer_class = NewsPostSerializer
    queryset = NewsPost.objects.all().order_by("-date", "-time")

    def get_queryset(self):
        queryset = super().get_queryset()

        category = self.request.query_params.get("category")
        date = self.request.query_params.get("date")
        search = self.request.query_params.get("search")

        if category and category != "All":
            queryset = queryset.filter(main_category__iexact=category)
        if date:
            queryset = queryset.filter(date=date)
        if search:
            queryset = queryset.filter(header__icontains=search)

        return queryset

# ✅ Retrieve a single post by UUID
class NewsPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NewsPost.objects.all()
    serializer_class = NewsPostSerializer
    lookup_field = 'id'


# ✅ Comment creation
class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['date'] = timezone.now().date()
        data['time'] = timezone.now().time()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        post = get_object_or_404(NewsPost, id=data.get('news_post_id'))
        post.comments.add(comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ✅ Top News assignment
@transaction.atomic
def assign_top_news(news_post, priority):
    if not (1 <= priority <= 20):
        raise ValueError("Priority must be between 1 and 20.")

    # Fetch all top news ordered by priority
    top_news = NewsPost.objects.filter(is_top_news=True).exclude(pk=news_post.pk).order_by('top_news_priority')

    # Shift priorities if there's a conflict
    priorities_to_shift = top_news.filter(top_news_priority__gte=priority)
    for post in reversed(priorities_to_shift):
        if post.top_news_priority >= 20:
            post.is_top_news = False
            post.top_news_priority = None
        else:
            post.top_news_priority += 1
        post.save()

    # Assign new priority to target post
    news_post.is_top_news = True
    news_post.top_news_priority = priority
    news_post.save()

@api_view(['GET'])
def list_top_news(request):
    top_news = NewsPost.objects.filter(is_top_news=True).order_by('top_news_priority')
    serializer = NewsPostSerializer(top_news, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def set_top_news(request):
    news_id = request.data.get('news_id')
    priority = request.data.get('priority')

    try:
        news_post = NewsPost.objects.get(pk=news_id)
        assign_top_news(news_post, int(priority))
        return Response({'message': 'Top News Updated Successfully'})
    except NewsPost.DoesNotExist:
        return Response({'error': 'News Post Not Found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ✅ Auto-assign top news (optional)
def auto_assign_top_news(news_post):
    existing_priorities = list(
        NewsPost.objects.filter(is_top_news=True).values_list('top_news_priority', flat=True)
    )
    available_priorities = [i for i in range(1, 21) if i not in existing_priorities]

    if not available_priorities:
        lowest = NewsPost.objects.filter(is_top_news=True).order_by('-top_news_priority').first()
        lowest.is_top_news = False
        lowest.top_news_priority = None
        lowest.save()
        available_priorities = [20]

    assign_top_news(news_post, min(available_priorities))
 
    
@transaction.atomic
def assign_trending_news(news_post, priority):
    if not (1 <= priority <= 30):
        raise ValueError("Priority must be between 1 and 30.")

    # Fetch all trending news ordered by priority
    trending_news = NewsPost.objects.filter(is_trending=True).exclude(pk=news_post.pk).order_by('trending_priority')

    # Shift priorities if conflict
    priorities_to_shift = trending_news.filter(trending_priority__gte=priority)
    for post in reversed(priorities_to_shift):
        if post.trending_priority >= 30:
            post.is_trending = False
            post.trending_priority = None
        else:
            post.trending_priority += 1
        post.save()

    # Assign priority to target post
    news_post.is_trending = True
    news_post.trending_priority = priority
    news_post.save()

@api_view(['GET'])
def list_trending_news(request):
    trending_news = NewsPost.objects.filter(is_trending=True).order_by('trending_priority')
    serializer = NewsPostSerializer(trending_news, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def set_trending_news(request):
    news_id = request.data.get('news_id')
    priority = request.data.get('priority')

    try:
        news_post = NewsPost.objects.get(pk=news_id)
        assign_trending_news(news_post, int(priority))
        return Response({'message': 'Trending News Updated Successfully'})
    except NewsPost.DoesNotExist:
        return Response({'error': 'News Post Not Found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def auto_assign_trending_news(news_post):
    existing_priorities = list(
        NewsPost.objects.filter(is_trending=True).values_list('trending_priority', flat=True)
    )
    available_priorities = [i for i in range(1, 31) if i not in existing_priorities]

    if not available_priorities:
        # Remove lowest priority if full
        lowest = NewsPost.objects.filter(is_trending=True).order_by('-trending_priority').first()
        lowest.is_trending = False
        lowest.trending_priority = None
        lowest.save()
        available_priorities = [30]

    assign_trending_news(news_post, min(available_priorities))

class AdvertisementListView(generics.ListAPIView):
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        queryset = Advertisement.objects.filter(is_active=True)
        ad_space = self.request.query_params.get('space')
        today = timezone.now().date()
        queryset = queryset.filter(start_date__lte=today, end_date__gte=today)

        if ad_space:
            queryset = queryset.filter(ad_space=ad_space)

        return queryset.order_by('created_at')

class AdvertisementCreateView(generics.CreateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
  
class AdvertisementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    lookup_field = 'id'

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'account_profile') and request.user.account_profile.user_type == 'manager'

class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'account_profile') and request.user.account_profile.user_type == 'employee'
    
class CreateEmployeeView(generics.CreateAPIView):
    serializer_class = AdminAccountSerializer
    permission_classes = [IsManager]

    def perform_create(self, serializer):
        serializer.save(manager=self.request.user.account_profile, user_type='employee')
        


class UserListView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsManager]
    queryset = CustomUser.objects.all()
    

class AdminSignupView(generics.CreateAPIView):
    serializer_class = AdminAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save user with default type 'admin' unless specified
        user = serializer.save(user_type=request.data.get('user_type', 'admin'))

        # Create or retrieve token
        token, _ = Token.objects.get_or_create(user=user.user)

        return Response({
            'token': token.key,
            'user_id': user.id,
            'name': f"{user.first_name} {user.last_name}",
            'employee_id': user.employee_id,
            'user_type': user.user_type
        }, status=status.HTTP_201_CREATED)


logger = logging.getLogger(__name__)

class AdminLoginView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            employee_id = serializer.validated_data['employee_id']
            password = serializer.validated_data['password']
            user_type = serializer.validated_data['user_type']

            try:
                user = AdminAccount.objects.get(employee_id=employee_id)

                if user.user_type != user_type:
                    return Response({'error': 'Invalid user type'}, status=403)

                if check_password(password, user.password):
                    token, _ = Token.objects.get_or_create(user=user.user)
                    return Response({
                        'token': token.key,
                        'user_id': user.id,
                        'employee_id': user.employee_id,
                        'name': f"{user.first_name} {user.last_name}",
                        'user_type': user.user_type
                    })
                else:
                    return Response({'error': 'Invalid password'}, status=400)

            except AdminAccount.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)

        except Exception as e:
            logger.error("Login error: %s", str(e))
            traceback.print_exc()
            return Response({'error': 'Internal server error', 'detail': str(e)}, status=500)

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'account_profile') and request.user.account_profile.user_type == 'admin'

class AdminListView(generics.ListAPIView):
    serializer_class = AdminAccountSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return AdminAccount.objects.filter(user_type='admin')

class DeleteAdminView(generics.DestroyAPIView):
    serializer_class = AdminAccountSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        return AdminAccount.objects.filter(user_type='admin')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_visit_stats(request, post_id):
    try:
        post = NewsPost.objects.get(id=post_id)
        total_posts = NewsPost.objects.count()
        edited_posts = NewsPost.objects.exclude(updated_by_employee=None).count()
        total_ads = Advertisement.objects.count()
        active_ads = Advertisement.objects.filter(is_active=True).count()

        return Response({
            "totalPosts": total_posts,
            "editedPosts": edited_posts,
            "totalAds": total_ads,
            "activeAds": active_ads,
            'daily_visitors': post.daily_visitors,
            'monthly_visitors': post.monthly_visitors
        })
    except NewsPost.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard_stats(request):
    total_posts = NewsPost.objects.count()
    edited_posts = NewsPost.objects.exclude(updated_by_employee=None).count()
    total_ads = Advertisement.objects.count()
    active_ads = Advertisement.objects.filter(is_active=True).count()

    today = timezone.now().date()
    one_month_ago = today - timedelta(days=30)

    daily_visitors = NewsPost.objects.filter(last_visited=today).aggregate(
        total=Sum("daily_visitors")
    )["total"] or 0

    monthly_visitors = NewsPost.objects.filter(last_visited__gte=one_month_ago).aggregate(
        total=Sum("monthly_visitors")
    )["total"] or 0

    return Response({
        "totalPosts": total_posts,
        "editedPosts": edited_posts,
        "totalAds": total_ads,
        "activeAds": active_ads,
        "dailyVisitors": daily_visitors,
        "monthlyVisitors": monthly_visitors
    })

    

@api_view(["POST"])
def track_blog_visit(request, post_id):
    try:
        post = NewsPost.objects.get(id=post_id)
        post.update_visit_counts()  # Make sure this method exists in your model
        return Response({
            "message": "Visit recorded",
            "daily_visitors": post.daily_visitors,
            "monthly_visitors": post.monthly_visitors
        })
    except NewsPost.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)




