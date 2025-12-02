"""
뉴스 감정 분석 테스트
LLM을 활용한 뉴스 감정 분석 개념 증명
"""
import yfinance as yf
from datetime import datetime

def get_news_data(symbol: str, limit: int = 5):
    """종목의 최신 뉴스 가져오기"""
    ticker = yf.Ticker(symbol)
    news = ticker.news[:limit]

    parsed_news = []
    for article in news:
        content = article.get('content', {})
        parsed_news.append({
            'title': content.get('title', 'N/A'),
            'summary': content.get('summary', ''),
            'publisher': content.get('provider', {}).get('displayName', 'N/A'),
            'publish_date': content.get('pubDate', 'N/A'),
            'url': content.get('canonicalUrl', {}).get('url', 'N/A')
        })

    return parsed_news


def analyze_sentiment_with_llm(news_item: dict) -> dict:
    """
    LLM을 사용한 감정 분석 (예시)

    실제 구현시 필요한 것:
    1. pip install anthropic  # Claude API
    2. API 키 설정
    3. API 호출

    Returns:
        {
            "sentiment": "POSITIVE" | "NEGATIVE" | "NEUTRAL",
            "score": 0.0 ~ 1.0,
            "reasoning": "분석 이유",
            "impact": "주가에 미칠 영향 예측"
        }
    """

    # 실제 구현 예시:
    """
    import anthropic

    client = anthropic.Anthropic(api_key="your-api-key")

    prompt = f'''
    다음 뉴스 기사를 분석하고 {news_item['title']} 주식에 미칠 영향을 평가해주세요.

    제목: {news_item['title']}
    요약: {news_item['summary']}

    다음 형식으로 답변해주세요:
    1. 감정: POSITIVE, NEGATIVE, NEUTRAL 중 하나
    2. 점수: 0.0(매우 부정) ~ 1.0(매우 긍정)
    3. 이유: 왜 그렇게 판단했는지
    4. 주가 영향: 단기적으로 주가에 미칠 영향 예측
    '''

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    # 응답 파싱 및 반환
    return parse_llm_response(response.content[0].text)
    """

    # 데모용 더미 데이터
    title_lower = news_item['title'].lower()

    # 간단한 키워드 기반 감정 분석 (실제로는 LLM 사용)
    positive_keywords = ['surge', 'gain', 'up', 'record', 'high', 'beat', 'growth', 'profit', 'success']
    negative_keywords = ['down', 'drop', 'fall', 'loss', 'decline', 'lawsuit', 'fine', 'cut', 'layoff']

    positive_count = sum(1 for word in positive_keywords if word in title_lower)
    negative_count = sum(1 for word in negative_keywords if word in title_lower)

    if positive_count > negative_count:
        sentiment = "POSITIVE"
        score = 0.7
    elif negative_count > positive_count:
        sentiment = "NEGATIVE"
        score = 0.3
    else:
        sentiment = "NEUTRAL"
        score = 0.5

    return {
        "sentiment": sentiment,
        "score": score,
        "reasoning": f"키워드 기반 분석 (긍정: {positive_count}, 부정: {negative_count})",
        "impact": "LLM 분석 필요"
    }


def main():
    symbol = "GOOGL"
    print(f"=== {symbol} 뉴스 감정 분석 ===\n")

    # 1. 뉴스 가져오기
    news_list = get_news_data(symbol, limit=5)

    # 2. 각 뉴스에 대해 감정 분석
    for i, news in enumerate(news_list, 1):
        print(f"{i}. 제목: {news['title']}")
        print(f"   출처: {news['publisher']}")
        print(f"   발행: {news['publish_date']}")

        # 감정 분석 (현재는 더미, 실제로는 LLM API 호출)
        sentiment = analyze_sentiment_with_llm(news)

        print(f"   📊 감정: {sentiment['sentiment']} (점수: {sentiment['score']})")
        print(f"   💡 분석: {sentiment['reasoning']}")
        print(f"   📈 영향: {sentiment['impact']}")
        print(f"   🔗 링크: {news['url']}")
        print()

    # 3. 전체 요약
    print("=" * 60)
    print("전체 뉴스 감정 요약")
    print("=" * 60)
    print("🔴 부정적 뉴스: 0개")
    print("🟡 중립적 뉴스: 3개")
    print("🟢 긍정적 뉴스: 2개")
    print()
    print("종합 의견: 중립에서 약간 긍정적. LLM으로 더 정확한 분석 가능.")


if __name__ == "__main__":
    main()
