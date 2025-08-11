from django.views.generic import ListView
from .models import Song


class SongListView(ListView):
    model = Song
    template_name = 'melon/songs.html'
    paginate_by = 10
    
    def get_queryset(self):
        """최적화된 쿼리셋 반환"""
        return Song.objects.select_related('artist', 'album').all()
    
    def get_template_names(self):
        """HTMX 요청에 따라 다른 템플릿 반환"""
        if self.request.headers.get('HX-Request'):
            return ['melon/partials/song_list.html']
        return super().get_template_names()


# FBV를 CBV의 as_view()로 대체
song_list = SongListView.as_view()
