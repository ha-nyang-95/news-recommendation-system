import feedparser
import requests
import os
from bs4 import BeautifulSoup
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# PostgreSQL 연결 정보
DB_CONFIG = {
    "dbname": "news",
    "user": os.getenv("DB_USERNAME"),
    "password": os.getenv("DB_PASSWORD"),
    "host": "localhost",
    "port": 5432
}

# RSS 피드 주소 (매일경제 사회 뉴스 예시)
RSS_FEED_URL = "https://www.mk.co.kr/rss/30100041/"

def extract_article_text(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        content = ""
        wrapper = soup.find("div", class_="news_cnt_detail_wrap")
        if wrapper:
            paragraphs = wrapper.find_all("p")
            if paragraphs:
                content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            figcaption = soup.select_one("figure figcaption")
            if figcaption:
                content = figcaption.get_text(strip=True)

        if not content:
            content = "[본문 없음]"

        author_tags = soup.select("dl.author > a")
        writers = [tag.get_text(strip=True) for tag in author_tags]
        writer = ", ".join(writers) if writers else "알 수 없음"

        return content, writer

    except Exception as e:
        print(f"[본문/기자 크롤링 오류] {url} → {e}")
        return "[본문 없음]", "알 수 없음"


def save_article_to_db(title, writer, pub_date, category, content, link):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # 중복 방지
        cur.execute("SELECT 1 FROM news_article WHERE url = %s", (link,))
        if cur.fetchone():
            print(f"[중복] 이미 존재: {title}")
        else:
            cur.execute(
                """
                INSERT INTO news_article 
                (title, writer, write_date, category, content, url, keywords)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    title,
                    writer,
                    pub_date,
                    category,
                    content,
                    link,
                    json.dumps([])  # 키워드 추출 X → 빈 리스트
                )
            )
            conn.commit()
            print(f"[저장 완료] {title}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB 저장 오류] {title} -> {e}")

def main():
    feed = feedparser.parse(RSS_FEED_URL)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        pub_date = entry.get('published_parsed')
        pub_date = datetime(*pub_date[:6]) if pub_date else datetime.now()
        category = entry.get("category", "기타")
        content, writer = extract_article_text(link)
        if content and content != "[본문 없음]":
            save_article_to_db(title, writer, pub_date, category, content, link)

if __name__ == "__main__":
    main()

