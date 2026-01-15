from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class StrategyMetadata(BaseModel):
    """롤체 전략 메타데이터"""
    
    # 필수 정보
    season: str = Field(..., description="시즌 정보 (예: '시즌13')")
    patch: str = Field(..., description="패치 버전 (예: '13.24')")
    game_stage: str = Field(..., description="게임 단계 (예: '2-1', '3-2')")
    strategy_type: str = Field(..., description="전략 유형 (리롤/레벨링/연승/연패/전환 등)")
    
    # 조합 정보
    composition_name: Optional[str] = Field(None, description="조합명 (예: '6도전자')")
    key_champions: List[str] = Field(default_factory=list, description="핵심 챔피언")
    synergies: List[str] = Field(default_factory=list, description="시너지 (예: ['도전자', '결투가'])")
    
    # 아이템 정보
    core_items: List[str] = Field(default_factory=list, description="핵심 아이템")
    
    # 난이도 & 조건
    difficulty: Literal["입문", "초보", "중급", "고급"] = Field("초보", description="난이도")
    prerequisites: Optional[str] = Field(None, description="전제 조건 (예: '2성 야스오 필수')")
    
    # 출처 정보
    video_source: str = Field(..., description="출처 영상 (유튜버명_영상ID)")
    timestamp: Optional[str] = Field(None, description="영상 타임스탬프 (예: '3:24-5:18')")
    created_at: datetime = Field(default_factory=datetime.now, description="데이터 생성 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "season": "시즌13",
                "patch": "13.24",
                "game_stage": "2-1",
                "strategy_type": "리롤",
                "composition_name": "6도전자",
                "key_champions": ["야스오", "요네"],
                "synergies": ["도전자", "결투가"],
                "core_items": ["무한의 대검", "최후의 속삭임"],
                "difficulty": "초보",
                "prerequisites": "2성 야스오 또는 요네 1개 이상",
                "video_source": "롤체유튜버_abc123",
                "timestamp": "3:24-5:18"
            }
        }


class GameState(BaseModel):
    """현재 게임 상태"""
    
    round: str = Field(..., description="현재 라운드 (예: '3-2')")
    level: int = Field(..., ge=1, le=10, description="현재 레벨")
    gold: int = Field(..., ge=0, description="현재 골드")
    hp: int = Field(..., ge=0, le=100, description="현재 체력")
    
    current_champions: List[str] = Field(default_factory=list, description="현재 보유 챔피언")
    current_synergies: List[str] = Field(default_factory=list, description="현재 활성 시너지")
    bench_champions: List[str] = Field(default_factory=list, description="벤치 챔피언")
    
    items: List[str] = Field(default_factory=list, description="보유 아이템")
    
    win_streak: int = Field(0, description="연승 횟수")
    lose_streak: int = Field(0, description="연패 횟수")
    
    question: str = Field(..., description="사용자 질문")
    
    class Config:
        json_schema_extra = {
            "example": {
                "round": "3-2",
                "level": 5,
                "gold": 32,
                "hp": 78,
                "current_champions": ["야스오", "요네", "제드"],
                "current_synergies": ["도전자 2", "결투가 2"],
                "bench_champions": ["세트", "아리"],
                "items": ["무한의 대검", "B.F. 대검"],
                "win_streak": 0,
                "lose_streak": 3,
                "question": "연패 중인데 리롤해야 할까요?"
            }
        }
