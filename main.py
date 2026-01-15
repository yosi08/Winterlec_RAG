"""
롤체 RAG 시스템 메인 파일

사용 예시:
1. 데이터 수집 및 처리:
   python main.py --mode process --video_url "https://youtube.com/..."

2. 질문하기:
   python main.py --mode query --question "3-2에서 뭐 해야 해?"

3. 대화형 모드:
   python main.py --mode interactive
"""

import argparse
from pathlib import Path
import json

from data.youtube_processor import YouTubeProcessor
from data.chunker import TFTChunker
from rag.vector_store import TFTVectorStore
from rag.retriever import TFTRetriever
from rag.generator import TFTGenerator
from data.metadata_schema import GameState
import config


class TFTRAGSystem:
    """롤체 RAG 통합 시스템"""
    
    def __init__(self):
        """시스템 초기화"""
        print("=== 롤체 RAG 시스템 초기화 ===")
        
        # 모듈 초기화
        self.youtube_processor = YouTubeProcessor()
        self.chunker = TFTChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.vector_store = TFTVectorStore(
            collection_name=config.COLLECTION_NAME,
            persist_directory=str(config.VECTOR_DB_DIR),
            embedding_model=config.EMBEDDING_MODEL
        )
        self.retriever = TFTRetriever(
            vector_store=self.vector_store,
            top_k=config.TOP_K,
            rerank_top_k=config.RERANK_TOP_K
        )
        
        # Generator는 API 키가 있을 때만 초기화
        try:
            self.generator = TFTGenerator()
            print("[OK] Gemini API 연결 성공")
        except ValueError:
            self.generator = None
            print("[!] API 키 없음 (검색만 가능)")
        
        print("=== 초기화 완료 ===\n")
    
    def process_video(
        self,
        video_url: str,
        metadata: dict
    ) -> int:
        """
        유튜브 영상 처리 및 Vector Store에 저장
        
        Args:
            video_url: 유튜브 URL
            metadata: 기본 메타데이터 (시즌, 패치, 조합명 등)
            
        Returns:
            생성된 청크 개수
        """
        print(f"\n=== 영상 처리 시작 ===")
        print(f"URL: {video_url}")
        
        # 1. 자막 추출 및 정제
        try:
            text = self.youtube_processor.process_video(video_url)
        except Exception as e:
            print(f"영상 처리 실패: {e}")
            return 0
        
        # 2. Chunking
        chunks = self.chunker.create_chunks_with_metadata(text, metadata)
        print(f"생성된 청크: {len(chunks)}개")
        
        # 3. Vector Store에 추가
        self.vector_store.add_chunks(chunks)
        
        print("=== 영상 처리 완료 ===\n")
        return len(chunks)
    
    def query(
        self,
        question: str,
        game_state: GameState = None,
        show_sources: bool = True
    ) -> dict:
        """
        질문에 답변
        
        Args:
            question: 사용자 질문
            game_state: 게임 상태 (선택)
            show_sources: 출처 정보 표시 여부
            
        Returns:
            {
                "answer": "답변",
                "sources": [...],
                "retrieved_chunks": [...]
            }
        """
        print(f"\n=== 질문 처리 ===")
        print(f"질문: {question}")
        
        # 1. 검색
        results = self.retriever.retrieve(
            query=question,
            game_state=game_state
        )
        
        if not results:
            return {
                "answer": "죄송합니다. 관련된 전략을 찾을 수 없습니다. 다른 방식으로 질문해주시겠어요?",
                "sources": [],
                "retrieved_chunks": []
            }
        
        # 2. 컨텍스트 포맷팅
        context = self.retriever.format_context(results)
        
        # 3. 답변 생성
        if self.generator:
            response_data = self.generator.generate_with_sources(
                question=question,
                context=context,
                search_results=results,
                game_state=game_state
            )
        else:
            # API 키 없으면 검색 결과만 반환
            response_data = {
                "answer": "⚠ Claude API 키가 설정되지 않아 검색 결과만 제공합니다.\n\n" + context,
                "sources": []
            }
        
        response_data["retrieved_chunks"] = results
        
        return response_data
    
    def interactive_mode(self):
        """대화형 모드"""
        print("\n" + "="*50)
        print("롤체 RAG 시스템 - 대화형 모드")
        print("="*50)
        print("질문을 입력하세요 (종료: 'exit' 또는 'quit')")
        print("="*50 + "\n")
        
        # 게임 상태 입력 받기 (선택)
        use_game_state = input("게임 상태 정보를 입력하시겠습니까? (y/n): ").lower() == 'y'
        
        game_state = None
        if use_game_state:
            try:
                round_input = input("현재 라운드 (예: 3-2): ")
                level = int(input("레벨: "))
                gold = int(input("골드: "))
                hp = int(input("체력: "))
                
                game_state = GameState(
                    round=round_input,
                    level=level,
                    gold=gold,
                    hp=hp,
                    question=""  # 나중에 채워짐
                )
                print("\n게임 상태가 설정되었습니다.\n")
            except Exception as e:
                print(f"게임 상태 입력 오류: {e}")
                print("게임 상태 없이 진행합니다.\n")
        
        while True:
            try:
                question = input("\n질문> ").strip()
                
                if question.lower() in ['exit', 'quit', '종료']:
                    print("종료합니다.")
                    break
                
                if not question:
                    continue
                
                if game_state:
                    game_state.question = question
                
                # 답변 생성
                response = self.query(
                    question=question,
                    game_state=game_state,
                    show_sources=True
                )
                
                print("\n" + "-"*50)
                print("답변:")
                print("-"*50)
                print(response["answer"])
                
                if response.get("sources"):
                    print("\n" + "-"*50)
                    print("참고 출처:")
                    print("-"*50)
                    for i, source in enumerate(response["sources"], 1):
                        print(f"{i}. {source['video_source']} ({source['timestamp']})")
                        print(f"   단계: {source['game_stage']}, 전략: {source['strategy_type']}")
                
            except KeyboardInterrupt:
                print("\n\n종료합니다.")
                break
            except Exception as e:
                print(f"\n오류 발생: {e}")
    
    def get_stats(self):
        """시스템 통계"""
        stats = self.vector_store.get_collection_stats()
        print("\n=== 시스템 통계 ===")
        print(f"컬렉션: {stats['collection_name']}")
        print(f"저장된 전략 청크: {stats['total_chunks']}개")
        print(f"저장 경로: {stats['persist_directory']}")
        print("==================\n")


