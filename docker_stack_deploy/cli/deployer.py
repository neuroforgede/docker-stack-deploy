from tempfile import NamedTemporaryFile
from typing import Dict, Any, Tuple, List, Literal
import yaml
import sys
import os
import hashlib
import subprocess
from copy import deepcopy

VERBOSE: bool = os.getenv("SWARM_DEPLOYER_VERBOSE") == "1"
WORKING_DIRECTORY = os.getcwd()


def log(text: str) -> None:
    if VERBOSE:
        print(text)


def augment_secrets_or_config(
    definitions: Dict[str, Any], key: Literal["secrets", "configs"]
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    if key not in ["configs", "secrets"]:
        raise AssertionError("augmentation only allowed for configs or secrets")

    key_singular = key[-1]

    augmented: Dict[str, Any] = dict()
    new_keys: Dict[str, str] = dict()

    for key, definition in definitions.items():
        if "name" in definition:
            raise AssertionError(f"name detected in {key_singular}, not supported yet")

        path = definition.get("file")
        if not path:
            raise AssertionError(
                f"file path not set in {key_singular}, not supported yet"
            )

        augmented_definition = deepcopy(definition)

        path = os.path.join(WORKING_DIRECTORY, path)

        if not os.path.exists(path):
            raise AssertionError(f"did not find file at path {path}")

        augmented_definition["file"] = os.path.normpath(path)

        with open(path, "rb") as secret_file:
            version = hashlib.sha1(secret_file.read()).hexdigest()[:12]

        new_key = key + "_" + version

        if len(new_key) > 64:
            print(
                f"hashed {key_singular} with key and version is longer than 64 characters ({new_key}), please shorten it"
            )

        augmented[new_key] = augmented_definition
        new_keys[key] = new_key

    return augmented, new_keys


def augment_services(
    services: Dict[str, Any],
    new_secret_keys: Dict[str, str],
    new_config_keys: Dict[str, str],
) -> Dict[str, Any]:
    augmented = deepcopy(services)

    for service_key, service_definition in augmented.items():
        augmented_service_definition = deepcopy(service_definition)

        if "secrets" in augmented_service_definition:
            augmented_secret_list = []
            for elem in augmented_service_definition["secrets"]:
                augmented_secret_list.append(
                    {**elem, "source": new_secret_keys[elem["source"]]}
                )

            augmented_service_definition["secrets"] = augmented_secret_list

        if "configs" in augmented_service_definition:
            augmented_config_list = []
            for elem in augmented_service_definition["configs"]:
                augmented_config_list.append(
                    {**elem, "source": new_config_keys[elem["source"]]}
                )

            augmented_service_definition["configs"] = augmented_config_list

        augmented[service_key] = augmented_service_definition

    return augmented


def find_all_stack_files(argv: List[str]) -> List[Tuple[int, str]]:
    ret: List[Tuple[int, str]] = []

    found_c = False

    for index, value in zip(range(0, len(argv)), argv):
        if value == "-c":
            found_c = True
            continue
        if found_c:
            if not value.endswith("yml") and not value.endswith("yaml"):
                raise AssertionError(
                    f"expected stack file ending in yml or yaml at cli index {index}"
                )
            ret.append((index, value))
            found_c = False

    return ret


def private_opener(path, flags):
    return os.open(path, flags, 0o600)


def docker_stack_deploy() -> None:
    all_stack_files = find_all_stack_files(sys.argv)
    new_stack_files: Dict[str, str] = dict()
    for argv_idx, stack_file in all_stack_files:
        if stack_file in new_stack_files:
            raise AssertionError(f"repeated stackfile {stack_file}")

        with open(stack_file) as stack_yml:
            parsed = yaml.load(stack_yml.read(), yaml.FullLoader)

            parsed_augmented = deepcopy(parsed)

            augmented_secrets, new_secret_keys = augment_secrets_or_config(
                parsed.get("secrets", dict()), "secrets"
            )
            parsed_augmented["secrets"] = augmented_secrets

            augmented_configs, new_config_keys = augment_secrets_or_config(
                parsed.get("configs", dict()), "configs"
            )
            parsed_augmented["configs"] = augmented_configs

            augmented_services = augment_services(
                parsed.get("services", dict()),
                new_secret_keys=new_secret_keys,
                new_config_keys=new_config_keys,
            )
            parsed_augmented["services"] = augmented_services

            with NamedTemporaryFile("w", delete=False) as file:
                new_stack_files[stack_file] = file.name
                yaml.dump(parsed_augmented, file)
                if VERBOSE:
                    print(f"augmented stack file for {stack_file}:\n")
                    print(yaml.dump(parsed_augmented))

    forwarded_params: List[str] = sys.argv[1:]
    for argv_idx, stack_file in all_stack_files:
        forwarded_params[argv_idx - 1] = new_stack_files[stack_file]

    new_cmd = ["/bin/docker", *forwarded_params]
    if VERBOSE:
        print("running docker command:")
        print(" ".join(new_cmd))
        print("")

    subprocess.check_call(
        new_cmd,
        env={
            **os.environ,
        },
        cwd=os.getcwd(),
    )
    log("\nsuccess.")

    log("cleaning up.")
    for argv_idx, stack_file in all_stack_files:
        os.unlink(new_stack_files[stack_file])
    log("done.")


def usage() -> None:
    print(
        """
docker-stack-deploy (docker-sdp)
================================

docker-stack-deploy (docker-sdp) is a utility that wraps around dockers to but adds the following features:

- appends the first 12 characters of the SHA-1 hash of the contents of any config/secret to the name to ensure rolling updates always work

Usage of docker stack deploy follows:"""
    )
    subprocess.check_call(
        ["/bin/docker", "stack", "deploy", "--help"],
        env={
            **os.environ,
        },
        cwd=os.getcwd(),
    )


def main() -> None:
    if len(sys.argv) >= 3:
        if sys.argv[2] == "stack" and sys.argv[3] == "deploy":
            docker_stack_deploy()
            return
    else:
        usage()
