# from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.core.mail import send_mail
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from blog.forms import EmailPostForm

from blog.models import Post

# Create your views here.


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 3) # 3 posts per page
#     page = request.GET.get('page')
#     try:
#         posts = paginator.page(page)
#     except PageNotAnInteger:
#         # if page is not an integer, deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range, deliver last page of results
#         posts = Paginator.page(paginator.num_pages)
#     return render(request, 'blog/post/list.html', {"page": page, "posts": posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day)
    return render(request, 'blog/post/detail.html', {"post": post})


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
            post_url = request.build_absolute_uri(post.get_absolute_url()) # link to the post detail
            subject = f"{cd['name']} recommends you {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'admin@domain.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {"post": post, "form": form, "sent": sent})
