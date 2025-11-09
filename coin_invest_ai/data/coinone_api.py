"""
코인원 API 연동 모듈
"""

import requests
import hashlib
import hmac
import time
import json
import base64
from typing import Dict, List, Optional
from config import COINONE_ACCESS_TOKEN, COINONE_SECRET_KEY
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://api.coinone.co.kr"


class CoinoneAPI:
    """코인원 API 클라이언트"""
    
    def __init__(self, access_token: str = None, secret_key: str = None):
        """
        Args:
            access_token: 코인원 Access Token
            secret_key: 코인원 Secret Key
        """
        self.access_token = access_token or COINONE_ACCESS_TOKEN
        self.secret_key = secret_key or COINONE_SECRET_KEY
        
        if not self.access_token or not self.secret_key:
            logger.warning("Access Token 또는 Secret Key가 설정되지 않았습니다.")
    
    def _prepare_private_api_request(self, payload: Dict) -> tuple:
        """
        Private API 요청을 위한 페이로드 및 헤더 준비
        코인원 API 문서에 따른 정확한 인증 방식 구현
        
        Args:
            payload: 요청 페이로드 딕셔너리
            
        Returns:
            (encoded_payload, headers) 튜플
            - encoded_payload: Base64 인코딩된 페이로드 (문자열)
            - headers: 요청 헤더 딕셔너리
        """
        # 페이로드에 기본 필드 추가
        payload['access_token'] = self.access_token
        payload['nonce'] = int(time.time() * 1000)  # V2.0 API: 정수 형태의 타임스탬프
        
        # JSON 문자열로 변환
        json_payload = json.dumps(payload, separators=(',', ':'))
        
        # Base64 인코딩 (X-COINONE-PAYLOAD)
        encoded_payload = base64.b64encode(json_payload.encode('utf-8')).decode('utf-8')
        
        # HMAC-SHA512 서명 생성 (X-COINONE-SIGNATURE)
        # Base64 인코딩된 페이로드를 바이트로 변환하여 서명 생성
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            encoded_payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # 헤더 설정
        headers = {
            'Content-Type': 'application/json',
            'X-COINONE-PAYLOAD': encoded_payload,
            'X-COINONE-SIGNATURE': signature
        }
        
        return encoded_payload, headers
    
    def get_ticker(self, currency: str = "BTC") -> Dict:
        """
        현재가 조회
        
        Args:
            currency: 통화 코드 (BTC, ETH, XRP 등)
            
        Returns:
            현재가 정보
        """
        try:
            url = f"{BASE_URL}/ticker"
            params = {"currency": currency}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"현재가 조회 실패: {e}")
            return {}
    
    def get_orderbook(self, currency: str = "BTC") -> Dict:
        """
        호가 조회
        
        Args:
            currency: 통화 코드
            
        Returns:
            호가 정보
        """
        try:
            url = f"{BASE_URL}/orderbook"
            params = {"currency": currency}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"호가 조회 실패: {e}")
            return {}
    
    def get_balance(self) -> Dict:
        """
        잔고 조회 (인증 필요)
        
        Returns:
            잔고 정보
        """
        try:
            url = f"{BASE_URL}/v2/account/balance"
            
            # 코인원 API 문서에 따른 인증 방식 사용
            encoded_payload, headers = self._prepare_private_api_request({})
            
            # Request Body에 Base64 인코딩된 페이로드 전송
            response = requests.post(url, data=encoded_payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            # 오류 발생 시 로깅
            if result.get('result') == 'error':
                error_code = result.get('errorCode', '')
                error_msg = result.get('errorMsg', '')
                logger.warning(f"잔고 조회 오류: {error_code} - {error_msg}")
            
            return result
            
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return {}
    
    def place_order(self, price: int, qty: float, currency: str = "BTC", 
                   order_type: str = "bid") -> Dict:
        """
        주문하기 (인증 필요)
        
        Args:
            price: 주문 가격
            qty: 주문 수량
            currency: 통화 코드
            order_type: 주문 유형 ("bid": 매수, "ask": 매도)
            
        Returns:
            주문 결과
        """
        try:
            url = f"{BASE_URL}/v2/order/{order_type}"
            
            # 코인원 API 문서에 따른 인증 방식 사용
            encoded_payload, headers = self._prepare_private_api_request({
                "price": price,
                "qty": qty,
                "currency": currency
            })
            
            # Request Body에 Base64 인코딩된 페이로드 전송
            response = requests.post(url, data=encoded_payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"주문 실패: {e}")
            return {}
    
    def get_orders(self, currency: str = "BTC") -> Dict:
        """
        주문 내역 조회 (인증 필요)
        
        Args:
            currency: 통화 코드
            
        Returns:
            주문 내역
        """
        try:
            url = f"{BASE_URL}/v2/order/limit_orders"
            
            # 코인원 API 문서에 따른 인증 방식 사용
            encoded_payload, headers = self._prepare_private_api_request({
                "currency": currency
            })
            
            # Request Body에 Base64 인코딩된 페이로드 전송
            response = requests.post(url, data=encoded_payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"주문 내역 조회 실패: {e}")
            return {}

