from django.test import Client
from django.contrib.auth.models import User
from chat.models import VideoCall, UserProfile
import json, sys

def get_or_create(username):
    u = User.objects.filter(username=username).first()
    if not u:
        u = User.objects.create_user(username=username, password='pass')
        UserProfile.objects.create(user=u)
    return u

print('Setting up users...')
a = get_or_create('usera')
b = get_or_create('userb')
print('Users:', a.username, b.username)

c1 = Client()
if not c1.login(username='usera', password='pass'):
    print('Failed to login usera')
    sys.exit(1)

c2 = Client()
if not c2.login(username='userb', password='pass'):
    print('Failed to login userb')
    sys.exit(1)

print('Accessing profile as usera...')
r = c1.get('/chat/profile/')
print('Profile status:', r.status_code)

print('Initiating call from usera to userb...')
payload = {'target_id': b.id, 'call_type': 'video'}
r = c1.post('/chat/call/initiate/', data=json.dumps(payload), content_type='application/json')
print('Initiate resp code:', r.status_code)
print('Initiate resp body:', r.content[:1000])

try:
    data = json.loads(r.content)
except Exception as e:
    print('Failed to parse JSON:', e)
    data = {}

call_id = data.get('call_id')
print('call_id:', call_id)

if call_id:
    try:
        call = VideoCall.objects.get(id=call_id)
        print('Call in DB: status=', call.status, 'receiver=', call.receiver.username)
    except Exception as e:
        print('Error fetching call from DB:', e)

    print('Userb fetching notifications JSON...')
    r2 = c2.get('/chat/notifications/')
    print('notifications endpoint status', r2.status_code)
    print('notifications body (first 500):', r2.content[:500])

    print('Userb accepting call...')
    r3 = c2.post(f'/chat/call/accept/{call_id}/')
    print('accept status', r3.status_code, 'body', r3.content)
    call.refresh_from_db()
    print('Call status after accept:', call.status)

    print('Usera ending call...')
    r4 = c1.post(f'/chat/call/end/{call_id}/')
    print('end status', r4.status_code, 'body', r4.content)
    call.refresh_from_db()
    print('Call status after end:', call.status)
else:
    print('No call created; aborting call flow tests')

print('Smoke test completed')
