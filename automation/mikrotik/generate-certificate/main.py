import argparse
import os
import sys
from getpass import getpass

import routeros_api
import routeros_api.exceptions
import yaml


def parse_args() -> dict:
    parser = argparse.ArgumentParser(description="CMD arguments parser")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="config/main.yaml",
        help="Path to config file (default: config/main.yaml)",
    )
    parser.add_argument(
        "--ca-name",
        type=str,
        default="",
        help="Name of existing CA certificate (optional)",
    )
    return vars(parser.parse_args())


def get_user_input() -> dict:
    parameters = {}
    parameters["host"] = input("[?] Enter host name: ")
    parameters["username"] = input("[?] Enter username [admin]: ") or "admin"
    parameters["password"] = getpass("[?] Enter password: ")
    parameters["certificates"] = []

    if parameters["host"] == "":
        raise ValueError("Host can not be empty")

    if os.path.isfile(CMD_ARGS["config"]):
        with open(CMD_ARGS["config"], "r", encoding="utf-8") as config_file:
            parameters |= yaml.load(config_file, yaml.SafeLoader)
    else:
        raise RuntimeError("Configuration file not found")

    return parameters


def generate_certificate(cert_params: dict, ca: dict = None) -> None:
    if ca is None:
        ca = {}

    try:
        api = routeros_api.connect(
            host=PARAMETERS["host"],
            username=PARAMETERS["username"],
            password=PARAMETERS["password"],
            plaintext_login=True,
        )
    except routeros_api.exceptions.RouterOsApiCommunicationError as e:
        print(str(e.original_message, encoding="utf-8"))
        sys.exit(-1)

    print(f"[*] Creating certificate: {cert_params['name']}")
    payload = {
        "name": cert_params["name"],
        "country": PARAMETERS["global"]["country"],
        "state": PARAMETERS["global"]["state"],
        "locality": PARAMETERS["global"]["locality"],
        "organization": PARAMETERS["global"]["organization"],
        "common_name": cert_params.get("commonName", cert_params["name"]),
        "subject_alt_name": f"{cert_params['subjectAltNameType']}:{cert_params['name']}",
        "key_size": cert_params.get("keySize", str(2048)),
        "days_valid": cert_params.get("daysValid", str(365)),
        "key_usage": ",".join(cert_params["keyUsage"]),
        "trusted": cert_params.get("trusted", "no"),
    }
    try:
        api.get_resource("/certificate").add(**payload)
    except routeros_api.exceptions.RouterOsApiCommunicationError as e:
        print(str(e.original_message, encoding="utf-8"))
        sys.exit(-1)

    print("[*] Signing...")
    if cert_params.get("ca", False):
        api.get_resource("/certificate").call(
            "sign", arguments={".id": cert_params["name"]}
        )
    else:
        api.get_resource("/certificate").call(
            "sign", arguments={".id": cert_params["name"], "ca": ca["name"]}
        )


def main() -> None:
    ca = {}
    for idx, c in enumerate(PARAMETERS["certificates"]):
        if c.get("ca", False):
            ca = PARAMETERS["certificates"].pop(idx)
            generate_certificate(ca)
            break
    else:
        ca["name"] = CMD_ARGS["ca_name"]
        try:
            if ca["name"] == "":
                raise ValueError(
                    "Either name of existing CA certificate should be specified, or certificate with CA flag in config file"
                )
        except ValueError as e:
            print(e)
            sys.exit(-1)

    for c in PARAMETERS["certificates"]:
        generate_certificate(c, ca)


if __name__ == "__main__":
    CMD_ARGS = parse_args()

    try:
        PARAMETERS = get_user_input()
    except (ValueError, RuntimeError) as e:
        print(e)
        sys.exit(-1)

    main()
