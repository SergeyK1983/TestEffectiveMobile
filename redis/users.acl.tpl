user default off

user application on >{{APPLICATION_PASSWORD}} ~cache:* ~auth:refresh:* ~queue:* +@all -@dangerous +flushall +flushdb

user admin on >{{ADMIN_PASSWORD}} ~* +@all

user health on >{{HEALTH_PASSWORD}} ~* +ping