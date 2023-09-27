## Getting Started
Project is configured to run on dockercompose up, and should migrate on start. To run the project, follow these steps:

1. Clone the repository: ``git clone https://github.com/MironPawlak/assignment.git``
2. Run the following command to build and start the containers:: ``docker-compose up --build``
3. Migrations will perform automatically
4. ``create_tiers`` command will also perform automatically and create objects: superuser with login:'admin'; password:'admin', three bultin account tiers, and two thumbnail sizes.

## Testing
To run test, use the following command
``docker exec -it assignment-web-1 python3 manage.py test``
