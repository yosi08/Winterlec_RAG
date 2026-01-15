from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict
import re


class YouTubeProcessor:
    """유튜브 영상에서 자막 추출 및 정제"""
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """유튜브 URL에서 video ID 추출"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError(f"유효하지 않은 유튜브 URL: {url}")
    
    @staticmethod
    def get_transcript(video_id: str, language: str = 'ko') -> List[Dict]:
        """
        유튜브 자막 가져오기
        
        Args:
            video_id: 유튜브 영상 ID
            language: 자막 언어 (기본값: 'ko')
            
        Returns:
            자막 리스트 [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
        """
        try:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, 
                languages=[language]
            )
            return transcript
        except Exception as e:
            print(f"자막 추출 실패: {e}")
            # 자동 생성 자막 시도
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=[f'{language}-auto']
                )
                return transcript
            except Exception as e2:
                raise Exception(f"자막을 가져올 수 없습니다: {e2}")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        텍스트 정제
        - 잡담 표현 제거
        - 불필요한 시간 표현 제거
        - 구어체 정리
        """
        # 잡담 패턴
        noise_patterns = [
            r'음+',  # 음음음
            r'어+',  # 어어어
            r'아+',  # 아아아
            r'그+니까+',
            r'뭐+랄까+',
            r'\(웃음\)',
            r'\(박수\)',
            r'ㅋ+',
            r'ㅎ+',
        ]
        
        cleaned = text
        for pattern in noise_patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # 중복 공백 제거
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    @staticmethod
    def merge_transcript(transcript: List[Dict], time_threshold: float = 10.0) -> str:
        """
        자막을 시간 기준으로 병합
        
        Args:
            transcript: 자막 리스트
            time_threshold: 병합 기준 시간 (초)
        """
        if not transcript:
            return ""
        
        merged_text = []
        current_segment = []
        last_time = transcript[0]['start']
        
        for item in transcript:
            # 시간 차이가 크면 새 세그먼트 시작
            if item['start'] - last_time > time_threshold:
                if current_segment:
                    merged_text.append(' '.join(current_segment))
                current_segment = [item['text']]
            else:
                current_segment.append(item['text'])
            
            last_time = item['start']
        
        # 마지막 세그먼트 추가
        if current_segment:
            merged_text.append(' '.join(current_segment))
        
        return '\n\n'.join(merged_text)
    
    def process_video(self, video_url: str) -> str:
        """
        유튜브 영상 전체 처리 파이프라인
        
        Args:
            video_url: 유튜브 URL
            
        Returns:
            정제된 텍스트
        """
        # 1. Video ID 추출
        video_id = self.extract_video_id(video_url)
        print(f"Video ID: {video_id}")
        
        # 2. 자막 가져오기
        transcript = self.get_transcript(video_id)
        print(f"자막 {len(transcript)}개 추출 완료")
        
        # 3. 자막 병합
        merged_text = self.merge_transcript(transcript)
        
        # 4. 텍스트 정제
        cleaned_text = self.clean_text(merged_text)
        print(f"정제 완료: {len(cleaned_text)} 글자")
        
        return cleaned_text


# 사용 예시
if __name__ == "__main__":
    processor = YouTubeProcessor()
    
    # 테스트 URL (실제 롤체 영상으로 교체)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        result = processor.process_video(test_url)
        print("\n=== 처리 결과 (처음 500자) ===")
        print(result[:500])
    except Exception as e:
        print(f"에러: {e}")
