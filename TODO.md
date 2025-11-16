## TODO: Fix Issues and Implement Video/Audio Calls

### Tasks to Complete

- [ ] Fix unresolved Git merge conflict in `chat/templates/index.html` by removing conflict markers and merging content properly
- [x] Add more CSS animations to `chat/templates/base.html` (e.g., slideIn, bounce, rotate effects for interactive elements)
- [x] Add more CSS animations to `chat/templates/index.html` (e.g., animate threads on load, button hover effects, reply animations)
- [ ] Check other template files (`chat/templates/register.html`, `chat/templates/login.html`, etc.) for syntax errors and fix any found
- [ ] Review `chat/views.py` and other Python files (`chat/models.py`, `chat/forms.py`, etc.) for logical errors or bugs
- [ ] Test the application by running the Django server to ensure no runtime errors
- [ ] Verify animations work correctly in the browser using browser_action tool
- [x] Complete WebRTC signaling in `chat/templates/video_call.html`: add peer connection, handle offers, answers, ICE candidates
- [x] Update `chat/consumers.py` VideoCallConsumer to properly handle WebRTC messages (offer, answer, ice_candidate)
- [x] Ensure call buttons in `chat/templates/home.html` work properly and initiate calls correctly
- [x] Check `requirements.txt` for any missing dependencies (e.g., for WebRTC, none needed server-side)
- [x] Run migrations to ensure all models are up to date
- [x] Run the Django server on port 8002 and verify video/audio calls work
- [x] Test each feature: initiate video call, accept/reject, end call, audio call, group calls if implemented
- [x] Fixed profile view URL issue
- [x] Created test users for testing
