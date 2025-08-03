# Project Structure

```
flask-website/
├── app.py                    # Main Flask application (561 lines)
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── DEPLOYMENT.md            # Deployment guide
├── LICENSE                  # MIT License
├── .gitignore              # Git ignore file
├── test_app.py             # Unit tests
├── PROJECT_STRUCTURE.md    # This file
├── instance/
│   └── site.db            # SQLite database (auto-generated)
├── static/
│   ├── uploads/           # Product images
│   │   └── .gitkeep      # Keep directory in git
│   ├── avatars/          # User avatars
│   │   └── .gitkeep      # Keep directory in git
│   └── (uploaded files)  # User-uploaded content
└── templates/
    ├── home.html          # Base template with Bootstrap
    ├── navbar.html        # Navigation component
    ├── listings.html      # Product listings with filters
    ├── listing_detail.html # Product detail with carousel
    ├── new_listing.html   # Create listing form
    ├── edit_listing.html  # Edit listing form
    ├── user_profile.html  # User profile page
    ├── conversations.html # Messaging interface
    ├── conversation.html  # Individual conversation
    ├── my_favorites.html  # User favorites
    ├── my_purchases.html  # Purchase history
    ├── my_sales.html      # Sales history
    ├── admin_dashboard.html # Admin panel
    ├── login.html         # Login form
    ├── register.html      # Registration form
    ├── about.html         # About page
    └── contact.html       # Contact page
```

## Key Files Description

### Backend (app.py)
- **Models**: User, Listing, ListingImage, Message, Review, Report
- **Routes**: Authentication, CRUD operations, messaging, admin
- **Security**: Password hashing, file upload validation
- **Database**: SQLAlchemy ORM with SQLite

### Frontend (templates/)
- **Responsive Design**: Bootstrap 5 for mobile-friendly UI
- **Dynamic Features**: JavaScript for image carousel, form validation
- **User Experience**: Intuitive navigation and interactions

### Configuration
- **Environment Variables**: SECRET_KEY, FLASK_ENV via python-dotenv
- **File Upload**: Secure filename handling, type validation
- **Database**: SQLite with automatic table creation

### Testing
- **Unit Tests**: pytest framework with fixtures
- **Coverage**: Core functionality testing
- **Security**: File upload and authentication tests

### Documentation
- **README.md**: Comprehensive project overview
- **DEPLOYMENT.md**: Production deployment guide
- **LICENSE**: MIT License for open source

## Database Schema

### User Table
- id (Primary Key)
- username (Unique)
- password_hash
- avatar_filename
- is_admin

### Listing Table
- id (Primary Key)
- title, description, price, location, category
- seller_id (Foreign Key to User)
- reserved_by_id (Foreign Key to User)
- status (Available/Reserved/Sold)

### ListingImage Table
- id (Primary Key)
- filename
- listing_id (Foreign Key to Listing)
- is_cover (Boolean)

### Message Table
- id (Primary Key)
- sender_id, recipient_id (Foreign Keys to User)
- content, timestamp, read

### Review Table
- id (Primary Key)
- reviewer_id, reviewee_id (Foreign Keys to User)
- listing_id (Foreign Key to Listing)
- rating, comment, timestamp

### Report Table
- id (Primary Key)
- reporter_id (Foreign Key to User)
- listing_id (Foreign Key to Listing)
- reason, timestamp, resolved

## API Endpoints

### Authentication
- GET/POST `/register` - User registration
- GET/POST `/login` - User login
- GET `/logout` - User logout

### Listings
- GET `/listings` - View all listings with filters
- GET `/listing/<id>` - View specific listing
- GET/POST `/listing/new` - Create new listing
- GET/POST `/listing/<id>/edit` - Edit listing
- POST `/listing/<id>/delete` - Delete listing

### User Management
- GET/POST `/user/<username>` - User profile
- GET `/my_favorites` - User favorites
- GET `/my_purchases` - Purchase history
- GET `/my_sales` - Sales history

### Messaging
- GET `/conversations` - List conversations
- GET/POST `/messages/<username>` - View/send messages

### Admin
- GET `/admin` - Admin dashboard

## Security Features

- **Password Hashing**: Werkzeug security
- **File Upload Security**: Type validation, secure filenames
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CSRF Protection**: Flask-Login
- **Input Validation**: Form validation and sanitization

## Performance Considerations

- **Database Indexing**: Primary keys and foreign keys
- **Image Optimization**: Responsive image display
- **Caching**: Static file caching headers
- **Lazy Loading**: Database relationship loading

## Scalability Features

- **Modular Design**: Separated concerns
- **Database Relationships**: Proper foreign key constraints
- **File Organization**: Structured static file handling
- **Template Inheritance**: DRY principle in templates 