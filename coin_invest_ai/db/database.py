"""
SQLite 데이터베이스 모듈: 매매 기록 저장 및 관리
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from config import DB_PATH
import logging

logger = logging.getLogger(__name__)


class TradingDatabase:
    """매매 기록 데이터베이스 클래스"""
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: 데이터베이스 파일 경로
        """
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 매매 기록 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        action TEXT NOT NULL,
                        price REAL NOT NULL,
                        quantity REAL NOT NULL,
                        total_amount REAL NOT NULL,
                        order_id TEXT,
                        status TEXT NOT NULL,
                        notes TEXT,
                        created_at TEXT NOT NULL
                    )
                """)
                
                # 포트폴리오 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        currency TEXT NOT NULL UNIQUE,
                        quantity REAL NOT NULL DEFAULT 0,
                        avg_price REAL NOT NULL DEFAULT 0,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # 분석 기록 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        currency TEXT NOT NULL,
                        analysis_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
                
                conn.commit()
                logger.info(f"데이터베이스 초기화 완료: {self.db_path}")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def add_trade(self, currency: str, action: str, price: float, 
                  quantity: float, order_id: str = None, 
                  status: str = "completed", notes: str = None) -> int:
        """
        매매 기록 추가
        
        Args:
            currency: 통화 코드
            action: 행동 ("buy" 또는 "sell")
            price: 가격
            quantity: 수량
            order_id: 주문 ID
            status: 상태
            notes: 메모
            
        Returns:
            추가된 레코드의 ID
        """
        try:
            timestamp = datetime.now().isoformat()
            total_amount = price * quantity
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO trades 
                    (timestamp, currency, action, price, quantity, total_amount, 
                     order_id, status, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (timestamp, currency, action, price, quantity, total_amount,
                      order_id, status, notes, timestamp))
                
                conn.commit()
                trade_id = cursor.lastrowid
                
                # 포트폴리오 업데이트
                self._update_portfolio(currency, action, quantity, price)
                
                logger.info(f"매매 기록 추가: {trade_id}")
                return trade_id
                
        except Exception as e:
            logger.error(f"매매 기록 추가 실패: {e}")
            raise
    
    def _update_portfolio(self, currency: str, action: str, quantity: float, price: float):
        """포트폴리오 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기존 포지션 조회
                cursor.execute("""
                    SELECT quantity, avg_price FROM portfolio WHERE currency = ?
                """, (currency,))
                
                row = cursor.fetchone()
                
                if row:
                    old_quantity, old_avg_price = row
                    
                    if action == "buy":
                        # 매수: 평균 가격 재계산
                        new_quantity = old_quantity + quantity
                        new_avg_price = (
                            (old_quantity * old_avg_price + quantity * price) / new_quantity
                        )
                    else:
                        # 매도: 수량 감소
                        new_quantity = old_quantity - quantity
                        new_avg_price = old_avg_price
                    
                    if new_quantity > 0:
                        cursor.execute("""
                            UPDATE portfolio 
                            SET quantity = ?, avg_price = ?, updated_at = ?
                            WHERE currency = ?
                        """, (new_quantity, new_avg_price, datetime.now().isoformat(), currency))
                    else:
                        cursor.execute("DELETE FROM portfolio WHERE currency = ?", (currency,))
                else:
                    # 새로운 포지션
                    if action == "buy":
                        cursor.execute("""
                            INSERT INTO portfolio (currency, quantity, avg_price, updated_at)
                            VALUES (?, ?, ?, ?)
                        """, (currency, quantity, price, datetime.now().isoformat()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"포트폴리오 업데이트 실패: {e}")
            raise
    
    def get_trades(self, currency: str = None, limit: int = 100) -> List[Dict]:
        """
        매매 기록 조회
        
        Args:
            currency: 통화 코드 (None이면 전체)
            limit: 조회 개수
            
        Returns:
            매매 기록 목록
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if currency:
                    cursor.execute("""
                        SELECT * FROM trades 
                        WHERE currency = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (currency, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM trades 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    """, (limit,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"매매 기록 조회 실패: {e}")
            return []
    
    def get_portfolio(self) -> List[Dict]:
        """
        포트폴리오 조회
        
        Returns:
            포트폴리오 목록
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM portfolio ORDER BY currency")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"포트폴리오 조회 실패: {e}")
            return []
    
    def add_analysis(self, currency: str, analysis_type: str, content: str):
        """
        분석 기록 추가
        
        Args:
            currency: 통화 코드
            analysis_type: 분석 유형
            content: 분석 내용
        """
        try:
            timestamp = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analysis (timestamp, currency, analysis_type, content, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (timestamp, currency, analysis_type, content, timestamp))
                
                conn.commit()
                logger.info("분석 기록 추가 완료")
                
        except Exception as e:
            logger.error(f"분석 기록 추가 실패: {e}")
            raise

