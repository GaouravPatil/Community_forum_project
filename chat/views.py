from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
import json

from .models import Thread, Reply, Vote, ChatMessage
from .forms import ThreadForm, ReplyForm
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseBadRequest

def index(request):
    threads = Thread.objects.all().order_by('-created_at')
    paginator = Paginator(threads, 10)  # Show 10 threads per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'page_obj': page_obj})

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
        return JsonResponse({
            'id': reply.id,
            'content': reply.content,
            'thread_id': thread_id,
            'type': 'new_reply'
        })
    return JsonResponse({'error': 'Invalid form'}, status=400)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
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
