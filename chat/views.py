import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import CustomUserCreationForm
from django.contrib.contenttypes.models import ContentType
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

import json
import uuid

from django.contrib.auth.models import User
from .models import (
    Category, Thread, Reply, Notification,
    VideoCall, GroupVideoCall, CallHistory,
    UserProfile, Vote, ChatMessage
)
from .forms import ThreadForm, ReplyForm, UserProfileForm


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('chat_home')
    else:
        return redirect('user_login')


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
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

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
    return JsonResponse({'error': 'Invalid form', 'errors': form.errors}, status=400)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def create_reply(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

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
                reply=reply
            )

        return JsonResponse({
            'id': reply.id,
            'content': reply.content,
            'thread_id': thread_id,
            'type': 'new_reply'
        })
    return JsonResponse({'error': 'Invalid form', 'errors': form.errors}, status=400)


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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('user_login')
    else:
        form = CustomUserCreationForm()
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
            vote_obj.delete()
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
    notifications_qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    # include any incoming ringing calls so user can accept/reject from notifications
    incoming_calls = VideoCall.objects.filter(receiver=request.user, status='ringing').order_by('-created_at')
    if request.method == 'POST':
        notifications_qs.update(is_read=True)
        return JsonResponse({'status': 'success'})

    return render(request, 'notifications.html', {
        'notifications': notifications_qs,
        'incoming_calls': incoming_calls,
    })


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


@login_required
def initiate_video_call(request, user_id):
    try:
        receiver = User.objects.get(id=user_id)
        call = VideoCall.objects.create(
            caller=request.user,
            receiver=receiver,
            status='ringing'
        )
        # push realtime incoming-call event to receiver's websocket connections
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{receiver.id}',
                {
                    'type': 'incoming_call',
                    'call_id': call.id,
                    'caller_id': request.user.id,
                    'caller_username': request.user.username,
                    'call_type': call.call_type,
                    'created_at': str(call.created_at),
                }
            )
        except Exception:
            # don't fail the request if notification push fails
            pass

        return JsonResponse({
            'success': True,
            'call_id': call.id,
            'receiver_username': receiver.username,
        })
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)


@login_required
def accept_video_call(request, call_id):
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
    try:
        call = VideoCall.objects.get(id=call_id, receiver=request.user)
        call.status = 'missed'
        call.save()
        return JsonResponse({'success': True})
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)


@login_required
def end_video_call(request, call_id):
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
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST method allowed')

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

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
    history = CallHistory.objects.filter(user=request.user).order_by('-call_date')[:50]
    data = [{
        'id': h.id,
        'duration': h.duration,
        'call_date': h.call_date.strftime('%Y-%m-%d %H:%M'),
        'call_type': 'group' if h.group_call else 'video',
    } for h in history]
    return JsonResponse({'call_history': data})


@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('chat_home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not password:
            messages.error(request, 'Please provide username and password.')
            return render(request, 'login.html', {'username': username})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # default redirect to main landing 'chat_home'
            return redirect(request.GET.get('next', 'chat_home'))
        messages.error(request, 'Invalid credentials.')
        return render(request, 'login.html', {'username': username})
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')


@login_required
def home(request):
    threads = Thread.objects.select_related('author','category').order_by('-created_at')[:30]
    users = User.objects.exclude(id=request.user.id).only('id','username')[:50]
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'home.html', {
        'threads': threads,
        'users': users,
        'notifications': notifications,
    })


@login_required
def notifications_list(request):
    if request.method == 'GET':
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
        data = [{
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'thread_id': getattr(n.thread, 'id', None),
        } for n in notifications]
        return JsonResponse({'notifications': data})
    return HttpResponseBadRequest('Invalid method')


@login_required
@require_POST
def mark_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@login_required
@require_POST
def initiate_call(request):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    target_id = payload.get('target_id')
    call_type = payload.get('call_type', 'video')
    if not target_id or call_type not in ('video','audio'):
        return JsonResponse({'success': False, 'error': 'Missing/invalid parameters'}, status=400)

    try:
        target = User.objects.get(id=target_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    call = VideoCall.objects.create(
        caller=request.user,
        receiver=target,
        call_type=call_type,
        status='ringing',
        created_at=timezone.now()
    )

    Notification.objects.create(
        user=target,
        message=f"{request.user.username} is calling you ({call_type})",
        thread=None
    )
    # push realtime incoming-call event to receiver's websocket connections
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{target.id}',
            {
                'type': 'incoming_call',
                'call_id': call.id,
                'caller_id': request.user.id,
                'caller_username': request.user.username,
                'call_type': call.call_type,
                'created_at': str(call.created_at),
            }
        )
    except Exception:
        pass
    ws_path = f"/ws/video-call/{call.id}/"
    return JsonResponse({'success': True, 'call_id': call.id, 'ws_path': ws_path, 'call_type': call.call_type})


@login_required
@require_POST
def accept_call(request, call_id):
    try:
        call = VideoCall.objects.get(id=call_id, receiver=request.user)
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)
    call.status = 'active'
    call.start_time = timezone.now()
    call.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def reject_call(request, call_id):
    try:
        call = VideoCall.objects.get(id=call_id, receiver=request.user)
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)
    call.status = 'missed'
    call.end_time = timezone.now()
    call.save()
    return JsonResponse({'success': True})


@login_required
@require_POST
def end_call(request, call_id):
    try:
        call = VideoCall.objects.get(id=call_id)
    except VideoCall.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Call not found'}, status=404)
    if request.user not in (call.caller, call.receiver):
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    call.status = 'ended'
    call.end_time = timezone.now()
    call.save()
    try:
        duration = int((call.end_time - call.start_time).total_seconds()) if call.start_time and call.end_time else 0
        CallHistory.objects.create(user=call.caller, call=call, duration=duration)
        if call.receiver:
            CallHistory.objects.create(user=call.receiver, call=call, duration=duration)
    except Exception:
        pass
    return JsonResponse({'success': True})


@login_required
def call_page(request, call_id):
    call = get_object_or_404(VideoCall, id=call_id)
    if request.user not in (call.caller, call.receiver):
        messages.error(request, "You are not a participant in this call")
        return redirect('chat_home')
    return render(request, 'video_call.html', {
        'call_id': call.id,
        'call_type': call.call_type,
        'is_caller': request.user == call.caller
    })


def check_username(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return JsonResponse({'available': False, 'message': 'Username is required'})
    if len(username) < 3 or len(username) > 30:
        return JsonResponse({'available': False, 'message': 'Username must be 3-30 characters'})
    if not username.replace('_', '').isalnum():
        return JsonResponse({'available': False, 'message': 'Username can only contain letters, numbers, and underscores'})
    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({'available': False, 'message': 'Username is already taken'})
    return JsonResponse({'available': True, 'message': 'Username is available'})


def check_email(request):
    email = request.GET.get('email', '').strip()
    if not email:
        return JsonResponse({'available': False, 'message': 'Email is required'})
    if '@' not in email:
        return JsonResponse({'available': False, 'message': 'Invalid email format'})
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'available': False, 'message': 'Email is already registered'})
    return JsonResponse({'available': True, 'message': 'Email is available'})


