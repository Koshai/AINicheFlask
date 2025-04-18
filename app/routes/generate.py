from flask import Blueprint, request, jsonify, current_app
from app.models import Generation
from app import db
from app.utils.translate import translate_to_bangla
from app.utils.ollama_client import generate_content
from app.middleware.auth_middleware import login_required, check_rate_limit

bp = Blueprint('generate', __name__, url_prefix='/generate')

TEMPLATES = {
    "Blog Post": "Write a detailed blog post about '{niche}' with at least 5 paragraphs, covering introduction, main points, and conclusion.",
    "Product Description": "Create a compelling product description for '{niche}' that highlights features, benefits, and unique selling points.",
    "Social Media": "Create 5 engaging social media posts about '{niche}' suitable for platforms like Instagram, Facebook and Twitter.",
    "Email Newsletter": "Write an email newsletter about '{niche}' with an engaging subject line, introduction, main content, and call to action.",
    "Landing Page": "Create landing page copy for '{niche}' with headline, subheadline, features, benefits, testimonial placeholders, and call to action.",
    "SEO Article": "Write an SEO-optimized article about '{niche}' with proper headings, subheadings, and keywords naturally incorporated."
}

# Load category data from file
def load_category_data():
    try:
        with open('app/data/full_clothing_combinations.txt', 'r') as file:
            categories = [line.strip() for line in file.readlines() if line.strip()]
        return categories
    except Exception as e:
        current_app.logger.error(f"Error loading category data: {str(e)}")
        return []
    
def get_categories():
    """Endpoint to get all clothing categories"""
    try:
        categories = load_category_data()
        return jsonify(categories)
    except Exception as e:
        current_app.logger.error(f"Error retrieving categories: {str(e)}")
        return jsonify({'error': 'Failed to retrieve categories'}), 500

@bp.route('/', methods=['POST'])
@login_required
@check_rate_limit
def generate_content_endpoint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Extract data from the request
        categories = data.get('categories', [])
        color = data.get('color', '')
        additional_words = data.get('additionalWords', '')
        content_type = data.get('type', 'Product Description')
        engine = data.get('engine', 'openai')
        language = data.get('language', 'en')

        if not categories:
            return jsonify({'error': 'No clothing categories provided'}), 400
            
        if not color:
            return jsonify({'error': 'No primary color provided'}), 400
            
        if content_type not in TEMPLATES:
            return jsonify({'error': f'Unknown content type. Available types: {", ".join(TEMPLATES.keys())}'}), 400

        # Build the niche description from the selected categories
        categories_str = ", ".join(categories)
        additional_words_formatted = additional_words.strip()
        
        niche = f"{color} {categories_str}"
        if additional_words_formatted:
            keywords = [word.strip() for word in additional_words_formatted.split(',')[:5]]
            if keywords:
                niche += f" with these keywords: {', '.join(keywords)}"
        
        # Generate content based on the niche
        prompt = TEMPLATES.get(content_type).format(niche=niche)
        content = generate_content(engine, prompt)

        # Translate if needed
        if language == 'bn':
            try:
                content = translate_to_bangla(content)
            except Exception as e:
                current_app.logger.error(f"Translation error: {str(e)}")
                return jsonify({'error': 'Translation failed', 'content': content}), 500

        # Save generation
        from flask import g
        generation = Generation(
            user_id=g.user.id,
            niche=niche,
            content_type=content_type,
            engine=engine,
            language=language,
            response=content
        )
        db.session.add(generation)
        db.session.commit()

        return jsonify({"content": content})
        
    except Exception as e:
        current_app.logger.error(f"Generation error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Content generation failed'}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    try:
        from flask import g
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        generations = Generation.query.filter_by(user_id=g.user.id) \
            .order_by(Generation.created_at.desc()) \
            .paginate(page=page, per_page=per_page)
            
        return jsonify({
            'items': [{
                'id': gen.id,
                'niche': gen.niche,
                'content_type': gen.content_type,
                'engine': gen.engine,
                'language': gen.language,
                'created_at': gen.created_at.isoformat(),
                'response': gen.response
            } for gen in generations.items],
            'total': generations.total,
            'pages': generations.pages,
            'current_page': page
        })
    except Exception as e:
        current_app.logger.error(f"History retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve history'}), 500