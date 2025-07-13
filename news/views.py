from rest_framework import generics
from .serializers import NewsPostSerializer, CommentSerializer
from django.db.models.functions import Lower
from .models import Comment, NewsPost
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.db import transaction

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
class NewsPostDetailView(generics.RetrieveAPIView):
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
