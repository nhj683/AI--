# 코인 투자 AI

암호화폐 투자를 위한 AI 기반 분석 및 자동매매 시스템

## 프로젝트 구조

```
coin_invest_ai/
├── app.py               # Streamlit 메인 앱
├── config.py            # API 키, 모델 경로 등
├── models/              # Qwen 모델 로딩
│   └── qwen_local.py
├── data/
│   └── coinone_api.py   # 코인원 API 연동
├── db/
│   └── database.py      # SQLite 매매 기록 DB
├── utils/
│   └── news_scraper.py  # 뉴스 수집 (옵션: 뉴스 API 또는 RSS)
├── requirements.txt
└── README.md
```

## 기능

- 📊 실시간 암호화폐 시장 현황 대시보드
- 💰 코인원 API를 통한 매매 주문
- 📈 포트폴리오 관리 및 거래 내역 기록
- 🤖 Qwen AI 모델을 활용한 투자 분석
- 📰 암호화폐 뉴스 수집 및 분석

## 설치 방법

1. 저장소 클론 또는 다운로드

2. 가상 환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. Qwen 모델 다운로드
   - Hugging Face에서 Qwen 모델을 다운로드하여 `models/` 디렉토리에 저장
   - 또는 `config.py`에서 모델 경로 설정

5. 환경 변수 설정
   - `.env` 파일 생성 또는 환경 변수 설정:
   ```bash
   export COINONE_API_KEY="your_api_key"
   export COINONE_SECRET_KEY="your_secret_key"
   export QWEN_MODEL_PATH="./models/qwen2.5-7b-instruct"
   export NEWS_API_KEY="your_news_api_key"  # 선택사항
   ```

## 사용 방법

1. Streamlit 앱 실행
```bash
streamlit run app.py
```

2. 웹 브라우저에서 `http://localhost:8501` 접속

3. 사이드바에서 모델 로드 및 API 연결 테스트

4. 각 탭에서 기능 사용:
   - **대시보드**: 시장 현황 및 뉴스 확인
   - **거래**: 매수/매도 주문
   - **포트폴리오**: 보유 현황 확인
   - **AI 분석**: AI 기반 투자 분석

## 설정

### config.py
- API 키 및 모델 경로 설정
- 데이터베이스 경로 설정
- 뉴스 API 및 RSS 피드 URL 설정

### 코인원 API
1. [코인원](https://coinone.co.kr) 계정 생성
2. API 키 발급
3. `config.py` 또는 환경 변수에 API 키 설정

## 주의사항

- 실제 거래 전에 충분한 테스트를 진행하세요
- API 키는 안전하게 관리하세요
- 투자 결정은 본인의 판단에 따라 신중하게 내리세요
- 이 도구는 투자 조언이 아닌 정보 제공 목적입니다

## 라이선스

MIT License

## 기여

이슈 및 풀 리퀘스트를 환영합니다!

