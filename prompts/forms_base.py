"""
재사용 가능한 Form 기반 클래스 및 Mixin
HTMX 실시간 폼 검증을 위한 공통 기능 제공
"""

from datetime import date
from django import forms
from django.core.exceptions import ValidationError


class FieldDefaultValueGenerator:
    """필드 타입별 기본값 생성 유틸리티"""

    DEFAULT_VALUES = {
        "CharField": "temporary_value",
        "TextField": "temporary content " * 10,  # 50자 이상
        "EmailField": "temp@example.com",
        "URLField": "https://example.com",
        "SlugField": "temp-slug",
        "IntegerField": 0,
        "FloatField": 0.0,
        "DecimalField": 0.0,
        "BooleanField": False,
        "DateField": lambda: date.today(),
        "DateTimeField": lambda: date.today(),
        "TimeField": "00:00:00",
        "DurationField": "00:00:00",
        "FileField": None,
        "ImageField": None,
        "JSONField": {},
        "UUIDField": None,
    }

    @classmethod
    def get_default_value(cls, field, instance=None, field_name=None):
        """
        필드에 대한 기본값 반환

        Args:
            field: Django Form Field 인스턴스
            instance: 모델 인스턴스 (수정 모드)
            field_name: 필드명

        Returns:
            필드 타입에 맞는 기본값
        """
        # 인스턴스가 있고 필드값이 있으면 기존 값 사용
        if instance and field_name and hasattr(instance, field_name):
            return getattr(instance, field_name)

        # ChoiceField 특별 처리
        if isinstance(field, forms.ChoiceField):
            choices = list(field.choices)
            if choices:
                # 빈 값 옵션 제외
                valid_choices = [c for c in choices if c[0]]
                return valid_choices[0][0] if valid_choices else ""

        # CharField의 Textarea 위젯 확인
        if isinstance(field, forms.CharField):
            if isinstance(field.widget, forms.Textarea):
                return cls.DEFAULT_VALUES.get("TextField", "")
            return cls.DEFAULT_VALUES.get("CharField", "")

        # 필드 타입명으로 기본값 찾기
        field_type = field.__class__.__name__
        default = cls.DEFAULT_VALUES.get(field_type, "")

        # 함수인 경우 실행
        if callable(default):
            return default()

        return default


