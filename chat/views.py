from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
import json

from .models import (
    Category, Thread, Reply, Vote, ChatMessage,
    UserProfile, Notification
)
from .forms import ThreadForm, ReplyForm, UserProfileForm

from django.shortcuts import render, get_object_or_404
from .models import Category, Thread, Notification
from django.core.paginator import Paginator

def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    threads = Thread.objects.filter(category=category).order_by('-created_at')

    paginator = Paginator(threads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

    return render(request, 'category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'unread_notifications': unread_notifications,
    })


def index(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    threads = Thread.objects.all().order_by('-created_at')

    if query:
        threads = threads.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )

    if category_id:
        threads = threads.filter(category_id=category_id)

    paginator = Paginator(threads, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'unread_notifications': unread_notifications,
    })



def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')



@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_thread(request):
    data = json.loads(request.body)
    form = ThreadForm(data)
    if form.is_valid():
        thread = form.save(commit=False)
        thread.author = request.user
        thread.save()
        return JsonResponse({
            'id': thread.id,
            'title': thread.title,
            'content': thread.content,
            'type': 'new_thread',
        })
    return JsonResponse({'error': 'Invalid form'}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_reply(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    data = json.loads(request.body)
    form = ReplyForm(data)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.thread = thread
        reply.author = request.user
        reply.save()


        if thread.author != request.user:
            Notification.objects.create(
                user=thread.author,
                message=f"{request.user.username} replied to your thread '{thread.title}'",
                thread=thread,
                reply=reply,
            )

        return JsonResponse({
            'id': reply.id,
            'content': reply.content,
            'thread_id': thread_id,
            'type': 'new_reply',
        })
    return JsonResponse({'error': 'Invalid form'}, status=400)



def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        unread = notifications.filter(is_read=False)
        data = [{
            'message': n.message,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        } for n in unread]

        # Mark them as read after sending
        unread.update(is_read=True)
        return JsonResponse({'notifications': data})

    return render(request, 'notifications.html', {'notifications': notifications})




def login_view(request):
    """Optional custom login view. Fixed: not protected by login_required, uses the
    correct template and redirects to the index on success.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Handle "Remember Me"
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)

            return redirect('index')
    else:
        form = AuthenticationForm()

    # Use the standard auth template location
    return render(request, "registration/login.html", {"form": form})



@login_required
def vote(request, model_type, object_id):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')

    vote_type = request.POST.get('vote_type')
    if vote_type not in ['1', '-1']:
        return HttpResponseBadRequest('Invalid vote type')

    vote_type = int(vote_type)

    try:
        if model_type == 'thread':
            content_type = ContentType.objects.get_for_model(Thread)
            obj = Thread.objects.get(id=object_id)
        elif model_type == 'reply':
            content_type = ContentType.objects.get_for_model(Reply)
            obj = Reply.objects.get(id=object_id)
        else:
            return HttpResponseBadRequest('Invalid model type')
    except (Thread.DoesNotExist, Reply.DoesNotExist):
        return HttpResponseBadRequest('Object not found')

    vote_obj, created = Vote.objects.get_or_create(
        content_type=content_type,
        object_id=object_id,
        user=request.user,
        defaults={'vote_type': vote_type}
    )

    if not created:
        if vote_obj.vote_type == vote_type:
            vote_obj.delete()
        else:
            vote_obj.vote_type = vote_type
            vote_obj.save()

    return JsonResponse({
        'vote_count': obj.vote_count(),
        'user_vote': obj.user_vote(request.user),
    })



@login_required
def profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'profile.html', {
        'form': form,
        'user_profile': user_profile,
    })



@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    if request.method == 'POST':
        notifications.update(is_read=True)
        return JsonResponse({'status': 'success'})

    return render(request, 'notifications.html', {'notifications': notifications})



@login_required
def send_chat_message(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')

    content = request.POST.get('content')
    if not content:
        return HttpResponseBadRequest('Content is required')

    message = ChatMessage.objects.create(content=content, author=request.user)
    return JsonResponse({
        'id': message.id,
        'content': message.content,
        'author': message.author.username,
        'created_at': message.created_at.isoformat(),
        'type': 'new_chat_message',
    })



@login_required
def request_access(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    send_mail(
        subject=f"Access Request for {category.name}",
        message=f"User {request.user.username} requested access to '{category.name}'.",
        from_email='no-reply@forum.com',
        recipient_list=['admin@forum.com'],
    )
    return render(request, 'forum/access_requested.html', {'category': category})



def search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    threads = Thread.objects.all().order_by('-created_at')

    if query:
        threads = threads.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query)
        )

    if category_id:
        threads = threads.filter(category_id=category_id)

    threads_data = []
    for thread in threads[:20]: 
        threads_data.append({
            'id': thread.id,
            'title': thread.title,
            'content': thread.content[:100] + '...' if len(thread.content) > 100 else thread.content,
            'author': thread.author.username,
            'category': thread.category.name if thread.category else 'General',
            'created_at': thread.created_at.strftime('%Y-%m-%d %H:%M'),
            'replies_count': thread.replies.count(),
            'vote_count': thread.vote_count(),
        })

    return JsonResponse({'threads': threads_data})
