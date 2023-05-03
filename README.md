# SalesFoo ML

## Getting Started

    pip install pipenv
    pipenv install
    pipenv shell
    python manage.py runserver

## Build and Test

To Run Database Migrations :

    python manage.py makemigrations
    python manage.py migrate

## Common Bugs:

### Deployed Server giving 500

- Issue 1 : No Requirements
  pipenv run pip freeze > requirements.txt
  update your requirements
  make sure requirements in same directory as manage.py

- poperly set django settings directory as salesfoo.settings

### Deployed Server not serving static files fix,

I've solved this problem by adding this 2 lines to the top of <handlers> section in root web.config file:

    <remove name="Python27_via_FastCGI" />
    <remove name="Python34_via_FastCGI" />

Everything else is the same as your's web.config and I didn't need separate config file in static/ directory

- https://stackoverflow.com/questions/45292372/django-azure-serving-static-files-in-production

## References:

- https://www.deploymachinelearning.com/
- https://stackoverflow.com/questions/47218362/microsoft-azure-app-service-storage