class HTMXValidationMixin:
    """
    HTMX 실시간 필드 검증 기능을 제공하는 Mixin

    사용법:
        class MyForm(HTMXValidationMixin, forms.ModelForm):
            validation_url_name = 'app_name:validate_field'
            # 또는
            def get_validation_url(self, field_name):
                return custom_url_logic
    """

    # URL reverse를 위한 URL 이름 (예: 'app_name:validate_field')
    validation_url_name = None

    # 추가 URL kwargs (필요시)
    validation_url_kwargs = {}

    # HTMX 트리거 설정
    htmx_trigger = "blur, change delay:500ms"

    def get_validation_url_kwargs(self, field_name):
        """
        URL reverse를 위한 kwargs 생성

        하위 클래스에서 오버라이드하여 추가 파라미터 제공 가능
        """
        base_kwargs = {"field_name": field_name}
        base_kwargs.update(self.validation_url_kwargs)
        return base_kwargs

    def get_validation_url(self, field_name):
        """
        Django URL reverse를 사용한 검증 URL 생성

        하위 클래스에서 오버라이드하여 커스텀 로직 구현 가능
        """
        if self.validation_url_name:
            from django.urls import reverse, NoReverseMatch

            kwargs = self.get_validation_url_kwargs(field_name)

            try:
                # kwargs 방식 우선 시도
                return reverse(self.validation_url_name, kwargs=kwargs)
            except (NoReverseMatch, TypeError):
                try:
                    # args 방식 fallback
                    return reverse(self.validation_url_name, args=[field_name])
                except NoReverseMatch:
                    import warnings

                    warnings.warn(
                        f"Could not reverse URL '{self.validation_url_name}' "
                        f"for field '{field_name}'. Make sure the URL pattern exists "
                        f"and accepts a 'field_name' parameter."
                    )
                    return None
        return None

    def get_htmx_trigger(self):
        """
        HTMX 트리거 설정 반환

        하위 클래스에서 오버라이드하여 커스터마이징 가능
        """
        return self.htmx_trigger

    def get_htmx_attributes(self, field_name):
        """
        필드별 HTMX 속성 딕셔너리 반환

        하위 클래스에서 오버라이드하여 추가 속성 제공 가능
        """
        url = self.get_validation_url(field_name)
        if not url:
            return {}

        return {
            "hx-post": url,
            "hx-trigger": self.get_htmx_trigger(),
            "hx-target": f"#error-{field_name}",
            "hx-swap": "outerHTML",
            "hx-indicator": f"#loading-{field_name}",
        }

    def get_field_default_value(self, field_name, field):
        """
        필드 타입에 따른 기본값 생성

        하위 클래스에서 오버라이드하여 커스텀 기본값 제공 가능
        """
        instance = getattr(self, "instance", None)
        return FieldDefaultValueGenerator.get_default_value(field, instance=instance, field_name=field_name)

    def validate_single_field(self, field_name, value):
        """
        단일 필드만 검증하는 메서드

        Args:
            field_name: 검증할 필드명
            value: 검증할 값

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # 유효한 필드인지 확인
        if field_name not in self.fields:
            return False, "유효하지 않은 필드입니다."

        # 폼 데이터 준비
        form_data = {field_name: value}

        # 다른 필수 필드들의 기본값 추가
        for fname, field in self.fields.items():
            if fname != field_name and field.required:
                form_data[fname] = self.get_field_default_value(fname, field)

        # 임시 폼 생성하여 검증
        instance = getattr(self, "instance", None)
        # ModelForm인 경우 instance 전달, 일반 Form인 경우는 전달하지 않음
        if instance is not None and hasattr(self.__class__, "_meta"):
            temp_form = self.__class__(form_data, instance=instance)
        else:
            temp_form = self.__class__(form_data)

        # 필드 검증
        try:
            # 폼 전체 유효성 검사 실행
            temp_form.is_valid()

            # 특정 필드 에러 확인
            if field_name in temp_form.errors:
                return False, temp_form.errors[field_name][0]

            # clean_<field_name> 메서드가 있으면 추가 검증
            clean_method = getattr(temp_form, f"clean_{field_name}", None)
            if clean_method and hasattr(temp_form, "cleaned_data") and field_name in temp_form.cleaned_data:
                try:
                    # clean 메서드 호출
                    result = clean_method()
                    temp_form.cleaned_data[field_name] = result
                except ValidationError as e:
                    # ValidationError의 메시지 추출
                    if hasattr(e, "message"):
                        return False, e.message
                    elif hasattr(e, "messages"):
                        return False, e.messages[0] if e.messages else str(e)
                    else:
                        return False, str(e)
                except Exception as e:
                    return False, str(e)

            return True, None

        except Exception as e:
            return False, str(e)

    def setup_htmx_attributes(self, field_names=None):
        """
        폼 필드에 HTMX 속성 자동 추가

        Args:
            field_names: HTMX를 적용할 필드명 리스트 (None이면 모든 필드)
        """
        if field_names is None:
            field_names = self.fields.keys()

        for field_name in field_names:
            if field_name in self.fields:
                htmx_attrs = self.get_htmx_attributes(field_name)
                if htmx_attrs:
                    self.fields[field_name].widget.attrs.update(htmx_attrs)

    def get_validation_status(self):
        """
        모든 필드의 검증 상태 반환

        Returns:
            dict: {field_name: {'valid': bool, 'error': str or None}}
        """
        status = {}
        for field_name in self.fields:
            value = self.data.get(field_name, "")
            is_valid, error = self.validate_single_field(field_name, value)
            status[field_name] = {"valid": is_valid, "error": error}
        return status


class BaseHTMXModelForm(HTMXValidationMixin, forms.ModelForm):
    """
    HTMX 검증 기능이 포함된 ModelForm 기본 클래스

    사용법:
        class MyForm(BaseHTMXModelForm):
            class Meta:
                model = MyModel
                fields = ['field1', 'field2']
    """

    pass


class BaseHTMXForm(HTMXValidationMixin, forms.Form):
    """
    HTMX 검증 기능이 포함된 일반 Form 기본 클래스

    사용법:
        class MyForm(BaseHTMXForm):
            field1 = forms.CharField()
            field2 = forms.EmailField()
    """

    pass
