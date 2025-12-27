# news/management/commands/fetch_news.py
from news.models import NewsPost
from django.core.management.base import BaseCommand
import uuid
from datetime import datetime

class Command(BaseCommand):
    help = "Placeholder command — RSS fetching removed. This can be used to manually add news if needed."

    def handle(self, *args, **kwargs):
        # Example of manually adding a news post
        news_example = {
            "header": "Sample News Headline",
            "content": "This is a sample news content.",
            "date": datetime.now().date(),
            "time": datetime.now().time(),
            "source": "Manual",
            "image": "/image/default1.jpg",
            "share_link": "https://example.com/sample-news",
            "main_category": "general",
            "sub_category": "",
        }

        NewsPost.objects.create(
            id=uuid.uuid4(),
            **news_example
        )

        self.stdout.write(self.style.SUCCESS("✓ Sample news post added successfully."))
