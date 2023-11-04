from django.db import models
from django.utils import timezone


# Create your models here.
class Post(models.Model):  # модель данных для постов блога
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)  # короткая метка
    body = models.TextField()  # тело поста
    publish = models.DateTimeField(default=timezone.now)  # дата и время публикации поста
    created = models.DateTimeField(auto_now_add=True)  # дата и время создания поста
    updated = models.DateTimeField(auto_now=True)  # последняя дата и время обновления поста

    class Meta:
        ordering = ['-publish']  # обратная сортировка по полю publish
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title
