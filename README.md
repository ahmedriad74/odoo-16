# Gold's Gym ERP System
 - odoo Community version 14
 -v5ud-96zr-x2f8



[![pipeline status](https://gitlab.objects.ws/odoo/golds-gym/badges/production/pipeline.svg)](https://gitlab.objects.ws/odoo/golds-gym/-/commits/production)


 
 **About Gold's Gym**
 
Gold's Gym International, Inc. is an American chain of international co-ed fitness centers originally started by Joe Gold in Venice Beach, California. Each gym offers a variety of cardio and strength training equipment as well as group exercise programs





## Getting Started
-This project contains the following modules:
 - [ ] HR
 - [ ] Accounting
 - [ ] Sales



### Prerequisites

 1. ubuntu os
 2. docker & docker-compose
way to install it 

[https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

### Installing

 1. clone repository
 
 ```
https://gitlab.objects.ws/odoo/golds-gym.git
```
 2. login to private docker image from Objects Docker Hub 
 
 -Docker Odoo 14 Community : 
 ```
docker pull objectsws/odoo:14.0.20210316
```

-- Username : objectsws
-- Password : 0bject$#123
    
```
docker login -u="objectsws" -p="0bject$#123"
```

 2. run docker-compose
```
docker-compose up --build
```


3. run initialize to upgrade modules 
```
docker-compose -f manage.yml build 
```
then
```
docker-compose -f manage.yml run initialize
```


## Development 
How to Develop in this Project?
 you have to put custom modules in addons Folder
 
##### Module Structure :
        my_module
        ├── __init__.py
        ├── __manifest__.py
        ├── controllers
        │   ├── __init__.py
        │   └── controllers.py
        ├── demo
        │   └── demo.xml
        ├── models
        │   ├── __init__.py
        │   └── models.py
        ├── security
        │   └── ir.model.access.csv
        └── views
            ├── templates.xml
            └── views.xml

## Deployment

 - live serve running :*
 
[![pipeline status](https://gitlab.objects.ws/odoo/golds-gym/badges/production/pipeline.svg)](https://gitlab.objects.ws/odoo/golds-gym/-/commits/production)




 - staging & training server :*
 
[![pipeline status](https://gitlab.objects.ws/odoo/golds-gym/badges/staging/pipeline.svg)](https://gitlab.objects.ws/odoo/golds-gym/-/commits/staging)


[http://staging.golds-gym.staging.objectsdev.com/](http://staging.golds-gym.staging.objectsdev.com/)

 - Master & development server :*

[![pipeline status](https://gitlab.objects.ws/odoo/golds-gym/badges/master/pipeline.svg)](https://gitlab.objects.ws/odoo/golds-gym/-/commits/master)

[http://master.golds-gym.staging.objectsdev.com/](http://master.golds-gym.staging.objectsdev.com/)
## Built With
* [Docker](https://maven.apache.org/) - Docker
* [Python 3]() 
* [Objects Odoo 14 Community](https://hub.docker.com/r/objectsws/odoo)
* [Postgres](https://rometools.github.io/rome/) - Docker Official Images
* [Ofelia]([https://hub.docker.com/r/mohamedhelmy/ofelia](https://hub.docker.com/r/mohamedhelmy/ofelia)) - Ofelia - a job scheduler
* [sync-with-s3]() - Docker image that runs a single cron job to sync files with S3
* [nginx]([https://hub.docker.com/_/nginx](https://hub.docker.com/_/nginx)) - Docker Official Images



## Contributing
Objects
## Versioning

...

## Authors

Objects

## License
...
