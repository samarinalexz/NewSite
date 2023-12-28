from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView, DeleteView
from requests import post

from .forms import AddPostForm, UploadFileForm, CommentForm
from .models import Board, Category, TagPost, UploadFiles, Comment
from .utils import DataMixin


class BoardHome(DataMixin, ListView):
    template_name = 'board/index.html'
    context_object_name = 'posts'
    title_page = "Главная страница"
    cat_selected = 0

    def get_queryset(self):
        return Board.published.all().select_related('cat')


@login_required
def about(request):
    contact_list = Board.published.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'board/about.html',
                  {'title': 'О сайте', 'page_obj': page_obj})


class ShowPost(DataMixin, DetailView):
    template_name = 'board/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        return self.get_mixin_context(context, title=context['post'].title)

    def get_object(self, queryset=None):
        return get_object_or_404(Board.published, slug=self.kwargs[self.slug_url_kwarg])


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'board/addpage.html'
    title_page = 'Создать объявление'

    def form_valid(self, form):
        b = form.save(commit=False)
        b.author = self.request.user
        return super().form_valid(form)


class UpdatePage(DataMixin, UpdateView):
    model = Board
    fields = ['title', 'content', 'upload', 'img', 'is_published', 'cat']
    template_name = 'board/addpage.html'
    success_url = reverse_lazy('home')
    title_page = 'Редактировать объявление'
    permission_required = 'board.change_board'


class DeletePage(DataMixin, DeleteView):
    model = Board
    template_name = 'board/deletepage.html'
    success_url = reverse_lazy('home')
    title_page = 'Удалить объявление'


def contact(request):
    return HttpResponse('Обратная связь')


def login(request):
    return HttpResponse('Авторизация')


class BoardCategory(DataMixin, ListView):
    template_name = 'board/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Board.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat = context['posts'][0].cat
        return self.get_mixin_context(context,
                                      title='Категория -' + cat.name,
                                      cat_selected=cat.pk,
                                      )


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


class TagPostList(DataMixin, ListView):
    template_name = 'board/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: ' + tag.tag,)

    def get_queryset(self):
        return Board.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')


def comment(request, slug):
    template_name = 'board/post.html'
    post = get_object_or_404(Board, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form})

