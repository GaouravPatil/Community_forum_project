- [x] Fix ENV PYTHONDONTWRITEBYTECODE to use = format
- [x] Fix ENV PYTHONUNBUFFERED to use = format
- [x] Change CMD to JSON array format

## New Backend Functionalities

### User Authentication
- [x] Add Django auth URLs (login, logout, register) to project/urls.py
- [x] Create auth templates (login.html, register.html, base.html)
- [x] Update chat/templates/index.html to include login/logout links and user info
- [x] Ensure views require login where necessary

### Voting System
- [x] Add Vote model to chat/models.py (for threads and replies)
- [x] Create vote views (upvote/downvote for threads and replies)
- [x] Update chat/urls.py for vote endpoints
- [x] Modify chat/consumers.py to broadcast vote updates
- [x] Update frontend JS for voting buttons and real-time vote counts

### Pagination
- [x] Modify index view in chat/views.py to use Django Paginator
- [x] Update chat/templates/index.html for pagination controls
- [x] Add AJAX for loading more pages if needed

### Real-Time Chatting
- [x] Add ChatMessage model to chat/models.py
- [x] Create chat views for sending/receiving messages
- [x] Extend chat/consumers.py for live chat (separate group or extend existing)
- [x] Update chat/routing.py for chat WebSocket
- [x] Add chat UI to chat/templates/index.html (chat box, message list)
- [x] Update frontend JS for sending/receiving chat messages

### General
- [x] Run migrations after model changes
- [x] Test all features for real-time updates
- [x] Update README.md with new features
