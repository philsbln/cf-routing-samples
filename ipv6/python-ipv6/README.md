# Python HTTP/2 H2C Sample

Example HTTP/2 server implemented in Python
## Deploying the python app
### Deploy the app using the manifest file
Deploy the app
```shell
export DOMAIN=my.cf.app.domain
cf push -f app-manifest.yml --var domain=$DOMAIN
```

### Deploy the app without the manifest file
```shell
cf push --no-route python-http2-test --buildpack https://github.com/cloudfoundry/python-buildpack
# my.cf.app.domain is used as an example for demonstration purpose
cf map-route python-http2-test my.cf.app.domain --hostname python-http2-test --app-protocol http2
```

## Testing the Python app
```shell
curl -v --http2-prior-knowledge https://python-http2-test.my.cf.app.domain 
```

The app supports HTTP/1.1 and HTTP/2 H2C if requested explicitly, i.e. no connection upgrade.

## Building and running on the local machine

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `PORT=8080 python3 main.py &`
5. `deactivate`
6. `curl -v --http2-prior-knowledge http://localhost:8080`
