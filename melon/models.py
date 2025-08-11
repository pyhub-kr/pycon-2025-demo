from django.db import models


class Artist(models.Model):
    uid = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Album(models.Model):
    uid = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=300)
    cover_image_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Song(models.Model):
    uid = models.BigIntegerField(unique=True)  # 곡일련번호
    rank = models.IntegerField()  # 순위
    title = models.CharField(max_length=300)  # 곡명
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="songs")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="songs")
    lyrics = models.TextField(blank=True)  # 가사
    genre = models.JSONField(default=list)  # 장르 리스트
    release_date = models.DateField()  # 발매일
    likes = models.IntegerField(default=0)  # 좋아요

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.rank}. {self.title} - {self.artist.name}"
