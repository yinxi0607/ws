from flask import Flask, request, session
from flask_socketio import SocketIO, join_room, leave_room
from geventwebsocket.handler import WebSocketHandler
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with your secret key
socketio = SocketIO(app, async_mode='gevent')

# Dictionary to store sessions and their last activity time
sessions = {}

# Session timeout in seconds
SESSION_TIMEOUT = 300  # 5 minutes

# Function to check and remove expired sessions
def cleanup_sessions():
    while True:
        time.sleep(60)  # Run every minute
        current_time = time.time()
        expired_sessions = [session_id for session_id, last_activity_time in sessions.items() if
                            current_time - last_activity_time > SESSION_TIMEOUT]

        for session_id in expired_sessions:
            leave_room(session_id)  # Leave the corresponding room
            del sessions[session_id]
            print(f'Session {session_id} expired and removed.')

# WebSocket event handler for connecting
@socketio.on('connect')
def handle_connect():
    session_id = session.get('current_session')
    if session_id and session_id in sessions:
        sessions[session_id] = time.time()
        join_room(session_id)  # Join the corresponding room
        print(f'WebSocket connected for session: {session_id}')
    else:
        print('Invalid or expired session ID during WebSocket connection.')

# HTTP route to get a WebSocket session
@app.route('/get_session', methods=['POST'])
def get_session():
    user_id = request.json.get('user_id')
    session_id = f'user_{user_id}_session'
    sessions[session_id] = time.time()  # Record the current time as the session's last activity time
    session['current_session'] = session_id
    print(f'Session {session_id} created.')
    return {'session_id': session_id}

# WebSocket event handler for receiving messages
@socketio.on('message')
def handle_message(message):
    session_id = session.get('current_session')
    if session_id:
        print(f'Received message from session {session_id}: {message}')
        # Broadcast the message to all clients in the same room
        socketio.emit('message', {'message': message}, room=session_id)
    else:
        print('No session found for message.')

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_sessions)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5022, use_reloader=False)
