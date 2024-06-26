from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count 
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity

class PostListView(ListView):
    """
    Альтернатиыное представление списка постов
    """
    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 3
    template_name = "blog/post/list.html"

    

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        #Если page_number не целое число, то выдать первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        #Если page_number находится вне диапозона, то выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(request, "blog/post/list.html", {"posts": posts,
                                                   "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, 
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    #Список активыных комментариев к этом посту
    comments = post.comments.filter(active=True)
    #Форма для комментирования пользователями
    form = CommentForm()

    #Список схожих постов
    post_tags_ids = post.tags.values_list("id", flat=True) #извлекается список идентификаторов, flat преобразует кортежи в одиночные значения
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "-publish")[:4] # генерим поле same_tags

    return render(request, "blog/post/detail.html", {"post": post,
                                                     "comments": comments,
                                                     "form": form,
                                                     "similar_posts": similar_posts})


def post_share(request, post_id):
    #Извлечь пост по идентификатору id
    post = get_object_or_404(Post, 
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    
    sent = False
    
    if request.method == "POST":
        #Форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data

            post_url = request.build_absolute_uri( # используем, чтобы сформировать полный url-адрес(uri), включая HTTP и хост
                post.get_absolute_url())
            subject = f"{cd["name"]} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd["name"]}'s comments: {cd["comments"]}"
            send_mail(subject, message, "primpyto@gmail.com", [cd["to"]])
            sent = True
            
            # ... отправить электронное письмо
    else:
        form = EmailPostForm()
    return render(request, "blog/post/share.html", {"post": post, 
                                                    "form": form,
                                                    "sent": sent})


@require_POST #разрешён только POST-запрос  
def post_comment(request, post_id):
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    comment = None
    #Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в БД
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # сохранить комментарий в БД
        comment.save()
    
    return render(request, "blog/post/comment.html",
                  {"post": post,
                   "form": form,
                   "comment": comment})

def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            results = Post.published.annotate(
               similarity = TrigramSimilarity("title", query),
            ).filter(similarity__gt=0.1).order_by("-similarity")


    return render(request,
                  "blog/post/search.html",
                  {"form": form,
                   "query": query,
                   "results": results })
