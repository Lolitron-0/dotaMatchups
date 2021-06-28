from django.contrib import admin
from .models import Article,Comment,Match, FullData

admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Match)
admin.site.register(FullData)
