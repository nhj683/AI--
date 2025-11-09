"""
설정 파일: API 키, 모델 경로 등의 환경 변수 관리
"""

import os
from pathlib import Path 

# 프로젝트 루트 디렉토리
ROOT_DIR = Path(__file__).parent

# 코인원 API 설정 (환경 변수에서 로드 또는 직접 설정)
# 환경 변수로 설정하거나 아래에 직접 값을 입력하세요
# Access Token: 코인원에서 발급받은 Access Token
# Secret Key: 코인원에서 발급받은 Secret Key
COINONE_ACCESS_TOKEN = os.getenv("COINONE_ACCESS_TOKEN", "d6bead1d-6b3e-4f64-b88b-15e66969f2d2")
COINONE_SECRET_KEY = os.getenv("COINONE_SECRET_KEY", "78df0684-d7a8-4044-882b-e7e3652505bf")

# Qwen 모델 경로 (로컬 모델 사용 시)
QWEN_MODEL_PATH = os.getenv("QWEN_MODEL_PATH", "/Users/eddie/.lmstudio/hub/models/qwen/qwen3-vl-8b")

# LM Studio API 설정
USE_LMSTUDIO_API = os.getenv("USE_LMSTUDIO_API", "true").lower() == "true"
LM_STUDIO_API_URL = os.getenv("LM_STUDIO_API_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL_NAME = os.getenv("LM_STUDIO_MODEL_NAME", "local-model")  # 또는 "qwen/qwen3-vl-8b"

# 데이터베이스 경로
DB_PATH = ROOT_DIR / "db" / "trading.db"

# 뉴스 API 설정 (옵션)
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
RSS_FEED_URLS = [
    "https://www.coindesk.com/feed/",
    # 추가 RSS 피드 URL
]

# 로깅 설정
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

