from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from openai import OpenAI
from .models import Prompt
from .forms import PromptForm


def prompt_list(request):
    """프롬프트 목록 및 검색 페이지"""
    prompts = Prompt.objects.all()
    categories = Prompt.CATEGORY_CHOICES

    # 카테고리 필터
    category = request.GET.get("category")
    if category:
        prompts = prompts.filter(category=category)

    context = {
        "prompts": prompts,
        "categories": categories,
        "selected_category": category,
    }
    return render(request, "prompts/prompt_list.html", context)


def search_prompts(request):
    """실시간 검색 자동완성 AJAX 뷰"""
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")

    # 기본 쿼리셋
    prompts = Prompt.objects.all()

    # 검색어가 있으면 필터링
    if query:
        prompts = prompts.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__icontains=query))

    # 카테고리 필터
    if category:
        prompts = prompts.filter(category=category)

    # 자동완성은 최대 10개까지
    prompts = prompts[:10]

    # # 검색어가 있으면 검색 결과, 없으면 인기 프롬프트
    # if not query:
    #     prompts = Prompt.objects.filter(is_favorite=True)[:5]

    context = {
        "prompts": prompts,
        "query": query,
        "selected_category": category,
        "categories": Prompt.CATEGORY_CHOICES,
    }

    return render(request, "prompts/partials/search_results.html", context)


def prompt_detail(request, pk):
    """프롬프트 상세 보기"""
    prompt = get_object_or_404(Prompt, pk=pk)
    prompt.increment_usage()  # 사용 횟수 증가

    return render(
        request,
        "prompts/partials/prompt_detail.html",
        {
            "prompt": prompt,
        },
    )


def toggle_favorite(request, pk):
    """즐겨찾기 토글"""
    if request.method == "POST":
        prompt = get_object_or_404(Prompt, pk=pk)
        prompt.is_favorite = not prompt.is_favorite
        prompt.save()

        return render(request, "prompts/partials/prompt_item.html", {"prompt": prompt})

    return JsonResponse({"error": "Method not allowed"}, status=405)


def prompt_create(request):
    """프롬프트 생성"""
    if request.method == "POST":
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.save()
            return redirect("prompts:list")
    else:
        form = PromptForm()

    # Alpine.js 버전 사용 (커스텀 JS 제거)
    return render(request, "prompts/prompt_form.html", {"form": form})


def prompt_update(request, pk):
    """프롬프트 수정"""
    prompt = get_object_or_404(Prompt, pk=pk)

    if request.method == "POST":
        form = PromptForm(request.POST, instance=prompt)
        if form.is_valid():
            form.save()
            return redirect("prompts:list")
    else:
        form = PromptForm(instance=prompt)

    # Alpine.js 버전 사용 (커스텀 JS 제거)
    return render(request, "prompts/prompt_form.html", {"form": form})


@require_http_methods(["POST"])
@csrf_exempt
def validate_field(request, field_name):
    """개별 필드 실시간 유효성 검사 - 리팩토링된 버전"""

    # 폼 인스턴스 가져오기 (수정 모드 지원)
    instance_pk = request.POST.get("instance_pk")
    instance = None
    if instance_pk:
        try:
            instance = Prompt.objects.get(pk=instance_pk)
        except Prompt.DoesNotExist:
            pass

    # PromptForm 생성 (인스턴스 전달)
    form = PromptForm(instance=instance)

    # 필드 값 가져오기
    field_value = request.POST.get(field_name, "")

    # 단일 필드 검증 수행
    is_valid, error_message = form.validate_single_field(field_name, field_value)

    return render(
        request,
        "prompts/partials/field_error.html",
        {"field_name": field_name, "error": error_message if not is_valid else None},
    )


def poem_view(request):
    """AI 시 생성 통합 뷰"""
    if request.method == "POST":
        # 시 생성 처리
        message = request.POST.get("message", "").strip()

        if message:
            try:
                # 시 작성을 위한 프롬프트
                poem_prompt = f"""주제 또는 영감: {message}

위 주제로 한국어로 아름답고 감성적인 시를 작성해주세요.
- 4-8줄 정도의 짧은 시
- 은유와 비유를 활용
- 감성적이고 서정적인 표현
- 한국어의 아름다움을 살린 표현"""

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": poem_prompt}],
                    max_tokens=200,
                    temperature=0.9,  # 창의성을 위해 온도 높임
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                ai_response = f"오류가 발생했습니다: {str(e)}"
        else:
            ai_response = "시의 주제를 입력해주세요."

        # POST 요청은 항상 부분 템플릿 반환 (HTMX 응답용)
        return render(request, "prompts/partials/poem_response.html", {"poem": ai_response, "theme": message})

    # GET 요청 - 전체 페이지 표시
    return render(request, "prompts/poem.html")