def main():
    parser = argparse.ArgumentParser(description="롤체 RAG 시스템")
    parser.add_argument(
        "--mode",
        choices=["process", "query", "interactive", "stats"],
        required=True,
        help="실행 모드"
    )
    parser.add_argument(
        "--video_url",
        help="처리할 유튜브 URL (process 모드)"
    )
    parser.add_argument(
        "--metadata_file",
        help="메타데이터 JSON 파일 (process 모드)"
    )
    parser.add_argument(
        "--question",
        help="질문 (query 모드)"
    )
    
    args = parser.parse_args()
    
    # 시스템 초기화
    system = TFTRAGSystem()
    
    if args.mode == "process":
        # 영상 처리 모드
        if not args.video_url:
            print("오류: --video_url이 필요합니다.")
            return
        
        # 메타데이터 로드
        if args.metadata_file:
            try:
                with open(args.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except FileNotFoundError:
                print(f"경고: 메타데이터 파일 '{args.metadata_file}'을 찾을 수 없습니다.")
                print("기본 메타데이터를 사용합니다.")
                metadata = {
                    'season': config.CURRENT_SEASON,
                    'patch': config.CURRENT_PATCH,
                    'video_source': args.video_url.split('=')[-1] if '=' in args.video_url else 'unknown',
                    'composition_name': '미정',
                    'difficulty': '초보'
                }
        else:
            # 기본 메타데이터
            metadata = {
                'season': config.CURRENT_SEASON,
                'patch': config.CURRENT_PATCH,
                'video_source': args.video_url.split('=')[-1] if '=' in args.video_url else 'unknown',
                'composition_name': '미정',
                'difficulty': '초보'
            }
        
        system.process_video(args.video_url, metadata)
    
    elif args.mode == "query":
        # 질문 모드
        if not args.question:
            print("오류: --question이 필요합니다.")
            return
        
        response = system.query(args.question)
        print("\n답변:")
        print(response["answer"])
    
    elif args.mode == "interactive":
        # 대화형 모드
        system.interactive_mode()
    
    elif args.mode == "stats":
        # 통계 모드
        system.get_stats()


if __name__ == "__main__":
    main()
