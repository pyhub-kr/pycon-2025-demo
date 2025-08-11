import json
from datetime import datetime

# 원본 JSON 파일 읽기
with open('/Users/allieus/Work/dump-data/melon/melon-20250811.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixtures = []
artist_set = {}
album_set = {}

# 중복 제거를 위한 집합
for idx, item in enumerate(data):
    # Artist 생성
    artist_uid = item['artist_uid']
    if artist_uid not in artist_set:
        artist_set[artist_uid] = item['artist_name']
        fixtures.append({
            "model": "melon.artist",
            "pk": artist_uid,
            "fields": {
                "uid": artist_uid,
                "name": item['artist_name']
            }
        })
    
    # Album 생성
    album_uid = item['album_uid']
    if album_uid not in album_set:
        album_set[album_uid] = item['album_name']
        fixtures.append({
            "model": "melon.album",
            "pk": album_uid,
            "fields": {
                "uid": album_uid,
                "name": item['album_name'],
                "cover_image_url": item['커버이미지_주소']
            }
        })
    
    # Song 생성
    fixtures.append({
        "model": "melon.song",
        "pk": item['곡일련번호'],
        "fields": {
            "uid": item['곡일련번호'],
            "rank": int(item['순위']),
            "title": item['곡명'],
            "artist": artist_uid,
            "album": album_uid,
            "lyrics": item.get('가사', ''),
            "genre": item.get('장르', []),
            "release_date": item['발매일'],
            "likes": item.get('좋아요', 0)
        }
    })

# Fixture 파일로 저장
with open('melon/fixtures/initial_data.json', 'w', encoding='utf-8') as f:
    json.dump(fixtures, f, ensure_ascii=False, indent=2)