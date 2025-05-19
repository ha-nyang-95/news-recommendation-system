from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한  (5000 토큰)
    토큰 수를 제한하여 처리 효율성 확보
    """
    import tiktoken

    if not content:
        return ""
        
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)
    
    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)
    
    return content


def transform_extract_keywords(text):
    """
    텍스트 데이터 변환 - 키워드 5개 추출  
    입력 텍스트에서 핵심 키워드를 추출하는 변환 로직
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 뉴스 콘텐츠를 분석하여 핵심 키워드 5개를 추출하는 역할을 합니다. 키워드는 명사 중심으로 추출하고, 쉼표로 구분하여 출력해주세요. 예: 경제, 부동산, 금리, 투자, 서울"}, # 해당 위치에서 키워드 5개를 추출할 수 있도록 프롬프트 작성성
            {"role": "user", "content": text}
        ],
        max_tokens=100
    )
    keywords = response.choices[0].message.content.strip()
    return [kw.strip() for kw in keywords.split(',') if kw.strip()]


def transform_to_embedding(text: str) -> list[float]:
    """
    텍스트 데이터 변환 - 벡터 임베딩  
    텍스트를 수치형 벡터로 변환하는 변환 로직
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def transform_classify_category(content):
    content = preprocess_content(content)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": """
            다음 뉴스 본문의 주제를 기반으로 가장 알맞은 카테고리를 아래 항목 중 하나로 분류하세요.
            정확히 하나만 선택해서 출력하세요 (텍스트만 출력).
            [IT_과학, 건강, 경제, 교육, 국제, 라이프스타일, 문화, 사건사고, 사회일반, 산업, 스포츠, 여성복지, 여행레저, 연예, 정치, 지역, 취미]
            """},
            {"role": "user", "content": content}
        ],
        max_tokens=10
    )

    model_output = response.choices[0].message.content.strip()


    if model_output not in ["IT_과학", "건강", "경제", "교육", "국제", "라이프스타일", "문화", "사건사고", "사회일반", "산업", "스포츠", "여성복지", "여행레저", "연예", "정치", "지역", "취미"]:
        model_output = "미분류"

    return model_output
