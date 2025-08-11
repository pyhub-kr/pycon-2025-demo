"""
프롬프트 모델 필드용 커스텀 validators
재사용 가능한 검증 로직을 모델 레벨에서 적용
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator


# Title 필드 validators
def validate_no_special_chars(value):
    """제목에 특수문자 사용 제한"""
    special_chars = ["<", ">", "/", "\\", "|", "*", "?"]
    for char in special_chars:
        if char in value:
            raise ValidationError(
                f"제목에 {char} 문자를 사용할 수 없습니다.", params={"char": char}, code="invalid_char"
            )


# Content 필드 validators
def validate_prompt_variables(value):
    """프롬프트 변수 패턴 검증 ([변수명] 형식)"""
    pattern = r"\[[^\]]*\]"
    variables = re.findall(pattern, value)

    for var in variables:
        # [과 ] 포함해서 최소 3자
        if len(var) < 3:
            raise ValidationError(
                f"변수 {var}가 너무 짧습니다. 변수명은 최소 1자 이상이어야 합니다.",
                params={"variable": var},
                code="variable_too_short",
            )
        if len(var) > 50:
            raise ValidationError(
                f"변수 {var}가 너무 깁니다. (최대 48자)", params={"variable": var}, code="variable_too_long"
            )


# Tags 필드 validators
def validate_tags_list(value):
    """태그 리스트 검증"""
    # JSONField는 자동으로 list로 변환되므로 타입 체크
    if value is None:
        return  # null 허용

    if not isinstance(value, list):
        raise ValidationError("태그는 리스트 형식이어야 합니다.", code="invalid_type")

    # 태그 개수 제한
    if len(value) > 10:
        raise ValidationError(
            "태그는 최대 10개까지 입력할 수 있습니다.", params={"count": len(value)}, code="too_many_tags"
        )

    # 각 태그 검증
    for i, tag in enumerate(value):
        if not isinstance(tag, str):
            raise ValidationError(
                f"{i+1}번째 태그가 문자열이 아닙니다.",
                params={"index": i + 1, "type": type(tag).__name__},
                code="invalid_tag_type",
            )

        tag = tag.strip()
        if len(tag) < 2:
            raise ValidationError(
                f'태그 "{tag}"가 너무 짧습니다. (최소 2자)', params={"tag": tag}, code="tag_too_short"
            )

        if len(tag) > 20:
            raise ValidationError(f'태그 "{tag}"가 너무 깁니다. (최대 20자)', params={"tag": tag}, code="tag_too_long")


def validate_unique_title(value):
    """
    제목 중복 체크 validator
    주의: 이 validator는 모델의 clean() 메서드에서 사용하는 것이 좋습니다.
    field validator로 사용 시 수정 모드에서 문제가 발생할 수 있습니다.
    """
    from .models import Prompt

    if Prompt.objects.filter(title=value).exists():
        raise ValidationError("이미 존재하는 제목입니다.", code="duplicate_title")


# 편의를 위한 복합 validator 생성 함수
def get_title_validators():
    """Title 필드용 validator 리스트 반환"""
    return [
        MinLengthValidator(5, message="제목은 최소 5자 이상이어야 합니다."),
        MaxLengthValidator(200, message="제목은 200자를 초과할 수 없습니다."),
        validate_no_special_chars,
    ]


def get_content_validators():
    """Content 필드용 validator 리스트 반환"""
    return [
        MinLengthValidator(50, message="프롬프트 내용은 최소 50자 이상이어야 합니다."),
        validate_prompt_variables,
    ]


def get_tags_validators():
    """Tags 필드용 validator 리스트 반환"""
    return [
        validate_tags_list,
    ]
