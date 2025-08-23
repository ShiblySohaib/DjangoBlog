# Show posts by a specific user
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from .forms import PostForm, ReviewForm
from .models import Post, Review
from django.contrib import messages
from django.db.models import Q, Avg
import threading
from django.template.loader import render_to_string
from datetime import datetime

# Dummy homepage view for redirect after login
@login_required
def home(request):
    query = request.GET.get('q', '')
    posts = Post.objects.all().order_by('-created_at')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(category__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        )
    return render(request, 'posts/home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:home')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:home')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('posts:home')
    return render(request, 'posts/delete_post.html', {'post': post})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    reviews = post.reviews.select_related('user').all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                post=post, user=request.user,
                defaults={
                    'comment': form.cleaned_data['comment'],
                    'rating': form.cleaned_data['rating'],
                }
            )
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = ReviewForm(instance=user_review)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'user_review': user_review,
        'star_range': [1, 2, 3, 4, 5],
    })


def user_posts(request, user_id):
    User = get_user_model()
    profile_user = get_object_or_404(User, pk=user_id)
    query = request.GET.get('q', '')
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query) |
            Q(category__icontains=query)
        )
    return render(request, 'posts/user_posts.html', {'posts': posts, 'profile_user': profile_user, 'request': request})


@login_required
@require_POST
def toggle_favorite(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    if user in post.favorited_by.all():
        post.favorited_by.remove(user)
        favorited = False
    else:
        post.favorited_by.add(user)
        favorited = True
        # Send email in a background thread
        from django.conf import settings
        post_url = request.build_absolute_uri(post.get_absolute_url()) if hasattr(post, 'get_absolute_url') else request.build_absolute_uri(f'/post/{post.pk}/')
        def send_favorite_email():
            html_body = render_to_string(
                'posts/favorite_email.html',
                {
                    'user': user,
                    'post': post,
                    'post_url': post_url,
                    'year': datetime.now().year,
                }
            )
            send_mail(
                subject='You favorited a post!',
                message='Thank you for favoriting the post.',  # fallback plain text
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_body,
                fail_silently=True,
            )
        threading.Thread(target=send_favorite_email).start()
    return JsonResponse({'favorited': favorited, 'count': post.favorited_by.count()})
