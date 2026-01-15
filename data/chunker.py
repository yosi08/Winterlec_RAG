from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
import re
from data.metadata_schema import StrategyMetadata


class TFTChunker:
    """롤체 전략 단위로 텍스트를 분할"""
    
    # 전략 단위 구분 키워드
    STRATEGY_MARKERS = [
        # 게임 단계
        r'\d-\d',  # 2-1, 3-2 등
        r'초반', r'중반', r'후반',
        
        # 전략 유형
        r'리롤', r'레벨링', r'레벨업',
        r'연승', r'연패',
        r'전환', r'고정',
        
        # 아이템/기물
        r'아이템', r'기물',
        r'이거', r'이렇게',
    ]
    
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 75):
        """
        Args:
            chunk_size: 청크 크기 (토큰 수)
            chunk_overlap: 청크 오버랩 (토큰 수)
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n\n",  # 큰 문단
                "\n\n",    # 문단
                "\n",      # 줄
                ". ",      # 문장
                "! ",
                "? ",
                " ",       # 단어
                ""
            ]
        )
    
    def detect_strategy_type(self, text: str) -> str:
        """텍스트에서 전략 유형 자동 감지"""
        text_lower = text.lower()
        
        if '리롤' in text or '돌림' in text:
            return '리롤'
        elif '레벨' in text:
            return '레벨링'
        elif '연승' in text:
            return '연승'
        elif '연패' in text:
            return '연패'
        elif '전환' in text or '바꾸' in text:
            return '전환'
        elif '고정' in text or '유지' in text:
            return '고정'
        elif '아이템' in text:
            return '아이템 판단'
        else:
            return '기물 선택'
    
    def detect_game_stage(self, text: str) -> str:
        """텍스트에서 게임 단계 자동 감지"""
        # 2-1 형식의 라운드 찾기
        round_pattern = r'\b([2-5])-([1-7])\b'
        matches = re.findall(round_pattern, text)
        
        if matches:
            # 가장 먼저 나온 라운드 반환
            return f"{matches[0][0]}-{matches[0][1]}"
        
        # 라운드 표현이 없으면 키워드로 판단
        if '초반' in text or '크립' in text:
            return '2-1'
        elif '중반' in text:
            return '3-2'
        elif '후반' in text:
            return '4-1'
        
        return '2-1'  # 기본값
    
    def extract_champions(self, text: str) -> List[str]:
        """텍스트에서 챔피언 이름 추출 (간단한 버전)"""
        # 실제로는 롤체 챔피언 목록을 가지고 매칭해야 함
        common_champions = [
            '야스오', '요네', '제드', '아리', '세트', '케넨',
            '볼리베어', '오공', '리산드라', '아지르', '킨드레드'
        ]
        
        found = []
        for champ in common_champions:
            if champ in text:
                found.append(champ)
        
        return found
    
    def create_chunks_with_metadata(
        self,
        text: str,
        base_metadata: Dict
    ) -> List[Dict]:
        """
        텍스트를 청크로 분할하고 각 청크에 메타데이터 부착
        
        Args:
            text: 정제된 텍스트
            base_metadata: 기본 메타데이터 (시즌, 패치, 출처 등)
            
        Returns:
            청크와 메타데이터 리스트
        """
        # 1. 텍스트 분할
        chunks = self.splitter.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            # 2. 각 청크에 대해 메타데이터 생성
            chunk_metadata = base_metadata.copy()
            
            # 자동 감지
            chunk_metadata['strategy_type'] = self.detect_strategy_type(chunk)
            chunk_metadata['game_stage'] = self.detect_game_stage(chunk)
            chunk_metadata['key_champions'] = self.extract_champions(chunk)
            
            result.append({
                'id': f"{base_metadata.get('video_source', 'unknown')}_{i}",
                'text': chunk,
                'metadata': chunk_metadata
            })
        
        return result
    
    def chunk_multiple_videos(
        self,
        videos: List[Dict[str, str]],
        base_metadata_list: List[Dict]
    ) -> List[Dict]:
        """
        여러 영상을 한번에 처리
        
        Args:
            videos: [{"text": "...", "video_id": "abc123"}, ...]
            base_metadata_list: 각 영상의 기본 메타데이터 리스트
            
        Returns:
            모든 청크 리스트
        """
        all_chunks = []
        
        for video, metadata in zip(videos, base_metadata_list):
            chunks = self.create_chunks_with_metadata(
                video['text'],
                metadata
            )
            all_chunks.extend(chunks)
        
        return all_chunks


# 사용 예시
if __name__ == "__main__":
    chunker = TFTChunker(chunk_size=400, chunk_overlap=75)
    
    # 테스트 텍스트
    test_text = """
    2-1에서는 연패 전략을 가져가는 게 좋습니다.
    야스오나 요네가 나오면 바로 픽업하세요.
    
    3-2가 되면 레벨을 올려야 합니다.
    골드가 50 이상이면 리롤을 고려하세요.
    
    아이템은 무한의 대검을 우선으로 만드세요.
    """
    
    base_metadata = {
        'season': '시즌13',
        'patch': '13.24',
        'video_source': 'test_video_001',
        'composition_name': '6도전자',
        'difficulty': '초보'
    }
    
    chunks = chunker.create_chunks_with_metadata(test_text, base_metadata)
    
    print(f"생성된 청크 수: {len(chunks)}\n")
    for i, chunk in enumerate(chunks):
        print(f"=== 청크 {i+1} ===")
        print(f"텍스트: {chunk['text'][:100]}...")
        print(f"전략 유형: {chunk['metadata']['strategy_type']}")
        print(f"게임 단계: {chunk['metadata']['game_stage']}")
        print(f"챔피언: {chunk['metadata']['key_champions']}")
        print()
