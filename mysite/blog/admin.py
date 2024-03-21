from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish',
                    'status']  # задаёт поля модели, которые показываются на странице админ. модели
    list_filter = ['status', 'created', 'publish', 'author'] # показывает сбоку фильтры
    search_fields = ['title', 'body'] # поля, по которым идет поиск, появляется поле поиска
    prepopulated_fields = {'slug': ('title',)} # автоматически заполняет slug по title
    raw_id_fields = ['author'] # более приемлемое отображание для выбора автора
    date_hierarchy = 'publish' # показывает иерархию дат(под поиском)
    ordering = ['status', 'publish'] # сортирует при нажатии на кнопку (критерии сортировки)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "post", "created", "active"]
    list_filter = ["active", "created", "updated"]
    search_fields = ["name", "email", "body"]