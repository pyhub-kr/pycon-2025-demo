from django.contrib import admin
from .models import Song, Artist, Album


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["uid", "name"]
    search_fields = ["name"]


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["uid", "name"]
    search_fields = ["name"]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["rank", "title", "artist", "album", "likes", "release_date"]
    list_filter = ["release_date", "genre"]
    search_fields = ["title", "artist__name", "album__name"]
    ordering = ["rank"]
