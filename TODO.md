# TODO for Real-time and Smoothness Improvements

- [x] Update chat/consumers.py to save new threads and replies asynchronously using database_sync_to_async.
- [x] Add error handling and validation in chat/consumers.py.
- [x] Update project/settings.py to use Redis channel layer instead of in-memory.
- [x] Add channels-redis to requirements.txt.
- [ ] Install and run Redis server (instructions below).
- [x] Improve frontend WebSocket handling in chat/templates/index.html:
  - [x] Add WebSocket reconnection logic.
  - [x] Add UI feedback for sending threads and replies.
  - [x] Optimize DOM updates to avoid duplicates.
- [ ] Test the real-time functionality after changes.

## Testing Instructions
1. Install and start Redis server (see instructions above).
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run Django migrations: `python manage.py migrate`
4. Start the Django server: `python manage.py runserver`
5. Open multiple browser tabs/windows to http://localhost:8000
6. Create threads and replies in one tab and verify they appear in real-time in other tabs.
7. Test WebSocket reconnection by stopping/starting the server and checking the status indicator.

## Redis Installation Instructions
To use the Redis channel layer, you need to install and run Redis server:

### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

### On Windows:
Download Redis from https://redis.io/download and follow installation instructions.

### Verify Redis is running:
```bash
redis-cli ping
```
Should respond with "PONG".

### Install Python dependencies:
```bash
pip install -r requirements.txt
```
