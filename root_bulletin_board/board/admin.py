from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from mptt.admin import DraggableMPTTAdmin

from .models import Board, Category, Comment


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    fields = ['title',  'slug', 'content', 'upload', 'post_upload', 'cat', 'tags']
    readonly_fields = ['post_upload']
    prepopulated_fields = {'slug': ('title', )}
    filter_horizontal = ['tags']
    list_display = ('title', 'post_upload', 'time_create', 'is_published', 'cat')
    list_display_links = ('title', )
    ordering = ['-time_create', 'title']
    list_editable = ('is_published', )
    list_per_page = 5
    actions = ['set_published', 'set_draft']
    search_fields = ['title', 'cat__name']
    list_filter = ['cat__name', 'is_published']
    save_on_top = True

    @admin.display(description='Файлы', ordering='content')
    def post_upload(self, board: Board):
        if board.upload:
            return mark_safe(f"<object data='{board.upload.url}' width=50></object>")
        return "Нет загруженных файлов"

    @admin.action(description='Опубликовать выбранные записи')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Board.Status.PUBLISHED)
        self.message_user(request, f'Опубликовано {count} записей')

    @admin.action(description='Снять с публикации выбранные записи')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Board.Status.DRAFT)
        self.message_user(request, f'{count} записей снято с публикации', messages.WARNING)


@admin.register(Category)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'post', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
