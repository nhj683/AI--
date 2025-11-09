"""
Hugging Face에서 직접 모델을 로드하는 테스트
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


def test_hf_model():
    """Hugging Face 모델 테스트"""
    print("=" * 60)
    print("Hugging Face 모델 테스트")
    print("=" * 60)
    
    if not PACKAGES_AVAILABLE:
        print(f"\n❌ 필수 패키지가 설치되지 않았습니다!")
        print(f"   오류: {MISSING_PACKAGE}")
        return False
    
    # 1. 라이브러리 확인
    print(f"\n1. 라이브러리 확인...")
    import torch
    import transformers
    print(f"   ✅ PyTorch 버전: {torch.__version__}")
    print(f"   ✅ Transformers 버전: {transformers.__version__}")
    print(f"   ✅ CUDA 사용 가능: {torch.cuda.is_available()}")
    if not torch.cuda.is_available():
        print(f"   ℹ️  CPU 모드로 실행됩니다 (느릴 수 있음)")
    
    # 2. 작은 모델로 테스트 (빠른 테스트를 위해)
    print(f"\n2. 작은 모델로 테스트 (빠른 테스트)...")
    
    # Qwen2.5-3B-Instruct 또는 더 작은 모델 사용
    # 실제 프로덕션에서는 더 큰 모델을 사용할 수 있음
    model_name = "Qwen/Qwen2.5-3B-Instruct"
    
    print(f"   모델: {model_name}")
    print(f"   💡 처음 실행 시 모델을 다운로드하므로 시간이 걸릴 수 있습니다.")
    print(f"   💡 모델 크기: 약 6GB (다운로드 필요)")
    
    try:
        print(f"\n3. 모델 로딩 시작...")
        
        # 토크나이저 로드
        print(f"   토크나이저 로딩 중...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        print(f"   ✅ 토크나이저 로드 완료")
        
        # 모델 로드
        print(f"   모델 로딩 중... (시간이 걸릴 수 있습니다)")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        if not torch.cuda.is_available():
            model = model.to("cpu")
        
        model.eval()
        print(f"   ✅ 모델 로드 완료")
        
        # 4. 텍스트 생성 테스트
        print(f"\n4. 텍스트 생성 테스트...")
        
        test_prompts = [
            "안녕하세요!",
            "비트코인에 대해 간단히 설명해주세요.",
            "1+1은 얼마인가요?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n   테스트 {i}: {prompt}")
            print(f"   생성 중...")
            
            try:
                # Qwen2.5는 채팅 템플릿 사용
                messages = [
                    {"role": "user", "content": prompt}
                ]
                
                # 채팅 템플릿 적용
                text = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                
                # 토크나이징
                model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
                
                # 생성
                with torch.no_grad():
                    generated_ids = model.generate(
                        **model_inputs,
                        max_new_tokens=256,
                        temperature=0.7,
                        do_sample=True
                    )
                
                # 디코딩
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                
                print(f"   ✅ 응답:")
                print(f"   {response[:300]}{'...' if len(response) > 300 else ''}")
                
            except Exception as e:
                print(f"   ❌ 텍스트 생성 실패: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"\n" + "=" * 60)
        print("✅ 모든 테스트 통과!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"   ❌ 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 대안:")
        print(f"   1. 인터넷 연결 확인")
        print(f"   2. 모델 이름 확인: {model_name}")
        print(f"   3. 디스크 공간 확인 (약 6GB 필요)")
        print(f"   4. 더 작은 모델 사용 (예: Qwen/Qwen2.5-1.5B-Instruct)")
        return False


if __name__ == "__main__":
    success = test_hf_model()
    sys.exit(0 if success else 1)

