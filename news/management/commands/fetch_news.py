import feedparser
import uuid
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from newspaper import Article
from django.core.management.base import BaseCommand
from news.models import NewsPost

RSS_SOURCES = [
    {
        "name": "Vision FM – Science & Technology",
        "website": "https://visionfm.ng",
        "rss": "https://visionfm.ng/rss/category/science-technology",
        "main_category": "Scientific",
    },
    {
        "name": "Africanews – World News",
        "website": "https://www.africanews.com",
        "rss": "https://www.africanews.com/feed/latest",  # world category
        "main_category": "World-News",
    },
    {
        "name": "Techpoint Africa – Tech",
        "website": "https://techpoint.africa",
        "rss": "https://techpoint.africa/feed",
        "main_category": "Technology",
    },
    {
        "name": "Nairametrics – Business",
        "website": "https://nairametrics.com",
        "rss": "https://nairametrics.com/feed",
        "main_category": "Business",
    },
    {
        "name": "Vision FM – Sports",
        "website": "https://visionfm.ng",
        "rss": "https://visionfm.ng/rss/category/sports",
        "main_category": "Sport",
    },
    {
        "name": "Fresh News Nigeria – Local News",
        "website": "https://home.freshnewsng.com",
        "rss": "https://home.freshnewsng.com/rss/category/latest-posts",
        "main_category": "Local-News",
    },
    {
        "name": "Punch Nigeria – Politics",
        "website": "https://punchng.com",
        "rss": "https://rss.punchng.com/v1/category/politics",
        "main_category": "Politics",
    },
    {
        "name": "Nollywood Reinvented – Entertainment",
        "website": "https://www.nollywoodreinvented.com",
        "rss": "https://www.nollywoodreinvented.com/feed",
        "main_category": "Entertainment",
    },
]

def fetch_article_with_newspaper(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip(), article.top_image or "/image/default1.jpg"
    except Exception as e:
        print(f"⚠️ newspaper3k failed: {url}\n{e}")
        return "", "/image/default1.jpg"

def extract_image(soup):
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"]

    tw = soup.find("meta", property="twitter:image")
    if tw and tw.get("content"):
        return tw["content"]

    return "/image/default1.jpg"

class Command(BaseCommand):
    help = "Fetches latest news from RSS feeds using newspaper3k"

   
    def handle(self, *args, **kwargs):
        for source in RSS_SOURCES:
            feed = feedparser.parse(source["rss"])
            if not feed.entries:
                self.stdout.write(self.style.WARNING(f"No entries found for {source['name']}"))
                continue

            cutoff = datetime.now() - timedelta(days=1)

            for entry in feed.entries:  # <- move the next lines INSIDE this loop
                published_parsed = getattr(entry, 'published_parsed', None)
                if not published_parsed:
                    continue
                published_dt = datetime.fromtimestamp(time.mktime(published_parsed))
                if published_dt < cutoff:
                    self.stdout.write(f"⏭️ Skipped old post: {entry.link}")
                    continue

                if NewsPost.objects.filter(share_link=entry.link).exists():
                    self.stdout.write(f"⏩ Skipped (duplicate): {entry.link}")
                    continue

                # ✅ Try to get date info
                published = entry.get("published", "")
                try:
                    date_obj = datetime.strptime(published[:16], "%a, %d %b %Y")
                except Exception:
                    date_obj = published_dt

                # ✅ Fetch content & image
                full_content, top_image = fetch_article_with_newspaper(entry.link)

                if not full_content:
                    content_html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
                    soup = BeautifulSoup(content_html, "html.parser")
                    full_content = soup.get_text(separator="\n").strip()
                    top_image = extract_image(soup)

                # ✅ Create NewsPost
                NewsPost.objects.create(
                    id=uuid.uuid4(),
                    header=entry.title,
                    content=full_content[:5000],
                    date=date_obj.date(),
                    time=date_obj.time(),
                    source=source["name"],
                    image=top_image or "/image/default1.jpg",
                    share_link=entry.link,
                    main_category=source["main_category"],
                    sub_category="",
                    views=0,
                )

                self.stdout.write(self.style.SUCCESS(f"✓ Fetched: {entry.title[:60]}"))

        
        try:
            article = Article(entry.link)  
            article.download()
            article.parse()
            return article.text.strip(), article.top_image or "/image/default1.jpg"
        except Exception as e:
            print(f"⚠️ newspaper3k failed: {entry.link}\n{e}")
            return "", "/image/default1.jpg"
