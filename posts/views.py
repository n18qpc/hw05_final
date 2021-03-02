from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

POSTS_PER_PAGE = 10


@cache_page(20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "new_post.html", {
        "form": form,
        "is_edit": False,
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author,
            user=request.user
        ).exists()
    else:
        following = False
    return render(request, "profile.html", {
        "author": author,
        "page": page,
        "paginator": paginator,
        "count_posts": posts.count,
        "following": following
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    count_posts = post.author.posts.count
    form = CommentForm()
    return render(
        request,
        "post.html",
        {
            "post": post,
            "count_posts": count_posts,
            "author": post.author,
            "comments": comments,
            "form": form
        }
    )


@login_required
def post_edit(request, username, post_id):
    post_edit = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user.username != username:
        return redirect("post", username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post_edit)
    if form.is_valid():
        form.save()
        return redirect("post", username, post_id)
    return render(request, "new_post.html", {
        "username": username,
        "is_edit": True,
        "form": form,
        "post_edit": post_edit,
    })


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {
        "page": page,
        "paginator": paginator
    })


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        following_user = get_object_or_404(User, username=username)
        Follow.objects.get_or_create(user=request.user, author=following_user)
    return redirect("profile", username)


@login_required
def profile_unfollow(request, username):
    unfollowing_user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=unfollowing_user).delete()
    return redirect("profile", username)
