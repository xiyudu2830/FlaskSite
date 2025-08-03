"""
Basic tests for the Second-Hand Trading Platform
Run with: python -m pytest test_app.py
"""

import pytest
import os
import tempfile
from app import app, db, User, Listing, ListingImage
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def test_user():
    """Create a test user."""
    user = User(
        username='testuser',
        password_hash=generate_password_hash('testpass')
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Second-Hand Trading Platform' in response.data


def test_register_page(client):
    """Test that the registration page loads."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data


def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_user_registration(client):
    """Test user registration functionality."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Check if user was created
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None


def test_user_login(client, test_user):
    """Test user login functionality."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_listings_page(client):
    """Test that the listings page loads."""
    response = client.get('/listings')
    assert response.status_code == 200
    assert b'All Listings' in response.data


def test_create_listing(client, test_user):
    """Test creating a new listing."""
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Create listing
    response = client.post('/listing/new', data={
        'title': 'Test Item',
        'description': 'Test description',
        'price': '10.00',
        'category': 'Electronics',
        'location': 'Test City',
        'cover_index': '0'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    # Check if listing was created
    with app.app_context():
        listing = Listing.query.filter_by(title='Test Item').first()
        assert listing is not None
        assert listing.seller.username == 'testuser'


def test_listing_detail_page(client, test_user):
    """Test listing detail page."""
    # Create a test listing
    with app.app_context():
        listing = Listing(
            title='Test Item',
            description='Test description',
            price=10.00,
            category='Electronics',
            location='Test City',
            seller=test_user
        )
        db.session.add(listing)
        db.session.commit()
        
        response = client.get(f'/listing/{listing.id}')
        assert response.status_code == 200
        assert b'Test Item' in response.data


def test_favorite_functionality(client, test_user):
    """Test favorite/unfavorite functionality."""
    # Create a test listing
    with app.app_context():
        listing = Listing(
            title='Test Item',
            description='Test description',
            price=10.00,
            category='Electronics',
            location='Test City',
            seller=test_user
        )
        db.session.add(listing)
        db.session.commit()
        
        # Login
        client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        # Add to favorites
        response = client.post(f'/favorite/{listing.id}', follow_redirects=True)
        assert response.status_code == 200
        
        # Check if added to favorites
        user = User.query.filter_by(username='testuser').first()
        assert listing in user.favorites.all()


def test_file_upload_security():
    """Test file upload security."""
    from app import allowed_file
    
    # Test allowed files
    assert allowed_file('image.jpg') == True
    assert allowed_file('image.png') == True
    assert allowed_file('image.jpeg') == True
    assert allowed_file('image.gif') == True
    
    # Test disallowed files
    assert allowed_file('image.exe') == False
    assert allowed_file('image.php') == False
    assert allowed_file('image.py') == False
    assert allowed_file('image.txt') == False


def test_password_hashing():
    """Test password hashing functionality."""
    user = User(username='testuser')
    user.password = 'testpass'
    
    # Test password verification
    assert user.verify_password('testpass') == True
    assert user.verify_password('wrongpass') == False


def test_database_relationships():
    """Test database relationships."""
    with app.app_context():
        # Create test user
        user = User(username='testuser')
        db.session.add(user)
        db.session.commit()
        
        # Create test listing
        listing = Listing(
            title='Test Item',
            description='Test description',
            price=10.00,
            category='Electronics',
            location='Test City',
            seller=user
        )
        db.session.add(listing)
        db.session.commit()
        
        # Test relationships
        assert listing.seller == user
        assert listing in user.listings
        
        # Test image relationship
        image = ListingImage(
            filename='test.jpg',
            listing=listing,
            is_cover=True
        )
        db.session.add(image)
        db.session.commit()
        
        assert image in listing.images
        assert image.listing == listing


if __name__ == '__main__':
    pytest.main([__file__]) 