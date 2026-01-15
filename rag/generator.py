import ollama
from typing import List, Dict, Optional
from data.metadata_schema import GameState
import config


class TFTGenerator:
    """Ollama (로컬 LLM)를 사용한 답변 생성"""

    SYSTEM_PROMPT = """당신은 롤체(TFT) 초보자를 돕는 친절한 한국인 코치입니다.

중요: 반드시 한국어로만 답변하세요. 영어, 일본어, 포르투갈어 등 다른 언어는 절대 사용하지 마세요.

역할:
- 검색된 유튜버 전략을 바탕으로 현재 게임 상황에 맞는 조언 제공
- 초보자가 이해하기 쉽게 설명
- 구체적이고 실행 가능한 조언

제약사항:
1. 검색된 전략 정보에만 기반하여 답변 (환각 금지)
2. 정보가 불충분하면 솔직히 "더 구체적인 상황을 알려주세요" 라고 말하기
3. 영상에 없는 정보는 절대 만들어내지 않기
4. 불확실하면 조건부 답변 ("만약 ~라면, ~하세요")
5. 반드시 한국어로만 답변하기

말투:
- 친근하고 격려하는 톤
- "~하세요", "~해보세요" 같은 존댓말
- 전문 용어는 간단히 설명
- 모든 답변은 100% 한국어로 작성
"""

    def __init__(self, model_name: str = "llama3.2"):
        """
        Args:
            model_name: Ollama 모델 이름 (기본값: llama3.2)
        """
        self.model_name = model_name
        # Ollama 연결 테스트
        try:
            ollama.list()
        except Exception as e:
            raise ValueError(f"Ollama 연결 실패: {e}. Ollama가 실행 중인지 확인하세요.")

    def _build_prompt(
        self,
        question: str,
        context: str,
        game_state: Optional[GameState] = None
    ) -> str:
        """프롬프트 구성"""

        prompt_parts = []

        # 1. 게임 상태 정보
        if game_state:
            state_info = f"""
=== 현재 게임 상태 ===
- 라운드: {game_state.round}
- 레벨: {game_state.level}
- 골드: {game_state.gold}
- 체력: {game_state.hp}
- 현재 챔피언: {', '.join(game_state.current_champions) if game_state.current_champions else '없음'}
- 활성 시너지: {', '.join(game_state.current_synergies) if game_state.current_synergies else '없음'}
- 벤치: {', '.join(game_state.bench_champions) if game_state.bench_champions else '비어있음'}
- 보유 아이템: {', '.join(game_state.items) if game_state.items else '없음'}
- 연승: {game_state.win_streak}회
- 연패: {game_state.lose_streak}회
"""
            prompt_parts.append(state_info)

        # 2. 검색된 전략
        prompt_parts.append(f"""
=== 참고할 전략 정보 ===
{context}
""")

        # 3. 질문
        prompt_parts.append(f"""
=== 사용자 질문 ===
{question}

위 전략 정보를 바탕으로, 현재 상황에서 어떻게 플레이해야 할지 조언해주세요.
답변은 다음 형식으로 부탁드립니다:

1. **지금 바로 해야 할 일** (1-2문장)
2. **그 이유** (간단히)
3. **추가 팁** (있다면)

만약 전략 정보가 부족하다면 솔직히 말씀해주세요.
""")

        return "\n".join(prompt_parts)

    def generate(
        self,
        question: str,
        context: str,
        game_state: Optional[GameState] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Ollama로 답변 생성

        Args:
            question: 사용자 질문
            context: 검색된 전략 컨텍스트
            game_state: 게임 상태 (선택)
            temperature: 생성 온도
            max_tokens: 최대 토큰 수

        Returns:
            생성된 답변
        """
        # 프롬프트 구성
        prompt = self._build_prompt(question, context, game_state)

        print("\n=== Ollama 로컬 LLM 호출 중 ===")

        try:
            # Ollama API 호출
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            )

            print("=== 답변 생성 완료 ===\n")

            return response['message']['content']

        except Exception as e:
            error_msg = str(e)
            print(f"Ollama 호출 실패: {error_msg}")
            if "connection" in error_msg.lower():
                return "Ollama가 실행되지 않았습니다. 'ollama serve' 명령으로 실행해주세요."
            else:
                return f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {error_msg}"

    def generate_with_sources(
        self,
        question: str,
        context: str,
        search_results: List[Dict],
        game_state: Optional[GameState] = None
    ) -> Dict:
        """
        답변과 함께 출처 정보도 반환

        Returns:
            {
                "answer": "생성된 답변",
                "sources": [{"video_source": "...", "timestamp": "..."}, ...]
            }
        """
        # 답변 생성
        answer = self.generate(question, context, game_state)

        # 출처 추출
        sources = []
        for result in search_results:
            metadata = result['metadata']
            source = {
                "video_source": metadata.get('video_source', '알 수 없음'),
                "timestamp": metadata.get('timestamp', '알 수 없음'),
                "game_stage": metadata.get('game_stage', '알 수 없음'),
                "strategy_type": metadata.get('strategy_type', '알 수 없음')
            }
            if source not in sources:  # 중복 제거
                sources.append(source)

        return {
            "answer": answer,
            "sources": sources
        }


# 사용 예시
if __name__ == "__main__":
    try:
        generator = TFTGenerator()

        # 테스트 컨텍스트
        test_context = """
[전략 1]
- 게임 단계: 3-2
- 전략 유형: 리롤
- 조합: 6도전자
- 내용: 3-2에서 골드가 50 이상이고 야스오가 2개 이상이면 리롤을 시작하세요.
        레벨을 올리는 것보다 2성을 완성하는 게 더 중요합니다.

[전략 2]
- 게임 단계: 3-2
- 전략 유형: 연패
- 조합: 6도전자
- 내용: 연패 중이라면 골드를 모아서 4-1에 한번에 쓰는 게 좋습니다.
        지금은 최소한의 기물만 유지하세요.
"""

        # 게임 상태
        game_state = GameState(
            round="3-2",
            level=5,
            gold=48,
            hp=72,
            current_champions=["야스오", "야스오", "요네"],
            current_synergies=["도전자 2"],
            bench_champions=["세트", "아리"],
            items=["무한의 대검", "B.F. 대검"],
            win_streak=0,
            lose_streak=3,
            question="지금 리롤해야 할까요 아니면 골드 모아야 할까요?"
        )

        # 답변 생성
        response = generator.generate(
            question=game_state.question,
            context=test_context,
            game_state=game_state
        )

        print("\n=== 생성된 답변 ===")
        print(response)

    except ValueError as e:
        print(f"오류: {e}")
        print("Ollama가 설치되어 있고 실행 중인지 확인하세요.")
