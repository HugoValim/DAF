import docker

CONTAINER_NAME = "dafioc"
CONTAINER_IMAGE = "prjemian/custom-synapps-6.2:latest"
CONTAINER_OPTIONS = {
    "network": "host",
    "stdin_open": True,
    "tty": True,
    "name": CONTAINER_NAME,
    "detach": True,
    "auto_remove": True,
    "environment": ["PREFIX=daf:"],
    "entrypoint": "iocxxx/softioc/xxx.sh run",
}


def run_container():
    flag_for_run_the_container = True
    client = docker.from_env()
    for container in client.containers.list():
        if container.name == CONTAINER_NAME:
            flag_for_run_the_container = False
            break
    if flag_for_run_the_container:
        client.containers.run(CONTAINER_IMAGE, **CONTAINER_OPTIONS)
