import feedparser
import uuid
import time
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from newspaper import Article
from django.core.management.base import BaseCommand
from news.models import NewsPost

CATEGORY_KEYWORDS = {
    "Scientific": ["science", "tech", "space", "research", "climate", "innovation", "biology", "physics"],
    "World-News": ["world", "global", "UN", "diplomacy", "conflict", "war", "international", "border"],
    "Technology": ["tech", "startup", "ai", "software", "hardware", "cloud", "cybersecurity", "blockchain", "robotics"],
    "Business": ["finance", "economy", "business", "market", "stock", "investment", "banking", "crypto", "trade", "entrepreneurship"],
    "Sport": ["sport", "football", "soccer", "tennis", "athletics", "basketball", "fifa", "uefa", "olympics"],
    "Politics": ["politics", "election", "government", "parliament", "senate", "policy", "lawmaker", "campaign", "vote"],
    "Entertainment": ["entertainment", "movie", "music", "nollywood", "actor", "celebrity", "award", "drama", "comedy", "festival"],
    "Local-News": ["local", "nigeria", "abuja", "lagos", "state", "community", "governor", "council", "townhall"],
}


RSS_SOURCES = [
    # 🌍 World News
    {
        "name": "BBC World News",
        "website": "https://www.bbc.com",
        "rss": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "main_category": "World-News",
    },
    {
        "name": "Reuters World News",
        "website": "https://www.reuters.com",
        "rss": "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
        "main_category": "World-News",
    },
    {
        "name": "Africanews – World News",
        "website": "https://www.africanews.com",
        "rss": "https://www.africanews.com/feed/latest",
        "main_category": "World-News",
    },

    # 💻 Technology
    {
        "name": "TechCrunch",
        "website": "https://techcrunch.com",
        "rss": "https://techcrunch.com/feed/",
        "main_category": "Technology",
    },
    {
        "name": "The Verge Technology",
        "website": "https://www.theverge.com",
        "rss": "https://www.theverge.com/rss/index.xml",
        "main_category": "Technology",
    },
    {
        "name": "Techpoint Africa",
        "website": "https://techpoint.africa",
        "rss": "https://techpoint.africa/feed",
        "main_category": "Technology",
    },

    # 🔬 Scientific
    {
        "name": "Scientific American",
        "website": "https://www.scientificamerican.com",
        "rss": "https://www.scientificamerican.com/feed/rss/",
        "main_category": "Scientific",
    },
    {
        "name": "Nature News",
        "website": "https://www.nature.com",
        "rss": "https://www.nature.com/subjects/news.rss",
        "main_category": "Scientific",
    },

    # 💵 Business
    {
        "name": "Nairametrics",
        "website": "https://nairametrics.com",
        "rss": "https://nairametrics.com/feed",
        "main_category": "Business",
    },
    {
        "name": "Business Insider",
        "website": "https://www.businessinsider.com",
        "rss": "https://www.businessinsider.com/rss",
        "main_category": "Business",
    },
    {
        "name": "Bloomberg ETFs",
        "website": "https://www.bloomberg.com",
        "rss": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
        "main_category": "Business",
    },

    # ⚽ Sports
    {
        "name": "BBC Sport",
        "website": "https://www.bbc.com/sport",
        "rss": "http://feeds.bbci.co.uk/sport/rss.xml",
        "main_category": "Sport",
    },
    {
        "name": "ESPN News",
        "website": "https://www.espn.com",
        "rss": "https://www.espn.com/espn/rss/news",
        "main_category": "Sport",
    },
    {
        "name": "Vision FM – Sports",
        "website": "https://visionfm.ng",
        "rss": "https://visionfm.ng/rss/category/sports",
        "main_category": "Sport",
    },

    # 🏛️ Politics
    {
        "name": "Reuters Politics",
        "website": "https://www.reuters.com",
        "rss": "https://www.reutersagency.com/feed/?best-topics=politics&post_type=best",
        "main_category": "Politics",
    },
    {
        "name": "Punch Nigeria – Politics",
        "website": "https://punchng.com",
        "rss": "https://rss.punchng.com/v1/category/politics",
        "main_category": "Politics",
    },

    # 🎬 Entertainment
    {
        "name": "Variety",
        "website": "https://variety.com",
        "rss": "https://variety.com/feed/",
        "main_category": "Entertainment",
    },
    {
        "name": "Hollywood Reporter",
        "website": "https://www.hollywoodreporter.com",
        "rss": "https://www.hollywoodreporter.com/c/rss-feed/",
        "main_category": "Entertainment",
    },
    {
        "name": "Nollywood Reinvented",
        "website": "https://www.nollywoodreinvented.com",
        "rss": "https://www.nollywoodreinvented.com/feed",
        "main_category": "Entertainment",
    },

    # 🏠 Local News (Nigeria)
    {
        "name": "Guardian Nigeria",
        "website": "https://guardian.ng",
        "rss": "https://guardian.ng/feed/",
        "main_category": "Local-News",
    },
    {
        "name": "Vanguard Nigeria",
        "website": "https://www.vanguardngr.com",
        "rss": "https://www.vanguardngr.com/feed/",
        "main_category": "Local-News",
    },
    {
        "name": "Fresh News Nigeria – Local News",
        "website": "https://home.freshnewsng.com",
        "rss": "https://home.freshnewsng.com/rss/category/latest-posts",
        "main_category": "Local-News",
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
            expected_keywords = CATEGORY_KEYWORDS[source["main_category"]]
            feed = feedparser.parse(source["rss"])

            if not feed.entries:
                self.stdout.write(self.style.WARNING(
                    f"No entries found for {source['name']} (URL: {source['rss']})"
                ))
                continue

            cutoff = datetime.now() - timedelta(days=1)

            for entry in feed.entries:
                if not any(keyword.lower() in entry.title.lower() for keyword in expected_keywords):
                    self.stdout.write(f"⏭️ Skipped unrelated article: {entry.title}")
                    continue

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

                published = entry.get("published", "")
                try:
                    date_obj = datetime.strptime(published[:16], "%a, %d %b %Y")
                except Exception:
                    date_obj = published_dt

                full_content, top_image = fetch_article_with_newspaper(entry.link)

                if not full_content:
                    content_html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
                    soup = BeautifulSoup(content_html, "html.parser")
                    full_content = soup.get_text(separator="\n").strip()
                    top_image = extract_image(soup)

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

