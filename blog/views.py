from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView
from django.core.mail import send_mail

# Create your views here.
def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 2) # 2 posts in each page
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.get_page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts':posts})

class PostListView(ListView):
    """
    Alternative post list view 
    """
    queryset = Post.published.all() 
    context_object_name = 'posts' 
    paginate_by = 2
    template_name = 'blog/post/list.html' 

        
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, 
        status=Post.Status.PUBLISHED, 
        slug=post,
        publish__year=year, 
        publish__month=month, 
        publish__day=day
    ) 
    return render(request,
                      'blog/post/detail.html',
                      {'post': post}
        )

from .forms import EmailPostForm 

def post_share(request, post_id): 
    # Retrieve post by id 
    post = get_object_or_404( 
        Post, 
        id=post_id, 
        status=Post.Status.PUBLISHED
    )
    sent = False 
    if request.method == 'POST':
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data()
            # ... send email
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}'s comments: {cd['comments']}"
            send_mail(
                subject=subject, 
                message=message, 
                from_email=None, 
                recipient_list=[cd['to']] ) 
            sent = True
    else:
        form = EmailPostForm()
        return render(
            request,
            'blog/post/share.html',
            {'post': post,
             'form': form,
             'sent': sent
             }
        )
    