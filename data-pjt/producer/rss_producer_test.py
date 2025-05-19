
import feedparser
import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from scrape_link import get_mk_rss_links

load_dotenv()


# Kafka 브로커 주소
KAFKA_BROKER = "localhost:9092"
# Kafka 토픽 이름
TOPIC = "news"

# Kafka Producer 생성 (value는 JSON 직렬화)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)

# RSS 피드 주소 (매일경제 사회 뉴스 예시)
# RSS_FEED_URL = "https://www.mk.co.kr/rss/50200011/"

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


def process_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        try:
            title = entry.title
            link = entry.link
            pub_date = entry.get('published_parsed')
            pub_date = datetime(*pub_date[:6]) if pub_date else datetime.now()
            category = entry.get("category", "기타")
            content, writer = extract_article_text(link)

            news_data = {
                "title": title,
                "link": link,
                "write_date": str(pub_date),
                "category": category,
                "content": content,
                "writer": writer
            }

            # Kafka 전송
            producer.send(TOPIC, news_data)
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sent: {title}")

            time.sleep(1)  # 뉴스 간격 조절 (1초 간격)

        except Exception as e:
            print(f"[송신 실패] {e}")


def main():
    rss_links = get_mk_rss_links()
    print(f"[총 {len(rss_links)}개 피드 수집 시작]")
    for url in rss_links:
        print(f"\n--- {url} 처리 중 ---")
        process_rss_feed(url)


if __name__ == "__main__":
    main()