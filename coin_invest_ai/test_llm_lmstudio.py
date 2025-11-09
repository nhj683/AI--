"""
LM Studio API 서버를 통한 LLM 테스트
"""

import requests
import json

def test_lmstudio_api():
    """LM Studio API 서버 테스트"""
    print("=" * 60)
    print("LM Studio API 서버 테스트")
    print("=" * 60)
    
    # LM Studio 기본 URL
    base_url = "http://localhost:1234/v1"
    
    # 1. API 서버 연결 확인
    print(f"\n1. LM Studio API 서버 연결 확인...")
    try:
        response = requests.get(f"{base_url}/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"   ✅ API 서버 연결 성공!")
            if 'data' in models and len(models['data']) > 0:
                print(f"   로드된 모델:")
                for model in models['data']:
                    print(f"      - {model.get('id', 'Unknown')}")
            else:
                print(f"   ⚠️  로드된 모델이 없습니다.")
        else:
            print(f"   ❌ API 서버 응답 오류: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ❌ LM Studio API 서버에 연결할 수 없습니다!")
        print(f"   💡 LM Studio를 실행하고 API 서버를 활성화해주세요.")
        print(f"   💡 LM Studio > Settings > Server > Enable API Server")
        return False
    except Exception as e:
        print(f"   ❌ 오류 발생: {e}")
        return False
    
    # 2. 채팅 완성 테스트
    print(f"\n2. 채팅 완성 테스트...")
    try:
        test_prompts = [
            "안녕하세요!",
            "비트코인에 대해 간단히 설명해주세요.",
            "1+1은 얼마인가요?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n   테스트 {i}: {prompt}")
            
            payload = {
                "model": "local-model",  # LM Studio는 로컬 모델 이름을 사용
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 256
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print(f"   ✅ 응답:")
                    print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
                else:
                    print(f"   ❌ 응답 형식 오류")
            else:
                print(f"   ❌ 요청 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
    except Exception as e:
        print(f"   ❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n" + "=" * 60)
    print("✅ LM Studio API 테스트 완료!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_lmstudio_api()

