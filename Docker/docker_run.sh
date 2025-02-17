# postgres
docker run -d -p 10001:5432 --name marketsync-postgres -e POSTGRES_PASSWORD=marketsyncpassword -e POSTGRES_USER=system_admin -e POSTGRES_DB=marketsync_database postgres:15.10
# mongodb
docker run -d -p 10003:27017 --name marketsync-mongo -e MONGO_INITDB_ROOT_USERNAME=system_admin -e MONGO_INITDB_ROOT_PASSWORD=marketsyncpassword mongo:8.0
