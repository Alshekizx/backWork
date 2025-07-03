from rest_framework import generics
from .serializers import NewsPostSerializer, CommentSerializer
from django.db.models.functions import Lower
from .models import Comment, NewsPost
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

# ✅ List all posts, with optional category filtering
class NewsPostListView(generics.ListAPIView):
    serializer_class = NewsPostSerializer

    def get_queryset(self):
        queryset = NewsPost.objects.all().order_by("-date", "-time")
        category = self.request.query_params.get("category")
        if category and category != "All":
            queryset = queryset.annotate(lower_category=Lower("main_category")).filter(lower_category=category.lower())
        return queryset

# ✅ Retrieve a single post by UUID
class NewsPostDetailView(generics.RetrieveAPIView):
    queryset = NewsPost.objects.all()
    serializer_class = NewsPostSerializer
    lookup_field = 'id'

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['date'] = timezone.now().date()
        data['time'] = timezone.now().time()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Link comment to news post
        post = NewsPost.objects.get(id=data['news_post_id'])
        post.comments.add(comment)
        post.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)