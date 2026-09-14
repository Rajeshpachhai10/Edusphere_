from django.contrib import admin
from .models import Thread, Post


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fields = ['author', 'body', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'author', 'is_pinned', 'reply_count', 'created_at']
    list_filter = ['is_pinned', 'course', 'created_at']
    search_fields = ['title', 'body', 'author__email']
    list_editable = ['is_pinned']
    inlines = [PostInline]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['body', 'author__email', 'thread__title']