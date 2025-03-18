# Microsoft SQL Server
docker run -d --name marketsync_mssql_server -p 10001:1433 -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong!Passw0rd" mcr.microsoft.com/mssql/server:2022-latest

# Mongodb
docker run -d --name marketsync_mongodb -p 10003:27017 -e MONGO_INITDB_ROOT_USERNAME=system_admin -e MONGO_INITDB_ROOT_PASSWORD=marketsyncpassword mongo:8.0
