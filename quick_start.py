"""
롤체 RAG 시스템 - 빠른 시작 가이드

이 파일을 실행하면 전체 시스템을 테스트할 수 있습니다.
"""

from main import TFTRAGSystem
from data.metadata_schema import GameState
import json


def quick_start_demo():
    """빠른 시작 데모"""
    
    print("="*60)
    print("롤체 RAG 시스템 - 빠른 시작 데모")
    print("="*60)
    
    # 1. 시스템 초기화
    print("\n[1단계] 시스템 초기화 중...")
    system = TFTRAGSystem()
    
    # 2. 테스트 데이터 추가
    print("\n[2단계] 테스트 전략 데이터 추가 중...")
    
    test_chunks = [
        {
            'id': 'demo_001',
            'text': '''
                2-1에서는 연패 전략을 추천합니다.
                야스오나 요네가 나오면 바로 픽업하세요.
                골드를 최대한 아껴서 4-1까지 50골드 이상 유지하는 게 목표입니다.
                체력이 30 이하로 떨어지면 최소한의 방어는 해야 합니다.
            ''',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '2-1',
                'strategy_type': '연패',
                'composition_name': '6도전자',
                'key_champions': json.dumps(['야스오', '요네'], ensure_ascii=False),
                'synergies': json.dumps(['도전자'], ensure_ascii=False),
                'core_items': json.dumps(['무한의 대검'], ensure_ascii=False),
                'difficulty': '초보',
                'video_source': '테스트영상_001',
                'timestamp': '0:00-2:30'
            }
        },
        {
            'id': 'demo_002',
            'text': '''
                3-2가 되면 레벨 6으로 올려야 합니다.
                골드가 50 이상이고 야스오가 2개 이상 있으면 리롤을 시작하세요.
                목표는 야스오 2성 또는 요네 2성을 만드는 것입니다.
                2성이 완성되면 리롤을 멈추고 레벨업으로 전환하세요.
            ''',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '3-2',
                'strategy_type': '리롤',
                'composition_name': '6도전자',
                'key_champions': json.dumps(['야스오', '요네'], ensure_ascii=False),
                'synergies': json.dumps(['도전자'], ensure_ascii=False),
                'core_items': json.dumps(['무한의 대검', '최후의 속삭임'], ensure_ascii=False),
                'difficulty': '초보',
                'video_source': '테스트영상_001',
                'timestamp': '2:30-5:00'
            }
        },
        {
            'id': 'demo_003',
            'text': '''
                4-1에서는 레벨 7-8로 올리고 강력한 조합을 완성해야 합니다.
                연패로 모은 골드를 사용할 시점입니다.
                도전자 6을 완성하거나, 다른 시너지로 전환을 고려하세요.
                아이템은 핵심 캐리에게 몰아주는 게 중요합니다.
            ''',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '4-1',
                'strategy_type': '전환',
                'composition_name': '6도전자',
                'key_champions': json.dumps(['야스오', '요네', '아지르'], ensure_ascii=False),
                'synergies': json.dumps(['도전자', '황제'], ensure_ascii=False),
                'core_items': json.dumps(['무한의 대검', '최후의 속삭임', '거인 학살자'], ensure_ascii=False),
                'difficulty': '중급',
                'video_source': '테스트영상_001',
                'timestamp': '5:00-7:30'
            }
        },
        {
            'id': 'demo_004',
            'text': '''
                아이템 우선순위: 무한의 대검 > 최후의 속삭임 > 거인 학살자
                야스오에게 공격 아이템을 주는 게 가장 좋습니다.
                방어 아이템은 앞라인 탱커에게 주세요.
                아이템이 애매하면 최대한 합치지 말고 기다리세요.
            ''',
            'metadata': {
                'season': '시즌13',
                'patch': '13.24',
                'game_stage': '3-2',
                'strategy_type': '아이템 판단',
                'composition_name': '6도전자',
                'key_champions': json.dumps(['야스오'], ensure_ascii=False),
                'synergies': json.dumps(['도전자'], ensure_ascii=False),
                'core_items': json.dumps(['무한의 대검', '최후의 속삭임', '거인 학살자'], ensure_ascii=False),
                'difficulty': '초보',
                'video_source': '테스트영상_002',
                'timestamp': '0:00-1:30'
            }
        }
    ]
    
    system.vector_store.add_chunks(test_chunks)
    
    # 3. 통계 확인
    print("\n[3단계] 데이터 저장 확인")
    system.get_stats()
    
    # 4. 질문 예시
    print("\n[4단계] 질문 테스트")
    print("="*60)
    
    test_questions = [
        {
            "question": "2-1에서 뭐 해야 해?",
            "game_state": None
        },
        {
            "question": "리롤해야 할까요?",
            "game_state": GameState(
                round="3-2",
                level=5,
                gold=52,
                hp=70,
                current_champions=["야스오", "야스오", "요네"],
                current_synergies=["도전자 2"],
                bench_champions=["세트"],
                items=["B.F. 대검", "B.F. 대검"],
                win_streak=0,
                lose_streak=3,
                question="리롤해야 할까요?"
            )
        }
    ]
    
    for i, test in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"테스트 질문 {i}")
        print('='*60)
        
        if test["game_state"]:
            print(f"게임 상태: {test['game_state'].round} 라운드, "
                  f"레벨 {test['game_state'].level}, "
                  f"골드 {test['game_state'].gold}")
        
        print(f"질문: {test['question']}")
        print("-"*60)
        
        response = system.query(
            question=test["question"],
            game_state=test["game_state"]
        )
        
        print("\n답변:")
        print(response["answer"])
        
        if response.get("sources"):
            print("\n출처:")
            for j, source in enumerate(response["sources"], 1):
                print(f"  {j}. {source['video_source']} "
                      f"({source['timestamp']}) "
                      f"- {source['strategy_type']}")
    
    print("\n" + "="*60)
    print("데모 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. 실제 유튜브 영상 처리: python main.py --mode process --video_url [URL]")
    print("2. 대화형 모드 실행: python main.py --mode interactive")
    print("3. README.md 참고")
    print("="*60)


if __name__ == "__main__":
    try:
        quick_start_demo()
    except Exception as e:
        print(f"\n오류 발생: {e}")
        print("\n문제 해결:")
        print("1. requirements.txt의 모든 패키지가 설치되었는지 확인")
        print("2. .env 파일에 ANTHROPIC_API_KEY가 설정되었는지 확인")
        print("3. Python 버전이 3.8 이상인지 확인")
