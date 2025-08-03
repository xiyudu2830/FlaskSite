from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_, and_

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

AVATAR_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'avatars')
if not os.path.exists(AVATAR_FOLDER):
    os.makedirs(AVATAR_FOLDER)
app.config['AVATAR_FOLDER'] = AVATAR_FOLDER
AVATAR_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_avatar(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AVATAR_ALLOWED_EXTENSIONS

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('listing_id', db.Integer, db.ForeignKey('listing.id'), primary_key=True)
)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100))
    image_filename = db.Column(db.String(120))
    category = db.Column(db.String(50))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reserved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller = db.relationship('User', foreign_keys=[seller_id], backref='listings')
    reserved_by = db.relationship('User', foreign_keys=[reserved_by_id], backref='reserved_listings')
    status = db.Column(db.String(20), default='Available')  # Available, Reserved, Sold
    images = db.relationship('ListingImage', cascade='all, delete-orphan', backref='listing')

class ListingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    is_cover = db.Column(db.Boolean, default=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    avatar_filename = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    favorites = db.relationship('Listing', secondary=favorites, backref='favorited_by', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='given_reviews')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='received_reviews')
    listing = db.relationship('Listing', backref='reviews')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    reporter = db.relationship('User', backref='reports')
    listing = db.relationship('Listing', backref='reports')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def load_unread_count():
    if current_user.is_authenticated:
        g.unread_count = Message.query.filter_by(recipient=current_user, read=False).count()
    else:
        g.unread_count = 0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Message sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

CATEGORIES = ['Electronics', 'Appliances', 'Books', 'Clothing', 'Sports', 'Other']

