# Synthesia Challenge
Synthesia Challenge APIs are implemented using [FastAPI](https://fastapi.tiangolo.com/) framework in python to solve the [hiring challenge](https://www.notion.so/Synthesia-Backend-Tech-Challenge-52a82f750aed436fbefcf4d8263a97be). 

The application implements a GET Endpoint `/crypto/sign` with a mandatory query field `message` and an optional field `callback_url`. The api returns a json response 
 * `{"success":true,"data":<signed_message>}` with status code `200 OK` if the upstream request is successfull
 * `{"success":true,"data":null}` with status code `200 OK` if the upstream request is unsuccessfull. If the optional query field `callback_url` is provided, the upstream request will be retried (asynchronously) and the `callback_url` endpoint will be notified on success with a POST json body `{"success":true,"data":<signed_message>}`.

The following libraries are used for following functions

- [uvicorn](https://www.uvicorn.org/) and [gunicorn](https://gunicorn.org/): Python servers to run api
- [typer](https://typer.tiangolo.com/): Used to create command line applications
- [python-rq](https://python-rq.org/): Used to enqueue tasks/jobs using redis.
- [rq-scheduler](https://github.com/rq/rq-scheduler) A lightwight task/job scheduler to schedule tasks/jobs in redis queue
- [httpx](https://www.python-httpx.org/): Used to call external API endpoints asynchronously

## Project Structure

All the application code can be found inside [app](./app/) folder. Database migration scripts can be found under [versions](./migrations/versions/) folder

The application code is divided into following code structure

- [settings](./app/__init__.py/): All the configuration for the api application and worker can be found here.
- [clients](./app/clients/): All External clients (api and redis queue) lives here.
- [handlers](./app/handlers/): The main application business logic lives here
- [routers](./app/routers/): The api call function lives here. Router functions call handler functions to read/write data.
- [tests](./tests/): Unit test files lives here.


## Local development and testing

The application can be run locally using [DockerCompose](https://docs.docker.com/compose/) that has the 
 * api container to serve the api requests
 * redis container used as a message queue
 * rqworker container that runs the scheduled worker tasks/jobs
 * rqscheduler containter that schedules the jobs at specific times

### Commands

To run locally, we need a `.env` file with the config `CRYPTO_CLIENT_API_KEY=<synthesia_api_key>` used to authenticate the API requests. All the necessary containers use docker-compose command `docker-compose up -d`

To check the logs for the api application use the command `docker-compose logs -f api`
To check the logs for the worker `docker-compose logs -f rqworker`
