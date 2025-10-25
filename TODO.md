## New Backend Functionalities

### User Profiles
- [ ] Add UserProfile model to chat/models.py (avatar, bio, location, join_date)
- [ ] Create profile view in chat/views.py
- [ ] Create profile.html template
- [ ] Update register view to create UserProfile
- [ ] Add profile link in navigation (update index.html)
- [ ] Update project/settings.py for media settings (avatars)

### Categories/Tags
- [ ] Add Category model to chat/models.py
- [ ] Add category field to Thread model
- [ ] Update ThreadForm in chat/forms.py for category selection
- [ ] Update create_thread view to handle categories
- [ ] Update index.html to display categories and filter threads
- [ ] Add category creation/management (optional admin or view)

### Server-side Search
- [ ] Add search view in chat/views.py with database queries
- [ ] Update index view to handle search parameters
- [ ] Implement AJAX search in index.html for better UX
- [ ] Update URL patterns in chat/urls.py for search

### Notifications
- [ ] Add Notification model to chat/models.py (for replies to user's threads)
- [ ] Create notifications on reply creation in views.py
- [ ] Add notifications view in chat/views.py
- [ ] Create notifications.html template
- [ ] Update navigation with notification count (index.html)
- [ ] Update chat/consumers.py for real-time notifications

### General
- [ ] Run migrations after model changes
- [ ] Install Pillow for image handling (update requirements.txt)
- [ ] Test all new features for real-time updates
- [ ] Update README.md with new features
