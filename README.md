# Issue Tracker API 🐞

## Project description 📙

An issue tracking system API built with Django, supporting project collaboration, bug tracking, and feature requests.

### Features ✨

* Token-based authentication with role-based access control
* Project and member management
* Bug and feature request tracking across lifecycle stages,
* Versioned RESTful API with OpenAPI documentation

## Tech Stack ⚙️

* Python 3.12
* Django + Django REST Framework
* PostgreSQL
* Docker + Docker Compose
* Nginx
* Celery + Redis + Flower

## Getting Started 🚀

First, clone the repo:

```
git clone https://github.com/yourusername/issue-tracker.git
```

Before you launch the project, add the following entries to your hosts file (used by Nginx for local domain resolution — these can be changed in ```/docker/nginx/dev.conf``` and ```/docker/nginx/prod.conf```):
```
127.0.0.1      api.bugtracker.local
127.0.0.1      media.bugtracker.local
```

Next, start the app using one of the following:

* #### Development:
```
docker compose up
```

* #### Production:
```
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

The app should now be accessible at:

```
http://api.bugtracker.local/
```
(Use `https://` in the production environment)

## API Documentation 📚

Once the app is running, you can access OpenAPI documentation at:

```
http://api.bugtracker.local/api/v1/docs/
```
(Use `https://` in the production environment)

> **_NOTE_**: This repository includes a self-signed SSL certificate intentionally and only for demonstration purposes.\
In a real production environment, committing private keys for SSL certificates is a security risk and should never be done.
