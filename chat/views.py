from datetime import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import json
import uuid

from .models import (
    CallHistory, GroupVideoCall, Thread, Reply, VideoCall,
    Vote, ChatMessage, UserProfile, Category, Notification
)
from .forms import ThreadForm, ReplyForm, UserProfileForm


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

    paginator = Paginator(threads, 10)  # Show 10 threads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    unread_notifications = 0
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'unread_notifications': unread_notifications
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
            'type': 'new_thread'
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

        # Create notification for thread author if not the same user
        if thread.author != request.user:
            Notification.objects.create(
                user=thread.author,
                message=f"{request.user.username} replied to your thread '{thread.title}'",
                thread=thread,
                reply=reply
            )

        return JsonResponse({
            'id': reply.id,
            'content': reply.content,
            'thread_id': thread_id,
            'type': 'new_reply'
        })
    return JsonResponse({'error': 'Invalid form'}, status=400)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create UserProfile for the new user
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


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
            vote_obj.delete()  # Remove vote if same type clicked again
        else:
            vote_obj.vote_type = vote_type
            vote_obj.save()

    return JsonResponse({'vote_count': obj.vote_count(), 'user_vote': obj.user_vote(request.user)})


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
        'type': 'new_chat_message'
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

    return render(request, 'profile.html', {'form': form, 'user_profile': user_profile})


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    if request.method == 'POST':
        # Mark all as read
        notifications.update(is_read=True)
        return JsonResponse({'status': 'success'})

    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def create_thread_form(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.author = request.user
            thread.save()
            messages.success(request, 'Thread created successfully!')
            return redirect('index')
    else:
        form = ThreadForm()
    categories = Category.objects.all()
    return render(request, 'create_thread.html', {'form': form, 'categories': categories})


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
    for thread in threads[:20]:  # Limit to 20 results
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


@login_required
def initiate_video_call(request, user_id):
    """Initiate a 1-on-1 video call"""
    try:
        receiver = User.objects.get(id=user_id)
        call = VideoCall.objects.create(
            caller=request.user,
            receiver=receiver,
            status='ringing'
        )
        return JsonResponse({
            'success': True,
            'call_id': call.id,
            'receiver_username': receiver.username,
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)


@login_required
def accept_video_call(request, call_id):
    """Accept an incoming video call"""
    try:
        call = VideoCall.objects.get(id=call_id, receiver=request.user)
        call.status = 'active'
        call.start_time = timezone.now()
        call.save()
        return JsonResponse({'success': True, 'call_id': call.id})
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)


@login_required
def reject_video_call(request, call_id):
    """Reject an incoming video call"""
    try:
        call = VideoCall.objects.get(id=call_id, receiver=request.user)
        call.status = 'missed'
        call.save()
        return JsonResponse({'success': True})
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)


@login_required
def end_video_call(request, call_id):
    """End an active video call"""
    try:
        call = VideoCall.objects.get(id=call_id)
        if call.caller == request.user or call.receiver == request.user:
            call.status = 'ended'
            call.end_time = timezone.now()
            call.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)


@login_required
def create_group_call(request):
    """Create a new group video call"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')

    data = json.loads(request.body)
    title = data.get('title', 'Group Call')
    description = data.get('description', '')
    max_participants = data.get('max_participants', 10)
    start_time = data.get('start_time')

    room_id = str(uuid.uuid4())[:12]

    group_call = GroupVideoCall.objects.create(
        initiator=request.user,
        title=title,
        description=description,
        max_participants=max_participants,
        start_time=timezone.now() if not start_time else start_time,
        room_id=room_id,
        status='active'
    )
    group_call.participants.add(request.user)

    return JsonResponse({
        'success': True,
        'room_id': room_id,
        'group_call_id': group_call.id,
        'title': title,
    })


@login_required
def join_group_call(request, room_id):
    """Join an existing group video call"""
    try:
        group_call = GroupVideoCall.objects.get(room_id=room_id)
        if group_call.participants.count() < group_call.max_participants:
            group_call.participants.add(request.user)
            return JsonResponse({
                'success': True,
                'room_id': room_id,
                'group_call_id': group_call.id,
                'title': group_call.title,
            })
        return JsonResponse({'success': False, 'error': 'Group call is full'}, status=400)
    except GroupVideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Group call not found'}, status=404)


@login_required
def get_call_history(request):
    """Get user's call history"""
    history = CallHistory.objects.filter(user=request.user).order_by('-call_date')[:50]
    data = [{
        'id': h.id,
        'duration': h.duration,
        'call_date': h.call_date.strftime('%Y-%m-%d %H:%M'),
        'call_type': 'group' if h.group_call else 'video',
    } for h in history]
    return JsonResponse({'call_history': data})
