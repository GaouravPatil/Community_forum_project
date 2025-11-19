# TODO: Implement Login Flow Changes

## Tasks
- [x] Change root URL redirect in config/urls.py to '/chat/login/'
- [x] Update LOGIN_REDIRECT_URL in config/settings.py to '/chat/chat/'
- [x] Update LOGOUT_REDIRECT_URL in config/settings.py to '/chat/login/'
- [x] Modify user_login view in chat/views.py to redirect to 'chat_home' by default

## Additional Tasks
- [x] Add API endpoints for username and email availability checks in registration page
