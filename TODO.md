## Updated TODO for Adding Functionality and Backend to Login and Thread Creation

### Custom Login Backend
- [ ] Add custom login view in chat/views.py to handle authentication manually (check credentials, log in user, handle errors).
- [ ] Update chat/urls.py to include path for login view.
- [ ] Update project/urls.py to remove or adjust 'accounts/' include, as we'll use custom login.
- [ ] Update chat/templates/login.html to use the custom login view (change form action).

### User Profiles (Enhance Existing)
- [ ] Verify UserProfile model in chat/models.py (avatar, bio, location, join_date).
- [ ] Ensure profile view in chat/views.py handles avatar upload and bio editing.
- [ ] Update chat/templates/profile.html if needed for better UX.
- [ ] Confirm register view creates UserProfile.
- [ ] Update project/settings.py for media settings (avatars) if not already done.
- [ ] Add Pillow to requirements.txt for image handling.

### Notifications
- [ ] Verify Notification model in chat/models.py.
- [ ] Ensure notifications view in chat/views.py is complete.
- [ ] Update chat/templates/notifications.html for display and mark as read.
- [ ] Update chat/consumers.py for real-time notifications via WebSockets.
- [ ] Update navigation in base.html or index.html to show notification count.

### Backend for Starting a New Thread
- [ ] Add a new view in chat/views.py for creating threads via a form (not just AJAX).
- [ ] Create a new template chat/templates/create_thread.html with a form for title, content, category.
- [ ] Update chat/urls.py to include path for create_thread_form view.
- [ ] Update chat/templates/index.html to link to the create thread page.
- [ ] Ensure ThreadForm in chat/forms.py includes category field.

### General
- [ ] Run migrations after any model changes.
- [ ] Test login, profile, notifications, and thread creation.
- [ ] Update README.md with new features and usage.
- [ ] Update this TODO.md as tasks are completed.
