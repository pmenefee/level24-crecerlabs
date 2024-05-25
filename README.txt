This configuration uses Docker to build a container in which you can run the code in the provided environment.

The first time you build the container it may take a few minutes (~600 seconds) as it has to download all of the supporting libs and models.
Subequent runs will run much faster.

To run:
docker-compose up --build -d

To shut down:
docker-compose down