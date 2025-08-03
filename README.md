# Second-Hand Trading Platform

A full-stack web application built with Flask for buying and selling second-hand items. Features user authentication, product listings, messaging system, and admin dashboard.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, login, profile management with avatar upload
- **Product Listings**: Create, edit, delete listings with multiple image support
- **Image Management**: Multi-image upload with cover image selection and manual rotation
- **Messaging System**: Real-time conversations between buyers and sellers
- **Favorites System**: Save and manage favorite listings
- **Transaction Management**: Reserve, purchase, and track sales history
- **Review System**: Rate and review users after completed transactions
- **Admin Dashboard**: Manage users, listings, and reports

### Technical Features
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Dynamic Image Carousel**: Custom JavaScript for manual image rotation
- **File Upload Security**: Secure filename handling and file type validation
- **Database Relationships**: Complex SQLAlchemy models with proper relationships
- **User Authentication**: Flask-Login integration with password hashing

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript (ES6+)
- **Authentication**: Flask-Login
- **Database**: SQLite with SQLAlchemy ORM
- **File Handling**: Werkzeug secure filename
- **Templating**: Jinja2

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd flask-website
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Create a .env file (optional)
   echo "SECRET_KEY=your-secret-key-here" > .env
   echo "FLASK_ENV=development" >> .env
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 📁 Project Structure

```
flask-website/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore           # Git ignore file
├── instance/
│   └── site.db         # SQLite database
├── static/
│   ├── uploads/        # Product images
│   └── avatars/        # User avatars
├── templates/
│   ├── home.html       # Base template
│   ├── navbar.html     # Navigation component
│   ├── listings.html   # Product listings page
│   ├── listing_detail.html  # Product detail page
│   ├── new_listing.html     # Create listing form
│   ├── edit_listing.html    # Edit listing form
│   ├── user_profile.html    # User profile page
│   ├── conversations.html   # Messaging interface
│   ├── my_favorites.html    # User favorites
│   ├── my_purchases.html    # Purchase history
│   ├── my_sales.html        # Sales history
│   ├── admin_dashboard.html # Admin panel
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   ├── about.html           # About page
│   └── contact.html         # Contact page
└── venv/                   # Virtual environment
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for session management
- `FLASK_ENV`: Environment mode (development/production)

### Database
The application uses SQLite by default. The database file is created automatically in the `instance/` directory.

### File Upload
- Maximum file size: 2MB
- Supported formats: PNG, JPG, JPEG, GIF
- Files are stored in `static/uploads/` (products) and `static/avatars/` (user avatars)

## 🚀 Usage

### For Users
1. **Register/Login**: Create an account or log in
2. **Browse Listings**: View all available products
3. **Create Listings**: Upload products with multiple images
4. **Manage Favorites**: Save interesting items
5. **Message Sellers**: Contact sellers through the messaging system
6. **Complete Transactions**: Reserve and purchase items
7. **Leave Reviews**: Rate other users after transactions

### For Administrators
1. **Access Admin Dashboard**: Available to admin users
2. **Monitor Reports**: Review user-submitted reports
3. **Manage Users**: View user statistics and activity
4. **Oversee Listings**: Monitor product listings and transactions

## 🔒 Security Features

- Password hashing using Werkzeug
- Secure file upload with filename validation
- SQL injection prevention through SQLAlchemy ORM
- CSRF protection through Flask-Login
- Input validation and sanitization

## 🧪 Testing

To run the application in development mode:
```bash
export FLASK_ENV=development
python app.py
```

## 📝 API Endpoints

### Authentication
- `GET/POST /register` - User registration
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Listings
- `GET /listings` - View all listings
- `GET /listing/<id>` - View specific listing
- `GET/POST /listing/new` - Create new listing
- `GET/POST /listing/<id>/edit` - Edit listing
- `POST /listing/<id>/delete` - Delete listing

### User Management
- `GET/POST /user/<username>` - User profile
- `GET /my_favorites` - User favorites
- `GET /my_purchases` - Purchase history
- `GET /my_sales` - Sales history

### Messaging
- `GET /conversations` - List conversations
- `GET/POST /messages/<username>` - View/send messages

### Admin
- `GET /admin` - Admin dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- None currently reported

## 🔮 Future Enhancements

- [ ] Email notifications
- [ ] Payment integration
- [ ] Advanced search and filtering
- [ ] Mobile app development
- [ ] Real-time chat using WebSockets
- [ ] Image compression and optimization
- [ ] Multi-language support

## 📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Note**: This is a development project. For production deployment, ensure proper security measures, environment variables, and database configuration. 