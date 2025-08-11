from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from .models import Prompt


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

    return render(request, "prompts/partials/prompt_detail.html", {"prompt": prompt})


def toggle_favorite(request, pk):
    """즐겨찾기 토글"""
    if request.method == "POST":
        prompt = get_object_or_404(Prompt, pk=pk)
        prompt.is_favorite = not prompt.is_favorite
        prompt.save()

        return render(request, "prompts/partials/prompt_item.html", {"prompt": prompt})

    return JsonResponse({"error": "Method not allowed"}, status=405)
