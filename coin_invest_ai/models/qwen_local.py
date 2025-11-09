"""
Qwen 모델 로딩 및 추론을 위한 모듈
LM Studio API 또는 로컬 모델 사용
"""

import requests
import logging
from typing import Optional
from config import QWEN_MODEL_PATH

logger = logging.getLogger(__name__)

# LM Studio API 기본 URL
LM_STUDIO_API_URL = "http://localhost:1234/v1"


class QwenModel:
    """Qwen 모델을 로드하고 추론하는 클래스 (LM Studio API 사용)"""
    
    def __init__(self, model_path: str = None, use_lmstudio: bool = True, api_url: str = None):
        """
        Args:
            model_path: 모델 경로 (로컬 모델 사용 시)
            use_lmstudio: LM Studio API 사용 여부 (기본값: True)
            api_url: LM Studio API URL (기본값: http://localhost:1234/v1)
        """
        self.model_path = model_path or QWEN_MODEL_PATH
        self.use_lmstudio = use_lmstudio
        self.api_url = api_url or LM_STUDIO_API_URL
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """모델 로드 (LM Studio API의 경우 연결 확인)"""
        try:
            if self.use_lmstudio:
                logger.info("LM Studio API 사용 모드")
                # LM Studio API 서버 연결 확인
                try:
                    response = requests.get(f"{self.api_url}/models", timeout=5)
                    if response.status_code == 200:
                        models = response.json()
                        if 'data' in models and len(models['data']) > 0:
                            logger.info(f"LM Studio API 연결 성공")
                            logger.info(f"사용 가능한 모델: {[m.get('id') for m in models['data']]}")
                        else:
                            logger.warning("LM Studio에 로드된 모델이 없습니다")
                    else:
                        logger.warning(f"LM Studio API 응답 오류: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    logger.error("LM Studio API 서버에 연결할 수 없습니다")
                    raise ConnectionError("LM Studio API 서버를 시작해주세요")
            else:
                # 로컬 모델 로드 (기존 방식)
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                logger.info(f"로컬 모델 로딩 중: {self.model_path}")
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"사용 디바이스: {self.device}")
                
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path,
                    trust_remote_code=True
                )
                
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_path,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                
                if self.device == "cpu":
                    self.model = self.model.to(self.device)
                
                self.model.eval()
                logger.info("로컬 모델 로딩 완료")
            
        except Exception as e:
            logger.error(f"모델 로딩 실패: {e}")
            raise
    
    def generate(self, prompt: str, max_length: int = 512, temperature: float = 0.7, 
                 model_name: str = "local-model") -> str:
        """
        텍스트 생성
        
        Args:
            prompt: 입력 프롬프트
            max_length: 최대 생성 길이
            temperature: 생성 온도
            model_name: LM Studio에서 사용할 모델 이름 (기본값: "local-model")
            
        Returns:
            생성된 텍스트
        """
        if self.use_lmstudio:
            # LM Studio API 사용
            try:
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_length
                }
                
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                    else:
                        raise ValueError("응답에 choices가 없습니다")
                else:
                    raise Exception(f"API 요청 실패: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                raise ConnectionError("LM Studio API 서버에 연결할 수 없습니다")
            except Exception as e:
                logger.error(f"텍스트 생성 실패: {e}")
                raise
        else:
            # 로컬 모델 사용
            if self.model is None or self.tokenizer is None:
                raise ValueError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
            
            try:
                # 토크나이징
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                
                # 생성
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        temperature=temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                # 디코딩
                generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # 프롬프트 제거하고 생성된 부분만 반환
                if generated_text.startswith(prompt):
                    generated_text = generated_text[len(prompt):].strip()
                
                return generated_text
                
            except Exception as e:
                logger.error(f"텍스트 생성 실패: {e}")
                raise

