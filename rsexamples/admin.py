from django.contrib import admin
from .models import BoatModel, Article, Comment


@admin.register(BoatModel)
class BoatsAdmin(admin.ModelAdmin):
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
