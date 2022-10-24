from django.contrib.postgres.search import SearchRank, SearchQuery, SearchVector
from django.core.mail import send_mail
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from taggit.models import Tag

from blog.forms import CommentForm, EmailPostForm, SearchForm
from blog.models import Post


# Create your views here.


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)  # 3 posts per page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        posts = Paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {"page": page, "posts": posts, "tag": tag})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='PUBLISHED',
                             publish__year=year, publish__month=month, publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # form for users to comment
    form = CommentForm()

    context = {'post': post, 'comments': comments, 'form': form}
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        # if form is submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(
                post.get_absolute_url())  # link to the post detail
            subject = f"{cd['name']} recommends you {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@domain.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {"post": post, "form": form, "sent": sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body', config='spanish')
            search_query = SearchQuery(query, config='spanish')
            results = Post.published.annotate(search=search_vector,
                                              rank=SearchRank(search_vector, search_query)).filter(
                search=search_query).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='PUBLISHED')
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # create a Comment object without saving
        comment = form.save(commit=False)
        # assign the post to the comment
        comment.post = post
        # save the comment to the database
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})
