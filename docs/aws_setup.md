# Deploying Django on Amazon EC2: A Step-by-Step Guide

## 1. Launching an EC2 Instance

1. Log in to AWS and navigate to **EC2**.
2. Click **Launch Instance**.
3. Configure the instance:
   - **Name**: Choose a relevant name.
   - **OS Image**: Select **Ubuntu**.
   - **Instance Type**: Choose **t3.micro**.
   - **Key Pair**: Create a new key pair and download the `.pem` file.
   - **Security Groups**:
     - Create a new security group and configure **Inbound Rules**:
       - SSH: Allow **0.0.0.0/0** (restricted to your IP for security).
       - HTTP: Allow **0.0.0.0/0** and **::/0** (for public access).
4. Click **Launch Instance**.
5. Assign an **Elastic IP**:
   - Navigate to **Elastic IPs** → Allocate a new IP.
   - Associate it with the newly launched EC2 instance.

## 2. Connecting to the EC2 Instance

1. Move the key pair to a secure location:

   ```bash
   mv /mnt/c/Users/seyi/Downloads/fadamasi.pem ~/.ssh/
   chmod 600 ~/.ssh/fadamasi.pem
   ```

2. Connect via SSH:

   ```bash
   ssh -i ~/.ssh/fadamasi.pem ubuntu@<your-ec2-ip>
   ```

3. Simplify SSH access by creating a config file:

   ```bash
   nano ~/.ssh/config
   ```

   Add the following:

   ```
   Host fadamasi
       HostName <your-ec2-ip>
       User ubuntu
       IdentityFile ~/.ssh/fadamasi.pem
   ```

   Now, connect using:

   ```bash
   ssh fadamasi
   ```

4. Update and install required packages:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl redis
   ```

## 3. Creating a Dedicated User (Optional)

```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
su - deploy
```

## 4. Cloning the Django Project

1. Set up SSH key for Git authentication:

   ```bash
   ssh-keygen -t rsa -b 4096 -C "prontomaster@gmail.com"
   cat ~/.ssh/id_rsa.pub
   ```

   Add the key to GitHub under **Settings** → **Deploy Keys**.
2. Clone the repository:

   ```bash
   git clone git@github.com:The-Backyard/fadamasi_backend.git
   ```

## 5. Setting Up the Virtual Environment

```bash
cd fadamasi_backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Configuring PostgreSQL

1. Switch to the PostgreSQL shell:

   ```bash
   sudo -u postgres psql
   ```

2. Create a database and user:

   ```sql
   CREATE USER fadamasiuser WITH PASSWORD 'fadamasipassword';
   ALTER ROLE fadamasiuser SET client_encoding TO 'utf8';
   ALTER ROLE fadamasiuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE fadamasiuser SET timezone TO 'UTC';
   CREATE DATABASE fadamasidb OWNER fadamasiuser;
   GRANT ALL PRIVILEGES ON DATABASE fadamasidb TO fadamasiuser;
   \q
   ```

## 7. Configuring Gunicorn

```bash
sudo nano /etc/systemd/system/gunicorn.service
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:www-data /var/log/gunicorn
sudo chmod 775 /var/log/gunicorn
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl status gunicorn
```

## 8. Configuring Nginx

1. Create an Nginx configuration file:

   ```bash
   sudo nano /etc/nginx/sites-available/fadamasi_backend
   ```

2. Create a symbolic link:

   ```bash
   sudo ln -s /etc/nginx/sites-available/fadamasi_backend /etc/nginx/sites-enabled
   ```

