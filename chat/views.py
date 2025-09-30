from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

from .models import Thread, Reply
from .forms import ThreadForm, ReplyForm

def index(request):
    threads = Thread.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'threads': threads})

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
