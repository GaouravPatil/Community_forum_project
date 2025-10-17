from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Thread(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
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
