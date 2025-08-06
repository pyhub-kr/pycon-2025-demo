"""
Django-independent core classes for the roleplay application.
This module can be used with any Python framework.
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Literal, cast

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel


class Difficulty(Enum):
    """난이도 레벨"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class UsageInfo:
    """OpenAI API 사용량 정보"""

    input_tokens: int
    output_tokens: int

    def __str__(self) -> str:
        """토큰 사용량을 읽기 쉬운 문자열로 반환"""
        return f"Input: {self.input_tokens}, Output: {self.output_tokens}, Total: {self.total_tokens}"

    @property
    def total_tokens(self) -> int:
        """총 토큰 수 반환"""
        return self.input_tokens + self.output_tokens


class ChatResponse(BaseModel):
    """채팅 응답을 위한 간소화된 모델"""

    text: str  # AI의 응답 텍스트
    suggested_phrases: list[str]  # 이어서 쓸 수 있는 표현들 (3-5개)
    usage: Optional[UsageInfo] = None  # API 사용량 정보

    def to_dict(self) -> dict:
        """JSON 직렬화 가능한 dict로 변환"""
        return self.model_dump(mode="json")

    def __str__(self) -> str:
        """문자열로 변환 시 text 반환"""
        return self.text


@dataclass
class Message:
    """대화 메시지를 나타내는 데이터 클래스"""

    role: Literal["user", "assistant", "system"]
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    usage: Optional[UsageInfo] = None  # Assistant 메시지인 경우 사용량 정보 포함


class BaseChatConfig(ABC):
    """모든 채팅 설정의 추상 기반 클래스"""

    @abstractmethod
    def build_system_prompt(self) -> str:
        """시스템 프롬프트 생성 - 모든 서브클래스에서 구현 필수"""
        pass


@dataclass(frozen=True)
class RolePlayChatConfig(BaseChatConfig):
    """역할극 채팅 설정"""

    language: str
    user_role: str
    gpt_role: str
    difficulty: Difficulty
    role_template: str  # 역할극 프롬프트 템플릿

    SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant supporting people learning **{language}**. 
Please assume that the user you are assisting is **{difficulty}** in {language}.

User context: **{user_role}**
Assistant role: **{gpt_role}**

{role_template}

IMPORTANT INSTRUCTIONS:
1. Always respond according to the context and role
2. Keep your responses natural and conversational
3. Use appropriate level of language complexity based on the user's proficiency
4. Additionally provide 3-5 similar or follow-up phrases that the user could use to continue the conversation"""

    @property
    def difficulty_description(self) -> str:
        """난이도를 영어 설명으로 변환"""
        mapping = {
            Difficulty.BEGINNER: "a beginner",
            Difficulty.INTERMEDIATE: "an intermediate learner",
            Difficulty.ADVANCED: "an advanced learner",
        }
        return mapping.get(self.difficulty, "a beginner")

    def build_system_prompt(self) -> str:
        """완전한 시스템 프롬프트 생성"""
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            language=self.language,
            difficulty=self.difficulty_description,
            user_role=self.user_role,
            gpt_role=self.gpt_role,
            role_template=self.role_template,
        )


@dataclass(frozen=True)
class SimpleChatConfig(BaseChatConfig):
    """단순 지시사항 기반 채팅 설정"""

    instruction: str

    def build_system_prompt(self) -> str:
        """단순히 지시사항을 그대로 반환"""
        return self.instruction


class ChatService:
    """Framework-independent chat service"""

    def __init__(
        self,
        config: BaseChatConfig,
        chat_history_store: Optional["BaseChatHistoryStore"] = None,
        api_key: str = None,
        model: str = "gpt-4o",
        temperature: float = 1.0,
        max_tokens: int = 1000,
        verbose: bool = False,
    ):
        self.config = config
        self.chat_history_store = chat_history_store
        self.verbose = verbose

        if api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY", None)
        else:
            self.api_key = api_key

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = OpenAI(api_key=self.api_key)

        # Build system prompt once during initialization
        self._system_prompt = config.build_system_prompt()

    @property
    def system_prompt(self) -> str:
        """Get the system prompt"""
        return self._system_prompt

    def send(self, message: str) -> ChatResponse:
        """OpenAI API 호출 (구조화된 응답)

        Args:
            message: 사용자 메시지

        Returns:
            ChatResponse 객체
        """
        # 사용자 메시지를 저장
        user_message = Message(role="user", content=message)
        if self.chat_history_store:
            self.chat_history_store.add_message(user_message)

        # 메시지 구성
        messages: list[ChatCompletionMessageParam] = []

        if self.system_prompt:
            messages.append(cast(ChatCompletionMessageParam, {"role": "system", "content": self.system_prompt}))

        if self.chat_history_store:
            # 최근 10개 메시지만 컨텍스트로 사용
            recent_messages = self.chat_history_store.get_messages(limit=10)
            messages.extend(
                [
                    cast(ChatCompletionMessageParam, {"role": msg.role, "content": msg.content})
                    for msg in recent_messages
                ]
            )
        else:
            # No history store, just add the current message
            messages.append(cast(ChatCompletionMessageParam, {"role": "user", "content": message}))

        # Verbose 모드 출력
        if self.verbose:
            print("\n" + "=" * 50)
            print("=== VERBOSE MODE ===")
            print("=" * 50)
            print("\n[System Prompt]")
            print("-" * 50)
            print(self.system_prompt)
            print("-" * 50)

            print("\n[Messages to OpenAI API]")
            print("-" * 50)
            for i, msg in enumerate(messages, 1):
                role = msg["role"]
                content = msg["content"]
                # 긴 메시지는 축약해서 표시
                if len(content) > 200 and role != "user":
                    content = content[:200] + "..."
                print(f"{i}. {role}: {content}")
            print("-" * 50)

            print("\n[API Configuration]")
            print(f"- Model: {self.model}")
            print(f"- Temperature: {self.temperature}")
            print(f"- Max Tokens: {self.max_tokens}")
            print("=" * 50 + "\n")

        # OpenAI API 호출 (구조화된 응답)
        completion = self.client.beta.chat.completions.parse(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format=ChatResponse,
        )

        # 구조화된 응답 가져오기
        role_play_response = completion.choices[0].message.parsed

        # 사용량 정보 추출
        usage_info = None
        if hasattr(completion, "usage") and completion.usage:
            usage_info = UsageInfo(
                input_tokens=completion.usage.prompt_tokens,
                output_tokens=completion.usage.completion_tokens,
            )
            role_play_response.usage = usage_info

        # assistant 응답 저장 (text와 usage 정보 포함)
        if self.chat_history_store:
            assistant_message = Message(role="assistant", content=role_play_response.text, usage=usage_info)
            self.chat_history_store.add_message(assistant_message)

        return role_play_response


class BaseChatHistoryStore(ABC):
    """대화 기록 저장소의 추상 인터페이스"""

    @abstractmethod
    def add_message(self, message: Message) -> None:
        """메시지를 저장소에 추가"""
        pass

    @abstractmethod
    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        """저장된 메시지 목록을 가져옴"""
        pass

    @abstractmethod
    def clear_history(self) -> None:
        """모든 대화 기록을 삭제"""
        pass


class InMemoryStore(BaseChatHistoryStore):
    """메모리 기반 대화 기록 저장소"""

    def __init__(self):
        self._messages: list[Message] = []

    def add_message(self, message: Message) -> None:
        self._messages.append(message)

    def get_messages(self, limit: Optional[int] = None) -> list[Message]:
        if limit is None:
            return self._messages.copy()
        return self._messages[-limit:].copy()

    def clear_history(self) -> None:
        self._messages.clear()
