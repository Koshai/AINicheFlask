from flask import session, g, request, jsonify
from functools import wraps
from app.models import User
from datetime import datetime, timedelta
from flask import current_app as app
from app.routes.auth import validate_token

def load_logged_in_user():
    user_id = session.get('user_id')
    
    # Try to get user from session first
    if user_id is not None:
        g.user = User.query.get(user_id)
        return
        
    # Then try token-based auth
    token = request.headers.get('X-API-Token')
    if token:
        user_id = validate_token(token)
        if user_id:
            g.user = User.query.get(user_id)
            return
            
    g.user = None

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return jsonify({'error': 'Authentication required'}), 401
        return view(*args, **kwargs)
    return wrapped_view

def check_rate_limit(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return jsonify({'error': 'Authentication required'}), 401
            
        now = datetime.utcnow()
        limit = app.config['RATE_LIMIT_PAID'] if g.user.is_paid else app.config['RATE_LIMIT_DEFAULT']
        
        # Reset count if it's been more than an hour
        if g.user.last_request_time and g.user.last_request_time < now - timedelta(hours=1):
            g.user.request_count = 0
            
        if g.user.request_count >= limit:
            return jsonify({'error': 'Rate limit exceeded'}), 429
            
        g.user.request_count += 1
        g.user.last_request_time = now
        
        return view(*args, **kwargs)
    return wrapped_view