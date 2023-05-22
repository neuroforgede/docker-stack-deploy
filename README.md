Proudly made by [NeuroForge](https://neuroforge.de/) in Bayreuth, Germany.

docker-stack-deploy (docker-sdp)
================================

docker-stack-deploy (docker-sdp) is a utility that wraps around dockers to but adds the following features:

- appends the first 12 characters of the SHA-1 hash of the contents of any config/secret to the name to ensure rolling updates always work

Why?
----

Docker Stack files are a great way to organize your deployments. The problem is, though, that Docker Swarm does not allow changes in secrets and configs.
This means that you have to manually rotate configs/secrets yourself.

Another smart solution people have come up with is appending the hashcode of the secret/config via an env var in the stack file, like so:

```
secrets:
  my_secret:
    name: "my_secret_${HASH}"
    file: ./my/secret
```

This however requires manually wrapping the deployment script in a process that generates this hash.

With docker-stack-deploy, this is not required anymore. docker-stack-deploy is a small python script that wraps around the actual `docker stack deploy` command and intercepts any stack files in the arguments. Then, it rewrites the stack files by appending the hash like so:

```
secrets:
  my_secret_<SHA hash truncated to 12 chars>:
    file: ./my/secret
```

Next, it searches for all occurences of the secret/config in service definitions and remaps them accordingly.

Any manually generated secret names and config names (set via the name property) will be left untouched.

Installation
------------

```
pip3 install https://github.com/neuroforgede/docker-stack-deploy/archive/refs/tags/0.2.9.zip
```

Usage
-----

In your docker stack deploy commands simply replace `docker` with `docker-sdp`. E.g:

```
docker-sdp stack deploy -c my_stack.yml mystack
```

It also supports multiple stack files (inheritance) as long as secrets are not mixed between the files.

```
docker-sdp stack deploy -c my_stack.1.yml -c my_stack.2.yml mystack
```