@app.route('/listings')
def listings():
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest')
    query = Listing.query
    if category:
        query = query.filter_by(category=category)
    if location:
        query = query.filter(Listing.location.contains(location))
    if keyword:
        query = query.filter(Listing.title.contains(keyword) | Listing.description.contains(keyword))
    if min_price:
        try:
            query = query.filter(Listing.price >= float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            query = query.filter(Listing.price <= float(max_price))
        except ValueError:
            pass
    if status:
        query = query.filter_by(status=status)
    if sort == 'price_asc':
        query = query.order_by(Listing.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Listing.price.desc())
    else:
        query = query.order_by(Listing.id.desc())
    all_listings = query.all()
    locations = [l.location for l in Listing.query.with_entities(Listing.location).distinct() if l.location]
    return render_template('listings.html', listings=all_listings, categories=CATEGORIES, selected_category=category, keyword=keyword, locations=locations, selected_location=location, min_price=min_price, max_price=max_price, selected_status=status, sort=sort)

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listing_detail.html', listing=listing)

# Remove YOLO/OpenCV imports and crop_main_object function

@app.route('/listing/new', methods=['GET', 'POST'])
@login_required
def new_listing():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']
        location = request.form['location']
        files = request.files.getlist('images')
        cover_index = int(request.form.get('cover_index', 0))
        listing = Listing(title=title, description=description, price=price, category=category, location=location, seller=current_user)
        db.session.add(listing)
        db.session.commit()
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = f"{current_user.id}_{listing.id}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                file.save(file_path)
                img = ListingImage(filename=image_filename, listing=listing, is_cover=(i == cover_index))
                db.session.add(img)
        db.session.commit()
        flash('Listing created!', 'success')
        return redirect(url_for('listings'))
    return render_template('new_listing.html', categories=CATEGORIES)

@app.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.seller != current_user:
        flash('You do not have permission to edit this listing.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    if request.method == 'POST':
        listing.title = request.form['title']
        listing.description = request.form['description']
        listing.price = float(request.form['price'])
        listing.category = request.form['category']
        listing.location = request.form['location']
        files = request.files.getlist('images')
        cover_existing = request.form.get('cover_radio_existing')
        cover_new = request.form.get('cover_index_new')
        delete_image_ids = request.form.get('delete_image_ids', '')
        # Delete selected images
        if delete_image_ids:
            ids_to_delete = [int(i) for i in delete_image_ids.split(',') if i.strip()]
            for img in listing.images[:]:
                if img.id in ids_to_delete:
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
                    except Exception:
                        pass
                    db.session.delete(img)
        # 1. Reset all existing images to not be cover
        for img in listing.images:
            img.is_cover = False
        # 2. Set existing image as cover if selected
        if cover_existing:
            for img in listing.images:
                if str(img.id) == str(cover_existing):
                    img.is_cover = True
        # 3. Set new image as cover if selected
        new_imgs = []
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_filename = f"{current_user.id}_{listing.id}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                file.save(file_path)
                is_cover = (cover_new is not None and str(i) == str(cover_new)) and not cover_existing
                img = ListingImage(filename=image_filename, listing=listing, is_cover=is_cover)
                db.session.add(img)
                new_imgs.append(img)
        db.session.commit()
        flash('Listing updated!', 'success')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    return render_template('edit_listing.html', listing=listing, categories=CATEGORIES)

@app.route('/listing/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.seller != current_user:
        flash('You do not have permission to delete this listing.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    # Delete associated images from disk
    for img in listing.images:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
        except Exception:
            pass
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted.', 'info')
    return redirect(url_for('listings'))

@app.route('/listing/<int:listing_id>/reserve', methods=['POST'])
@login_required
def reserve_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.status != 'Available':
        flash('This listing is not available for reservation.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    if listing.seller == current_user:
        flash('You cannot reserve your own listing.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    listing.status = 'Reserved'
    listing.reserved_by = current_user
    db.session.commit()
    flash('You have reserved this listing.', 'success')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/listing/<int:listing_id>/cancel_reservation', methods=['POST'])
@login_required
def cancel_reservation(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    # Only the reserving user or the seller can cancel
    if listing.status != 'Reserved':
        flash('This listing is not reserved.', 'danger')
    elif current_user != listing.reserved_by and current_user != listing.seller:
        flash('You do not have permission to cancel this reservation.', 'danger')
    else:
        listing.status = 'Available'
        listing.reserved_by = None
        db.session.commit()
        flash('Reservation cancelled.', 'info')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/listing/<int:listing_id>/relist', methods=['POST'])
@login_required
def relist_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if current_user != listing.seller:
        flash('Only the seller can relist.', 'danger')
    else:
        listing.status = 'Available'
        listing.reserved_by = None
        db.session.commit()
        flash('Listing relisted as available.', 'success')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/listing/<int:listing_id>/mark_sold', methods=['POST'])
@login_required
def mark_sold(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.seller != current_user:
        flash('Only the seller can mark as sold.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    if listing.status != 'Reserved':
        flash('Listing must be reserved before marking as sold.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    listing.status = 'Sold'
    db.session.commit()
    flash('Listing marked as sold.', 'success')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/user/<username>', methods=['GET', 'POST'])
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    listings = Listing.query.filter_by(seller=user).order_by(Listing.id.desc()).all()
    if current_user.is_authenticated and current_user.id == user.id and request.method == 'POST':
        file = request.files.get('avatar')
        if file and allowed_avatar(file.filename):
            filename = secure_filename(file.filename)
            avatar_filename = f"{user.id}_{filename}"
            file.save(os.path.join(app.config['AVATAR_FOLDER'], avatar_filename))
            user.avatar_filename = avatar_filename
            db.session.commit()
            flash('Avatar updated!', 'success')
            return redirect(url_for('user_profile', username=user.username))
    # Calculate average rating
    reviews = Review.query.filter_by(reviewee=user).all()
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else None
    return render_template('user_profile.html', user=user, listings=listings, reviews=reviews, avg_rating=avg_rating)

@app.route('/avatars/<filename>')
def avatar_file(filename):
    return send_from_directory(app.config['AVATAR_FOLDER'], filename)

@app.route('/conversations')
@login_required
def conversations():
    # Find all users who have chatted with current_user
    user_ids = set()
    for msg in Message.query.filter(or_(Message.sender==current_user, Message.recipient==current_user)).all():
        if msg.sender != current_user:
            user_ids.add(msg.sender_id)
        if msg.recipient != current_user:
            user_ids.add(msg.recipient_id)
    users = User.query.filter(User.id.in_(user_ids)).all()
    threads = []
    for user in users:
        last_msg = Message.query.filter(
            or_(and_(Message.sender==current_user, Message.recipient==user),
                 and_(Message.sender==user, Message.recipient==current_user))
        ).order_by(Message.timestamp.desc()).first()
        unread = Message.query.filter_by(sender=user, recipient=current_user, read=False).count()
        threads.append({'user': user, 'last_msg': last_msg, 'unread': unread})
    threads.sort(key=lambda t: t['last_msg'].timestamp if t['last_msg'] else 0, reverse=True)
    return render_template('conversations.html', threads=threads)

@app.route('/messages/<username>', methods=['GET', 'POST'])
@login_required
def conversation(username):
    other = User.query.filter_by(username=username).first_or_404()
    if request.method == 'POST':
        content = request.form['content']
        if content.strip():
            msg = Message(sender=current_user, recipient=other, content=content)
            db.session.add(msg)
            db.session.commit()
            flash('Message sent!', 'success')
        return redirect(url_for('conversation', username=other.username))
    # Mark all messages from other as read
    Message.query.filter_by(sender=other, recipient=current_user, read=False).update({'read': True})
    db.session.commit()
    messages = Message.query.filter(
        ((Message.sender == current_user) & (Message.recipient == other)) |
        ((Message.sender == other) & (Message.recipient == current_user))
    ).order_by(Message.timestamp.asc()).all()
    return render_template('conversation.html', other=other, messages=messages)

@app.route('/message/send/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    content = request.form['content']
    if not content.strip():
        flash('Message cannot be empty.', 'danger')
        return redirect(request.referrer or url_for('home'))
    msg = Message(sender=current_user, recipient=recipient, content=content)
    db.session.add(msg)
    db.session.commit()
    flash('Message sent!', 'success')
    return redirect(url_for('conversation', username=recipient.username))

# Removed /inbox and /outbox routes as Conversations replaces their functionality

@app.route('/favorite/<int:listing_id>', methods=['POST'])
@login_required
def favorite_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing in current_user.favorites:
        flash('Already in favorites.', 'info')
    elif listing.seller == current_user:
        flash('You cannot favorite your own listing.', 'danger')
    else:
        current_user.favorites.append(listing)
        db.session.commit()
        flash('Added to favorites.', 'success')
    return redirect(request.referrer or url_for('listings'))

@app.route('/unfavorite/<int:listing_id>', methods=['POST'])
@login_required
def unfavorite_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing in current_user.favorites:
        current_user.favorites.remove(listing)
        db.session.commit()
        flash('Removed from favorites.', 'info')
    return redirect(request.referrer or url_for('listings'))

@app.route('/my_favorites')
@login_required
def my_favorites():
    listings = current_user.favorites.order_by(Listing.id.desc()).all()
    return render_template('my_favorites.html', listings=listings)

@app.route('/my_purchases')
@login_required
def my_purchases():
    listings = Listing.query.filter_by(reserved_by=current_user, status='Sold').order_by(Listing.id.desc()).all()
    return render_template('my_purchases.html', listings=listings)

@app.route('/my_sales')
@login_required
def my_sales():
    listings = Listing.query.filter_by(seller=current_user, status='Sold').order_by(Listing.id.desc()).all()
    return render_template('my_sales.html', listings=listings)

@app.route('/review/<int:listing_id>/<int:reviewee_id>', methods=['POST'])
@login_required
def submit_review(listing_id, reviewee_id):
    listing = Listing.query.get_or_404(listing_id)
    reviewee = User.query.get_or_404(reviewee_id)
    rating = int(request.form['rating'])
    comment = request.form['comment']
    # Only allow review if user was buyer or seller and transaction is complete
    if listing.status != 'Sold' or (current_user != listing.seller and current_user != listing.reserved_by):
        flash('You cannot review this transaction.', 'danger')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    # Prevent duplicate reviews
    existing = Review.query.filter_by(reviewer=current_user, reviewee=reviewee, listing=listing).first()
    if existing:
        flash('You have already reviewed this user for this transaction.', 'info')
        return redirect(url_for('listing_detail', listing_id=listing.id))
    review = Review(reviewer=current_user, reviewee=reviewee, listing=listing, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    flash('Review submitted!', 'success')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/report/listing/<int:listing_id>', methods=['POST'])
@login_required
def report_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    reason = request.form['reason']
    report = Report(reporter=current_user, listing=listing, reason=reason)
    db.session.add(report)
    db.session.commit()
    flash('Report submitted. Thank you for helping keep the platform safe.', 'success')
    return redirect(url_for('listing_detail', listing_id=listing.id))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    reports = Report.query.order_by(Report.timestamp.desc()).all()
    users = User.query.all()
    listings = Listing.query.all()
    return render_template('admin_dashboard.html', reports=reports, users=users, listings=listings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 