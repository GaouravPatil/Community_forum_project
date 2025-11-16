from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def vote_count(self):
        up_votes = self.votes.filter(vote_type=Vote.UPVOTE).count()
        down_votes = self.votes.filter(vote_type=Vote.DOWNVOTE).count()
        return up_votes - down_votes

    def user_vote(self, user):
        try:
            vote = self.votes.get(user=user)
            return vote.vote_type
        except Vote.DoesNotExist:
            return 0

class Reply(models.Model):
    content = models.TextField()
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.thread.title}"

    def vote_count(self):
        up_votes = self.votes.filter(vote_type=Vote.UPVOTE).count()
        down_votes = self.votes.filter(vote_type=Vote.DOWNVOTE).count()
        return up_votes - down_votes

    def user_vote(self, user):
        try:
            vote = self.votes.get(user=user)
            return vote.vote_type
        except Vote.DoesNotExist:
            return 0

class ChatMessage(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

class Vote(models.Model):
    UPVOTE = 1
    DOWNVOTE = -1
    VOTE_TYPES = [
        (UPVOTE, 'Upvote'),
        (DOWNVOTE, 'Downvote'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.SmallIntegerField(choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f"{self.user.username} voted {self.get_vote_type_display()} on {self.content_object}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
    
    # ...existing code...

class VideoCall(models.Model):
    CALL_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('missed', 'Missed'),
    ]
    
    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_initiated')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_received', null=True, blank=True)
    status = models.CharField(max_length=20, choices=CALL_STATUS_CHOICES, default='initiated')
    call_type = models.CharField(max_length=10, choices=[('video', 'Video'), ('audio', 'Audio')], default='video')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def duration(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def __str__(self):
        return f"Call: {self.caller.username} -> {self.receiver.username if self.receiver else 'Group'}"


class GroupVideoCall(models.Model):
    GROUP_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]
    
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_calls_initiated')
    participants = models.ManyToManyField(User, related_name='group_calls_participated')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=GROUP_STATUS_CHOICES, default='scheduled')
    max_participants = models.IntegerField(default=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    room_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"Group Call: {self.title}"
    
    class Meta:
        ordering = ['-created_at']


class CallHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='call_history')
    call = models.ForeignKey(VideoCall, on_delete=models.CASCADE, null=True, blank=True)
    group_call = models.ForeignKey(GroupVideoCall, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(default=0)  # in seconds
    call_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Call history for {self.user.username}"
