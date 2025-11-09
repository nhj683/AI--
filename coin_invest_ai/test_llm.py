"""
로컬 LLM 연결 테스트 스크립트
"""

import sys
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 필수 패키지 확인
try:
    import torch
    import transformers
    from transformers import AutoModelForCausalLM, AutoTokenizer
    PACKAGES_AVAILABLE = True
except ImportError as e:
    PACKAGES_AVAILABLE = False
    MISSING_PACKAGE = str(e)

from config import QWEN_MODEL_PATH


def test_llm_connection():
    """로컬 LLM 연결 테스트"""
    print("=" * 60)
    print("로컬 LLM 연결 테스트")
    print("=" * 60)
    
    # 0. 필수 패키지 확인
    if not PACKAGES_AVAILABLE:
        print(f"\n❌ 필수 패키지가 설치되지 않았습니다!")
        print(f"   오류: {MISSING_PACKAGE}")
        print(f"\n💡 다음 명령어로 패키지를 설치해주세요:")
        print(f"   pip install -r requirements.txt")
        print(f"\n   또는 개별 설치:")
        print(f"   pip install torch transformers accelerate sentencepiece")
        return False
    
    # 1. 필요한 라이브러리 확인
    print(f"\n1. 필요한 라이브러리 확인...")
    try:
        import torch
        import transformers
        print(f"   ✅ PyTorch 버전: {torch.__version__}")
        print(f"   ✅ Transformers 버전: {transformers.__version__}")
        print(f"   ✅ CUDA 사용 가능: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   ✅ CUDA 버전: {torch.version.cuda}")
            print(f"   ✅ GPU 개수: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"      - GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print(f"   ℹ️  CPU 모드로 실행됩니다 (느릴 수 있음)")
    except Exception as e:
        print(f"   ❌ 라이브러리 확인 실패: {e}")
        return False
    
    # 2. 모델 경로 확인
    print(f"\n2. 모델 경로 확인...")
    model_path = Path(QWEN_MODEL_PATH)
    print(f"   설정된 경로: {QWEN_MODEL_PATH}")
    
    # 절대 경로로 변환
    if not model_path.is_absolute():
        model_path = Path(__file__).parent / model_path
    
    if not model_path.exists():
        print(f"   ❌ 모델 경로가 존재하지 않습니다!")
        print(f"   💡 모델을 다운로드하거나 경로를 수정해주세요.")
        print(f"   💡 Hugging Face에서 모델을 다운로드할 수 있습니다:")
        print(f"      - Qwen2.5-7B-Instruct: Qwen/Qwen2.5-7B-Instruct")
        print(f"      - Qwen2.5-3B-Instruct: Qwen/Qwen2.5-3B-Instruct")
        print(f"      - Qwen2-7B-Instruct: Qwen/Qwen2-7B-Instruct")
        print(f"\n   💡 모델 다운로드 예시:")
        print(f"      from transformers import AutoModelForCausalLM, AutoTokenizer")
        print(f"      model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-7B-Instruct')")
        print(f"      tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-7B-Instruct')")
        return False
    else:
        print(f"   ✅ 모델 경로 존재 확인: {model_path}")
    
    # 3. 모델 로드 테스트
    print(f"\n3. 모델 로드 테스트...")
    try:
        from models.qwen_local import QwenModel
        model = QwenModel(model_path=str(model_path))
        print(f"   사용 디바이스: {model.device}")
        print(f"   모델 로딩 시작... (시간이 걸릴 수 있습니다)")
        model.load_model()
        print(f"   ✅ 모델 로드 성공!")
    except Exception as e:
        print(f"   ❌ 모델 로드 실패: {e}")
        import traceback
        print(f"\n   상세 오류:")
        traceback.print_exc()
        return False
    
    # 4. 텍스트 생성 테스트
    print(f"\n4. 텍스트 생성 테스트...")
    test_prompts = [
        "안녕하세요!",
        "비트코인에 대해 간단히 설명해주세요.",
        "1+1은 얼마인가요?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        try:
            print(f"\n   테스트 {i}: {prompt}")
            print(f"   생성 중...")
            
            # Qwen 모델의 경우 채팅 템플릿을 사용해야 할 수 있음
            response = model.generate(
                prompt=prompt,
                max_length=256,
                temperature=0.7
            )
            
            print(f"   ✅ 응답:")
            print(f"   {response[:200]}{'...' if len(response) > 200 else ''}")
            
        except Exception as e:
            print(f"   ❌ 텍스트 생성 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n" + "=" * 60)
    print("✅ 모든 테스트 통과!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)

