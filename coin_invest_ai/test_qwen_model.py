"""
업데이트된 QwenModel 클래스 테스트
"""

from models.qwen_local import QwenModel
from config import USE_LMSTUDIO_API, LM_STUDIO_MODEL_NAME
import logging

logging.basicConfig(level=logging.INFO)

def test_qwen_model():
    """QwenModel 클래스 테스트"""
    print("=" * 60)
    print("QwenModel 클래스 테스트")
    print("=" * 60)
    
    # LM Studio API 사용 여부 확인
    use_lmstudio = USE_LMSTUDIO_API
    print(f"\n1. 설정 확인...")
    print(f"   LM Studio API 사용: {use_lmstudio}")
    if use_lmstudio:
        print(f"   모델 이름: {LM_STUDIO_MODEL_NAME}")
    
    # 모델 초기화
    print(f"\n2. 모델 초기화...")
    try:
        model = QwenModel(use_lmstudio=use_lmstudio)
        print(f"   ✅ 모델 초기화 완료")
    except Exception as e:
        print(f"   ❌ 모델 초기화 실패: {e}")
        return False
    
    # 모델 로드
    print(f"\n3. 모델 로드...")
    try:
        model.load_model()
        print(f"   ✅ 모델 로드 완료")
    except Exception as e:
        print(f"   ❌ 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 텍스트 생성 테스트
    print(f"\n4. 텍스트 생성 테스트...")
    test_prompts = [
        "안녕하세요!",
        "비트코인에 대해 간단히 설명해주세요.",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        try:
            print(f"\n   테스트 {i}: {prompt}")
            print(f"   생성 중...")
            
            response = model.generate(
                prompt=prompt,
                max_length=256,
                temperature=0.7,
                model_name=LM_STUDIO_MODEL_NAME if use_lmstudio else None
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
    test_qwen_model()

