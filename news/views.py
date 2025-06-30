from rest_framework import generics
from .models import NewsPost
from .serializers import NewsPostSerializer
from django.db.models.functions import Lower

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