3. Test and restart Nginx:

   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   sudo systemctl status nginx
   ```

## 9. Securing the Server with UFW (Firewall)

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 10. Configuring Static Files Permissions

```bash
python manage.py collectstatic
sudo chown -R www-data:www-data /home/ubuntu/fadamasi_backend/assets/
sudo chmod -R 755 /home/ubuntu/fadamasi_backend/assets/
sudo chmod +x /home/ubuntu
sudo chmod +x /home/ubuntu/fadamasi_backend
```

## 11. Finishing Up

```bash
python manage.py createsuperuser
```

--------------------------------------

# Django Deployment Guide: Amazon EC2 Setup and Configuration

## Overview

This guide provides a comprehensive walkthrough for deploying a Django project on an Amazon EC2 instance, covering everything from initial server setup to project deployment.

## Prerequisites

- AWS Account
- Django Project
- Basic Linux and command-line knowledge

## 1. AWS EC2 Instance Setup

### 1.1 Launch EC2 Instance

1. Log in to Amazon AWS Console
2. Navigate to EC2 Dashboard
3. Click "Launch Instances"

#### Instance Configuration

- **Operating System**: Ubuntu
- **Instance Type**: t3.micro or t2.micro
- **Security Group**: Configure to allow:
  - SSH (port 22)
  - HTTP (port 80)
  - HTTPS (port 443)

### 1.2 Create and Manage Security Groups

1. Create a new security group
2. Configure Inbound Rules:
   - SSH: Allow from your IP or 0.0.0.0/0 (use cautiously)
   - HTTP: Allow from 0.0.0.0/0
   - HTTPS: Allow from 0.0.0.0/0

### 1.3 Key Pair Management

1. Create a new key pair or use an existing one
2. Save the `.pem` file securely
3. Set appropriate permissions:

   ```bash
   chmod 600 ~/.ssh/your-key.pem
   ```

## 2. Initial Server Setup

### 2.1 Connect to Your Instance

```bash
# Using SSH
ssh -i ~/.ssh/your-key.pem ubuntu@your-instance-ip

# Simplify SSH Access (optional)
# Edit ~/.ssh/config
Host myserver
    HostName your-instance-address
    User ubuntu
    IdentityFile ~/.ssh/your-key.pem
```

### 2.2 System Updates

```bash
sudo apt update && sudo apt upgrade -y
```

### 2.3 Install Required Packages

```bash
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    curl \
    redis
```

## 3. Database Setup (PostgreSQL)

### 3.1 Create Database User and Database

```bash
# Switch to PostgreSQL
sudo -u postgres psql

# Create user
CREATE USER myprojectuser WITH PASSWORD 'mypassword';

# Configure user settings
ALTER ROLE myprojectuser SET client_encoding TO 'utf8';
ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myprojectuser SET timezone TO 'UTC';

# Create database
CREATE DATABASE myprojectdb OWNER myprojectuser;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE myprojectdb TO myprojectuser;

# Exit psql
\q
```

## 4. Project Deployment

### 4.1 Git Authentication

**Option 1: SSH Key**

```bash
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"

# Display public key to add to GitHub
cat ~/.ssh/id_rsa.pub
```

**Option 2: Personal Access Token**

1. Generate token on GitHub
2. Use in clone URL

### 4.2 Clone and Setup Project

```bash
# Clone repository
git clone your-repo-url

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Database and static files
cp .env.example .env
python manage.py migrate
python manage.py collectstatic
```

## 5. Gunicorn Configuration

### 5.1 Create Gunicorn Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/gunicorn.service

# Example configuration
[Unit]
Description=Gunicorn Django Daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/path/to/your/project
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/gunicorn.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 5.2 Manage Gunicorn Service

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

## 6. Nginx Configuration

### 6.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/myproject

# Configure server block for your project
```

### 6.2 Enable and Test Nginx

```bash
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Firewall and Security

### 7.1 Configure UFW

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 8. Final Steps

### 8.1 Static Files Permissions

```bash
python manage.py collectstatic
sudo chown -R www-data:www-data /path/to/static/files
sudo chmod -R 755 /path/to/static/files
```

### 8.2 Create Superuser

```bash
python manage.py createsuperuser
```

## Troubleshooting

- Check Gunicorn logs: `sudo tail -f /var/log/gunicorn/error.log`
- Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
