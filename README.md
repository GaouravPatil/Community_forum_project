# Community Forum Projects 

# Implement Full Discussion Forum with Real-Time Features

## Features

### Core Functionality
- **Real-time Discussion Forum**: Create threads and replies with instant WebSocket updates.
- **User Authentication**: Login, register, and logout with Django's built-in auth system.
- **Voting System**: Upvote/downvote threads and replies with real-time vote counts.
- **Pagination**: Navigate through threads with Django's Paginator (10 threads per page).
- **Live Chat**: Real-time chat feature for authenticated users.

### Technical Stack
- **Backend**: Django 5.2, Channels for WebSockets, SQLite database.
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), WebSockets for real-time features.
- **Real-time**: Channels with ASGI for WebSocket communication.

## Setup and Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Start the Server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the Application**:
   - Forum: http://127.0.0.1:8000/chat/
   - Admin: http://127.0.0.1:8000/admin/

## Usage

1. **Register/Login**: Create an account or log in to access full features.
2. **Create Threads**: Use the "Start a New Thread" form to post discussions.
3. **Reply to Threads**: Click "Reply" on any thread to add responses.
4. **Vote**: Use 👍/👎 buttons to upvote or downvote threads/replies.
5. **Navigate Pages**: Use pagination controls to browse threads.
6. **Live Chat**: Authenticated users can chat in real-time via the chat box.

## Testing Real-time Features

- Open multiple browser tabs/windows.
- Create threads/replies in one tab and see updates in others instantly.
- Vote on posts and observe real-time vote count changes.
- Send chat messages and see them appear live for all users.

## Completed Steps
- [x] Create chat/models.py: Define Thread and Reply models with fields for title, content, author (User), and timestamps.
- [x] Create chat/forms.py: Define ThreadForm and ReplyForm for handling user input.
- [x] Create chat/views.py: Implement index view to render the forum, and AJAX views for creating threads and replies.
- [x] Create chat/urls.py: Define URL patterns for the chat app (index, create-thread, create-reply).
- [x] Update project/urls.py: Include the chat app URLs under /chat/.
- [x] Update project/settings.py: Add 'channels' to INSTALLED_APPS, set ASGI_APPLICATION, and configure CHANNEL_LAYERS (InMemory for dev).
- [x] Create chat/consumers.py: Implement ChatConsumer for WebSocket handling (connect, disconnect, receive messages for new threads/replies).
- [x] Create chat/routing.py: Define WebSocket URL patterns for /ws/chat/.
- [x] Update project/asgi.py: Integrate ProtocolTypeRouter for WebSockets using chat.routing.
- [x] Update requirements.txt: Add channels dependency.
- [x] Install dependencies: Run `pip install channels`.
- [x] Run migrations: `python manage.py makemigrations chat` and `python manage.py migrate`.
