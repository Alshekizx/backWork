# news/management/commands/fetch_news.py
from news.models import NewsPost, NewsSource
from datetime import datetime, timedelta
import feedparser, time, uuid
from bs4 import BeautifulSoup
from newspaper import Article
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Fetches latest news from RSS feeds using DB-configured categories & sources"

    def handle(self, *args, **kwargs):
        sources = NewsSource.objects.select_related("main_category").all()
        cutoff = datetime.now() - timedelta(days=1)

        for source in sources:
            expected_keywords = source.main_category.keyword_list()
            feed = feedparser.parse(source.rss)

            if not feed.entries:
                self.stdout.write(self.style.WARNING(
                    f"No entries for {source.name} ({source.rss})"
                ))
                continue

            for entry in feed.entries:
                if not any(keyword in entry.title.lower() for keyword in expected_keywords):
                    self.stdout.write(f"⏭️ Skipped unrelated: {entry.title}")
                    continue

                published_parsed = getattr(entry, "published_parsed", None)
                if not published_parsed:
                    continue
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                if published_dt < cutoff:
                    continue

                if NewsPost.objects.filter(share_link=entry.link).exists():
                    self.stdout.write(f"⏩ Skipped duplicate: {entry.link}")
                    continue

                # ✅ Fetch content
                content, image = self.fetch_article(entry.link, entry)

                NewsPost.objects.create(
                    id=uuid.uuid4(),
                    header=entry.title,
                    content=content[:5000],
                    date=published_dt.date(),
                    time=published_dt.time(),
                    source=source.name,
                    image=image,
                    share_link=entry.link,
                    main_category=source.main_category.name,
                    sub_category="",
                )
                self.stdout.write(self.style.SUCCESS(f"✓ Added: {entry.title[:60]}"))

    def fetch_article(self, url, entry):
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text.strip(), article.top_image or "/image/default1.jpg"
        except Exception:
            content_html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
            soup = BeautifulSoup(content_html, "html.parser")
            text = soup.get_text(separator="\n").strip()
            image = self.extract_image(soup)
            return text, image

    def extract_image(self, soup):
        for attr in ["img[src]", "meta[property='og:image']", "meta[property='twitter:image']"]:
            tag = soup.select_one(attr)
            if tag:
                return tag.get("src") or tag.get("content")
        return "/image/default1.jpg"
