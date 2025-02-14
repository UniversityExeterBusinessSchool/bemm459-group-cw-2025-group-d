# postgres
docker run -d -p 10001:5432 --name marketsync-postgres -e POSTGRES_PASSWORD=marketsyncpassword -e POSTGRES_USER=system_admin -e POSTGRES_DB=marketsync_database postgres:15.10
# redis
docker run -d -p 10002:6379 --name marketsync-redis -e REDIS_PASSWORD=marketsyncpassword redis:7.4.2
# mongodb
docker run -d -p 10003:27017 --name marketsync-mongo -e MONGO_INITDB_ROOT_USERNAME=system_admin -e MONGO_INITDB_ROOT_PASSWORD=marketsyncpassword mongo:8.0
# elasticsearch
docker run -d -p 10004:9200 --name marketsync-elasticsearch -e "discovery.type=single-node" -e "ELASTIC_PASSWORD=marketsyncpassword" elasticsearch:8.17.1