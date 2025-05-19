import requests
from bs4 import BeautifulSoup

def get_mk_rss_links():
    """
    매일경제 RSS 페이지에서 모든 RSS 피드 링크를 추출하여 리스트로 반환합니다.
    
    Returns:
        List[str]: 추출된 RSS 링크들의 리스트
    """
    url = "https://www.mk.co.kr/rss"
    try:
        response = requests.get(url)
        response.encoding = "utf-8"  # 또는 "euc-kr" 필요 시
        soup = BeautifulSoup(response.text, "html.parser")

        rss_links = []
        for a in soup.find_all("a", class_="rss_link"):
            link = a.get("href", "").strip()
            if link.startswith("http"):
                rss_links.append(link)
        return rss_links

    except Exception as e:
        print(f"[에러] RSS 링크 추출 중 오류 발생: {e}")
        return []
