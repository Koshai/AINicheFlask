from flask import Blueprint, request, jsonify, session, current_app
from app.models import User
from app import db, bcrypt
import secrets
import traceback

bp = Blueprint('auth', __name__, url_prefix='/auth')

# In-memory token store (not persistent across restarts)
# In a production app, you'd store this in Redis or a database
tokens = {}

@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'})
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate API token
        token = secrets.token_urlsafe(32)
        tokens[token] = user.id
        
        # Still set session for browser clients
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Logged in successfully',
            'token': token,  # Return token for API usage
            'user': {
                'email': user.email,
                'is_paid': user.is_paid
            }
        })
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    # Clear session
    session.clear()
    
    # Clear token if provided
    token = request.headers.get('X-API-Token')
    if token and token in tokens:
        del tokens[token]
        
    return jsonify({'message': 'Logged out successfully'})

# Add a function to validate tokens
def validate_token(token):
    return tokens.get(token)