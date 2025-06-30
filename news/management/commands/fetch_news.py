from django.core.management.base import BaseCommand
from news.models import NewsPost
import feedparser
from datetime import datetime
import uuid
from bs4 import BeautifulSoup
import requests
from newspaper import Article

RSS_SOURCES = [
    {
        "name": "The Guardian Nigeria",
        "website": "https://guardian.ng",
        "rss": "https://guardian.ng/feed",
        "main_category": "World-News",
    },
    {
        "name": "Punch Nigeria – Latest News",
        "website": "https://punchng.com",
        "rss": "https://rss.punchng.com/",
        "main_category": "Local-News",
    },
    
    # Local-News replacement
    {
    "name": "Daily Post Nigeria",
    "website": "https://dailypost.ng",
    "rss": "https://dailypost.ng/feed",
    "main_category": "Local-News",
    },
    # Bonus local-news
    {
    "name": "Legit.ng",
    "website": "https://www.legit.ng",
    "rss": "https://www.legit.ng/rss/all.rss",
    "main_category": "Local-News",
    },
    # Replace Scientific/Nigerian
    {
    "name": "Information Nigeria",
    "website": "https://www.informationng.com",
    "rss": "https://www.informationng.com/feed",
    "main_category": "Scientific",
    },
    # Premium Times category feeds
    {
    "name": "Premium Times Nigeria – News",
    "website": "https://www.premiumtimesng.com",
    "rss": "https://www.premiumtimesng.com/category/news/feed",
    "main_category": "Politics",
    },
    {
    "name": "Premium Times Nigeria – Tech",
    "website": "https://www.premiumtimesng.com",
    "rss": "https://www.premiumtimesng.com/category/technology/feed",
    "main_category": "Technology",
    },

    {
        "name": "Complete Sports Nigeria",
        "website": "https://www.completesports.com",
        "rss": "https://www.completesports.com/feed",
        "main_category": "Sport",
    },
    {
        "name": "Techpoint Africa",
        "website": "https://techpoint.africa",
        "rss": "https://techpoint.africa/feed",
        "main_category": "Technology",
    },
    {
        "name": "Nollywood Reinvented",
        "website": "https://www.nollywoodreinvented.com",
        "rss": "https://www.nollywoodreinvented.com/feed",
        "main_category": "Entertainment",
    },
    {
        "name": "Scientific Nigerian",
        "website": "https://scientificnigerian.com",
        "rss": "https://scientificnigerian.com/feed",
        "main_category": "Scientific",
    },
    {
        "name": "Business Day Nigeria",
        "website": "https://businessday.ng",
        "rss": "https://businessday.ng/feed",
        "main_category": "Business",
    },
    {
        "name": "Premium Times Nigeria",
        "website": "https://www.premiumtimesng.com",
        "rss": "https://www.premiumtimesng.com/feed",
        "main_category": "Politics",
    },
]

class Command(BaseCommand):
    help = "Fetches latest news from RSS feeds using newspaper3k"

    def handle(self, *args, **kwargs):
        for source in RSS_SOURCES:
            feed = feedparser.parse(source["rss"])
            if not feed.entries:
                self.stdout.write(self.style.WARNING(f"No entries found for {source['name']}"))
                continue

            for entry in feed.entries:
                if NewsPost.objects.filter(share_link=entry.link).exists():
                    self.stdout.write(f"⏩ Skipped (duplicate): {entry.link}")
                    continue

                published = entry.get("published", "")
                try:
                    date_obj = datetime.strptime(published[:16], "%a, %d %b %Y")
                except Exception:
                    date_obj = datetime.now()

                # 🔍 Try to fetch full article with newspaper3k
                full_content, top_image = fetch_article_with_newspaper(entry.link)

                # If newspaper3k fails, fallback to RSS content + BeautifulSoup
                if not full_content:
                    content_html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
                    soup = BeautifulSoup(content_html, "html.parser")
                    full_content = soup.get_text(separator="\n").strip()
                    top_image = extract_image(soup)

                # Create the news post
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
