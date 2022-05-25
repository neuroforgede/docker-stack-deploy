docker-stack-deploy (docker-sdp)
================================

docker-stack-deploy (docker-sdp) is a utility that wraps around dockers to but adds the following features:

- appends the first 12 characters of the SHA-1 hash of the contents of any config/secret to the name to ensure rolling updates always work

Installation
------------

```
pip3 install https://codeload.github.com/neuroforgede/docker-stack-deploy/zip/refs/tags/0.1.0
```

Usage
-----

In your docker stack deploy commands simply replace `docker` with `docker-sdp`. E.g:

```
docker-sdp stack deploy -c my_stack.yml mystack
```

It also supports multiple stack files (inheritance)

```
docker-sdp stack deploy -c my_stack.1.yml -c my_stack.2.yml mystack
```