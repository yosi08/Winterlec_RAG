from typing import List, Dict, Optional
from rag.vector_store import TFTVectorStore
from data.metadata_schema import GameState
import re


class TFTRetriever:
    """
    롤체 전략 검색기
    - Hybrid Search (벡터 + 메타데이터 필터)
    - 쿼리 분석 및 필터 자동 생성
    - 재정렬 (Reranking)
    """
    
    def __init__(
        self,
        vector_store: TFTVectorStore,
        top_k: int = 5,
        rerank_top_k: int = 3
    ):
        """
        Args:
            vector_store: TFTVectorStore 인스턴스
            top_k: 초기 검색 결과 개수
            rerank_top_k: 재정렬 후 최종 선택 개수
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k
    
    def _extract_game_stage(self, query: str) -> Optional[str]:
        """쿼리에서 게임 단계 추출"""
        # 2-1 형식
        round_pattern = r'\b([2-5])-([1-7])\b'
        match = re.search(round_pattern, query)
        if match:
            return match.group(0)
        
        # 키워드
        if '초반' in query or '크립' in query:
            return '2-1'
        elif '중반' in query:
            return '3-2'
        elif '후반' in query:
            return '4-1'
        
        return None
    
    def _extract_strategy_type(self, query: str) -> Optional[str]:
        """쿼리에서 전략 유형 추출"""
        if '리롤' in query or '돌림' in query or '돌려' in query:
            return '리롤'
        elif '레벨' in query:
            return '레벨링'
        elif '연승' in query:
            return '연승'
        elif '연패' in query:
            return '연패'
        elif '전환' in query or '바꾸' in query:
            return '전환'
        elif '고정' in query or '유지' in query:
            return '고정'
        elif '아이템' in query:
            return '아이템 판단'
        
        return None
    
    def _build_filters(
        self,
        query: str,
        game_state: Optional[GameState] = None
    ) -> Dict:
        """
        쿼리와 게임 상태로부터 메타데이터 필터 생성
        
        Args:
            query: 사용자 질문
            game_state: 현재 게임 상태 (선택)
            
        Returns:
            ChromaDB where 필터
        """
        filters = {}
        
        # 1. 게임 단계 필터
        stage = None
        if game_state:
            stage = game_state.round
        else:
            stage = self._extract_game_stage(query)
        
        if stage:
            filters['game_stage'] = stage
        
        # 2. 전략 유형 필터
        strategy_type = self._extract_strategy_type(query)
        if strategy_type:
            filters['strategy_type'] = strategy_type
        
        return filters if filters else None
    
    def _rerank_results(
        self,
        results: List[Dict],
        game_state: Optional[GameState] = None
    ) -> List[Dict]:
        """
        검색 결과 재정렬
        
        우선순위:
        1. 현재 패치 (최신 > 이전)
        2. 게임 단계 일치
        3. 난이도 (초보자 우선)
        4. 거리 점수
        """
        def score_result(result: Dict) -> float:
            score = 0.0
            metadata = result['metadata']
            
            # 1. 패치 점수 (최신 패치 가중치)
            # 예: 13.24 > 13.23
            try:
                patch_parts = metadata.get('patch', '0.0').split('.')
                patch_score = float(patch_parts[0]) * 100 + float(patch_parts[1])
                score += patch_score
            except:
                pass
            
            # 2. 게임 단계 일치 (높은 가중치)
            if game_state and metadata.get('game_stage') == game_state.round:
                score += 1000
            
            # 3. 난이도 (초보자 우선)
            difficulty_scores = {'입문': 100, '초보': 80, '중급': 50, '고급': 20}
            score += difficulty_scores.get(metadata.get('difficulty', '초보'), 0)
            
            # 4. 거리 점수 (낮을수록 좋음)
            if result.get('distance') is not None:
                score -= result['distance'] * 10
            
            return score
        
        # 점수로 정렬
        scored_results = [(score_result(r), r) for r in results]
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        # 상위 K개 반환
        return [r for _, r in scored_results[:self.rerank_top_k]]
    
    def retrieve(
        self,
        query: str,
        game_state: Optional[GameState] = None
    ) -> List[Dict]:
        """
        쿼리로 관련 전략 검색
        
        Args:
            query: 사용자 질문
            game_state: 현재 게임 상태 (선택)
            
        Returns:
            재정렬된 검색 결과
        """
        # 1. 필터 생성
        filters = self._build_filters(query, game_state)
        
        print(f"\n=== 검색 시작 ===")
        print(f"쿼리: {query}")
        print(f"필터: {filters}")
        
        # 2. Vector Search
        results = self.vector_store.search(
            query=query,
            n_results=self.top_k,
            filters=filters
        )
        
        print(f"초기 검색 결과: {len(results)}개")
        
        # 3. Reranking
        reranked = self._rerank_results(results, game_state)
        
        print(f"재정렬 후: {len(reranked)}개")
        print("=== 검색 완료 ===\n")
        
        return reranked
    
    def format_context(self, results: List[Dict]) -> str:
        """
        검색 결과를 프롬프트용 컨텍스트로 포맷팅
        
        Returns:
            프롬프트에 넣을 컨텍스트 문자열
        """
        if not results:
            return "관련된 전략을 찾을 수 없습니다."
        
        context_parts = []
        
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            
            context = f"""
[전략 {i}]
- 게임 단계: {metadata.get('game_stage', '미정')}
- 전략 유형: {metadata.get('strategy_type', '미정')}
- 조합: {metadata.get('composition_name', '미정')}
- 난이도: {metadata.get('difficulty', '초보')}
- 내용: {result['text']}
"""
            context_parts.append(context.strip())
        
        return "\n\n".join(context_parts)


# 사용 예시
if __name__ == "__main__":
    from rag.vector_store import TFTVectorStore
    
    # Vector Store 초기화
    vector_store = TFTVectorStore()
    
    # Retriever 초기화
    retriever = TFTRetriever(
        vector_store=vector_store,
        top_k=5,
        rerank_top_k=3
    )
    
    # 게임 상태 예시
    game_state = GameState(
        round="3-2",
        level=5,
        gold=45,
        hp=75,
        current_champions=["야스오", "요네"],
        current_synergies=["도전자 2"],
        bench_champions=["세트"],
        items=["무한의 대검"],
        win_streak=0,
        lose_streak=3,
        question="연패 중인데 리롤해야 할까요?"
    )
    
    # 검색
    results = retriever.retrieve(
        query=game_state.question,
        game_state=game_state
    )
    
    # 컨텍스트 포맷팅
    context = retriever.format_context(results)
    print("\n=== 생성된 컨텍스트 ===")
    print(context)
