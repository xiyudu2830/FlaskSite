# Deployment Guide

This guide provides instructions for deploying the Second-Hand Trading Platform to production.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Web server (Nginx, Apache, etc.)
- WSGI server (Gunicorn, uWSGI, etc.)

## Production Setup

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
DATABASE_URL=sqlite:///site.db
```

**Important**: Generate a strong secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install gunicorn  # For production WSGI server
```

### 3. Database Setup

```bash
# Create database tables
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 4. File Permissions

Ensure upload directories have proper permissions:

```bash
mkdir -p static/uploads static/avatars
chmod 755 static/uploads static/avatars
```

### 5. Using Gunicorn

Create a `gunicorn.conf.py` file:

```python
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

Run with Gunicorn:

```bash
gunicorn -c gunicorn.conf.py app:app
```

### 6. Nginx Configuration

Create `/etc/nginx/sites-available/flask-app`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/your/project/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/flask-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Systemd Service

Create `/etc/systemd/system/flask-app.service`:

```ini
[Unit]
Description=Flask Second-Hand Trading Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/venv/bin"
ExecStart=/path/to/your/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable flask-app
sudo systemctl start flask-app
```

## Security Considerations

### 1. HTTPS Setup

Install SSL certificate (Let's Encrypt):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 2. Firewall Configuration

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. Database Security

For production, consider using PostgreSQL:

```bash
pip install psycopg2-binary
```

Update `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 4. File Upload Security

- Set appropriate file size limits
- Validate file types
- Scan uploaded files for malware
- Use cloud storage (AWS S3, Google Cloud Storage) for large-scale deployments

## Monitoring

### 1. Logs

Monitor application logs:

```bash
sudo journalctl -u flask-app -f
```

### 2. Performance Monitoring

Install monitoring tools:

```bash
pip install prometheus_client
```

### 3. Backup Strategy

Set up automated backups:

```bash
# Database backup
sqlite3 instance/site.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# File backup
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz static/uploads/
```

## Scaling Considerations

### 1. Load Balancing

Use multiple Gunicorn workers and a load balancer.

### 2. Caching

Implement Redis for session storage and caching:

```bash
pip install redis
```

### 3. CDN

Use a CDN for static files (Cloudflare, AWS CloudFront).

### 4. Database Optimization

- Add database indexes
- Implement connection pooling
- Consider read replicas for high-traffic scenarios

## Troubleshooting

### Common Issues

1. **Permission Denied**: Check file permissions
2. **Database Locked**: Ensure only one process accesses SQLite
3. **Memory Issues**: Adjust Gunicorn worker count
4. **Static Files Not Loading**: Check Nginx configuration

### Debug Mode

For debugging, temporarily enable debug mode:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
2. **Database Maintenance**: Regular backups and cleanup
3. **Log Rotation**: Configure logrotate
4. **Security Updates**: Keep system packages updated

### Performance Tuning

1. **Database Queries**: Monitor slow queries
2. **Image Optimization**: Implement image compression
3. **Caching**: Add Redis caching layer
4. **CDN**: Use CDN for static assets

---

**Note**: This is a basic deployment guide. For enterprise deployments, consider using containerization (Docker) and orchestration tools (Kubernetes). 