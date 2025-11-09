"""
Streamlit 메인 앱: 코인 투자 AI 대시보드
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging

from config import QWEN_MODEL_PATH, USE_LMSTUDIO_API, LM_STUDIO_MODEL_NAME
from models.qwen_local import QwenModel
from data.coinone_api import CoinoneAPI
from config import COINONE_ACCESS_TOKEN, COINONE_SECRET_KEY
from db.database import TradingDatabase
from utils.news_scraper import NewsScraper

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 페이지 설정
st.set_page_config(
    page_title="코인 투자 AI",
    page_icon="₿",
    layout="wide"
)

# 세션 상태 초기화
if "model" not in st.session_state:
    st.session_state.model = None
if "api" not in st.session_state:
    st.session_state.api = None
if "db" not in st.session_state:
    st.session_state.db = None


def init_components():
    """컴포넌트 초기화"""
    if st.session_state.db is None:
        st.session_state.db = TradingDatabase()
    if st.session_state.api is None:
        st.session_state.api = CoinoneAPI()


def main():
    """메인 함수"""
    st.title("₿ 코인 투자 AI")
    st.markdown("---")
    
    init_components()
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 모델 로딩
        if st.button("모델 로드", type="primary"):
            with st.spinner("모델 로딩 중..."):
                try:
                    st.session_state.model = QwenModel(use_lmstudio=USE_LMSTUDIO_API)
                    st.session_state.model.load_model()
                    if USE_LMSTUDIO_API:
                        st.success("LM Studio API 연결 완료!")
                    else:
                        st.success("로컬 모델 로딩 완료!")
                except Exception as e:
                    st.error(f"모델 로딩 실패: {e}")
        
        # API 연결 테스트
        if st.button("API 연결 테스트"):
            try:
                ticker = st.session_state.api.get_ticker("BTC")
                if ticker:
                    st.success("API 연결 성공!")
                else:
                    st.warning("API 연결 실패")
            except Exception as e:
                st.error(f"API 연결 오류: {e}")
    
    # 메인 탭
    tab1, tab2, tab3, tab4 = st.tabs(["📊 대시보드", "💰 거래", "📈 포트폴리오", "🤖 AI 분석"])
    
    # 탭 1: 대시보드
    with tab1:
        st.header("시장 현황")
        
        col1, col2, col3 = st.columns(3)
        
        currencies = ["BTC", "ETH", "XRP"]
        
        for i, currency in enumerate(currencies):
            with col1 if i == 0 else col2 if i == 1 else col3:
                try:
                    ticker = st.session_state.api.get_ticker(currency)
                    if ticker and "last" in ticker:
                        st.metric(
                            label=currency,
                            value=f"{float(ticker['last']):,.0f}원",
                            delta=f"{float(ticker.get('change_rate', 0)) * 100:.2f}%"
                        )
                except Exception as e:
                    st.error(f"{currency} 데이터 로드 실패: {e}")
        
        # 뉴스 섹션
        st.subheader("최근 뉴스")
        if st.button("뉴스 새로고침"):
            with st.spinner("뉴스 수집 중..."):
                scraper = NewsScraper()
                news_list = scraper.get_crypto_news(method="rss", max_results=5)
                
                for news in news_list:
                    with st.expander(news['title']):
                        st.write(news.get('description', ''))
                        st.write(f"출처: {news.get('source', 'Unknown')}")
                        st.write(f"링크: {news.get('url', '')}")
    
    # 탭 2: 거래
    with tab2:
        st.header("매매 주문")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("매수")
            buy_currency = st.selectbox("통화 선택", ["BTC", "ETH", "XRP"], key="buy_currency")
            buy_price = st.number_input("가격 (원)", min_value=0.0, key="buy_price")
            buy_quantity = st.number_input("수량", min_value=0.0, key="buy_quantity")
            
            if st.button("매수 주문", type="primary"):
                try:
                    # 실제 주문은 주석 처리 (테스트용)
                    # result = st.session_state.api.place_order(
                    #     price=int(buy_price),
                    #     qty=buy_quantity,
                    #     currency=buy_currency,
                    #     order_type="bid"
                    # )
                    
                    # 데이터베이스에 기록
                    trade_id = st.session_state.db.add_trade(
                        currency=buy_currency,
                        action="buy",
                        price=buy_price,
                        quantity=buy_quantity,
                        status="pending",
                        notes="Streamlit 앱에서 주문"
                    )
                    st.success(f"매수 주문이 기록되었습니다. (ID: {trade_id})")
                except Exception as e:
                    st.error(f"주문 실패: {e}")
        
        with col2:
            st.subheader("매도")
            sell_currency = st.selectbox("통화 선택", ["BTC", "ETH", "XRP"], key="sell_currency")
            sell_price = st.number_input("가격 (원)", min_value=0.0, key="sell_price")
            sell_quantity = st.number_input("수량", min_value=0.0, key="sell_quantity")
            
            if st.button("매도 주문", type="primary"):
                try:
                    # 실제 주문은 주석 처리 (테스트용)
                    # result = st.session_state.api.place_order(
                    #     price=int(sell_price),
                    #     qty=sell_quantity,
                    #     currency=sell_currency,
                    #     order_type="ask"
                    # )
                    
                    # 데이터베이스에 기록
                    trade_id = st.session_state.db.add_trade(
                        currency=sell_currency,
                        action="sell",
                        price=sell_price,
                        quantity=sell_quantity,
                        status="pending",
                        notes="Streamlit 앱에서 주문"
                    )
                    st.success(f"매도 주문이 기록되었습니다. (ID: {trade_id})")
                except Exception as e:
                    st.error(f"주문 실패: {e}")
        
        # 거래 내역
        st.subheader("거래 내역")
        trades = st.session_state.db.get_trades(limit=50)
        if trades:
            df = pd.DataFrame(trades)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("거래 내역이 없습니다.")
    
    # 탭 3: 포트폴리오
    with tab3:
        st.header("내 포트폴리오")
        
        portfolio = st.session_state.db.get_portfolio()
        if portfolio:
            df = pd.DataFrame(portfolio)
            st.dataframe(df, use_container_width=True)
            
            # 차트
            if len(portfolio) > 0:
                st.subheader("보유 현황")
                chart_data = pd.DataFrame({
                    "통화": [p["currency"] for p in portfolio],
                    "수량": [p["quantity"] for p in portfolio]
                })
                st.bar_chart(chart_data.set_index("통화"))
        else:
            st.info("포트폴리오가 비어있습니다.")
    
    # 탭 4: AI 분석
    with tab4:
        st.header("AI 투자 분석")
        
        if st.session_state.model is None:
            st.warning("먼저 사이드바에서 모델을 로드하세요.")
        else:
            analysis_currency = st.selectbox("분석할 통화", ["BTC", "ETH", "XRP"], key="analysis_currency")
            
            if st.button("AI 분석 실행", type="primary"):
                with st.spinner("AI 분석 중..."):
                    try:
                        # 현재가 가져오기
                        ticker = st.session_state.api.get_ticker(analysis_currency)
                        current_price = ticker.get("last", "N/A") if ticker else "N/A"
                        
                        # 뉴스 수집
                        scraper = NewsScraper()
                        news_list = scraper.get_crypto_news(method="rss", max_results=5)
                        news_text = scraper.format_news_for_ai(news_list)
                        
                        # AI 분석 프롬프트 구성
                        prompt = f"""
당신은 암호화폐 투자 분석가입니다. 다음 정보를 바탕으로 {analysis_currency}에 대한 투자 의견을 제시해주세요.

현재 가격: {current_price}원

{news_text}

분석 요청사항:
1. 현재 시장 상황 분석
2. 기술적 분석
3. 투자 추천 (매수/매도/보유)
4. 이유 설명

분석 결과를 한국어로 작성해주세요.
"""
                        
                        # AI 분석 실행
                        analysis_result = st.session_state.model.generate(
                            prompt=prompt,
                            max_length=1024,
                            temperature=0.7,
                            model_name=LM_STUDIO_MODEL_NAME if USE_LMSTUDIO_API else None
                        )
                        
                        st.subheader("AI 분석 결과")
                        st.write(analysis_result)
                        
                        # 분석 결과 저장
                        st.session_state.db.add_analysis(
                            currency=analysis_currency,
                            analysis_type="ai_analysis",
                            content=analysis_result
                        )
                        
                        st.success("분석 완료 및 저장됨")
                        
                    except Exception as e:
                        st.error(f"AI 분석 실패: {e}")


if __name__ == "__main__":
    main()

