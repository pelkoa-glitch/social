# Django Social Website 

### A simple social website where you can:

* Bookmark images from different sites via bookmarklet and share with your friends
* Follow other people
* Like other images

## Requirements

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [GNU Make](https://www.gnu.org/software/make/)
- [POETRY](https://python-poetry.org/)

## How to Use

1. **Clone the repository:**

   ```bash
   git clone https://github.com/pelkoa-glitch/social.git
2. Install all required packages in `Requirements` section.

3. Rename and fill the file `.env.example` with your dependencies'

4. Run command
    ```bash
        cd social
        poetry install  -  install dependencies
        poetry shell    -  activate python venv
        make all        -  command will run all docker containers

5. Go to your https://host:port and enjoy the app

### Implemented Commands

* `make app` - up application and database/infrastructure
* `make app-logs` - follow the logs in app container
* `make app-down` - down application and all infrastructure
* `make storages` - up only storages. you should run your application locally for debugging/developing purposes
* `make storages-logs` - follow the logs in storages container
* `make storages-down` - down all infrastructure
* `make redis` - up redis container
* `make redis-logs` - follow the logs in redis container
* `make redis-down` - down redis container

### Most Used Django Specific Commands

* `make migrations` - make migrations to models
* `make migrate` - apply all made migrations
* `make collectstatic` - collect static
* `make superuser` - create admin user
