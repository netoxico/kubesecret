import subprocess
import re
import base64
import json
import yaml

import click
from rich.console import Console
from rich.table import Table

console = Console()


class SecretNotFoundError(Exception):
    def __init__(self, secret_name, origin_message):
        self.secret_name = secret_name
        self.origin_message = origin_message
        super().__init__(self.secret_name, self.origin_message)

    def __str__(self):
        return f"Secret '{self.secret_name}' not found, original message: {self.origin_message}"


def get_secret_data(secret_name):
    out = subprocess.Popen(
        ["kubectl", "get", "secret", secret_name, "-o", "jsonpath='{.data}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = out.communicate()

    if stderr:
        console.print(stderr)
        return None

    m = re.search(r"\{(.*?)\}", stdout.decode("utf-8"))
    if not m:
        raise SecretNotFoundError(secret_name, stdout)

    return json.loads(m.group(0))


def get_secret_full(secret_name):
    out = subprocess.Popen(
        ["kubectl", "get", "secret", secret_name, "-o", "json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = out.communicate()

    if stderr:
        console.print(stderr)
        return None

    try:
        return json.loads(stdout.decode("utf-8"))
    except json.JSONDecodeError:
        raise SecretNotFoundError(secret_name, stdout)


def print_table(secrets, secret_name):
    table = Table(title=f"🔓 {secret_name}")
    table.add_column("Key", justify="right", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    for key in secrets:
        table.add_row(key, base64.b64decode(secrets[key]).decode("utf-8"))
    console.print(table)


def create_exportable_yaml(secret_data, secret_name):
    sanitized_secret = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {"name": secret_name},
        "type": secret_data.get("type", "Opaque"),
        "data": secret_data["data"],
    }

    return yaml.dump(sanitized_secret, default_flow_style=False)


@click.command()
@click.argument("secret_name", required=True)
@click.option("--export", "-e", is_flag=True, help="Export secret as YAML manifest")
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default="-",
    help="Output file (default: stdout)",
)
def cli(secret_name, export, output):
    """CLI tool for Kubernetes secrets management.

    View or export Kubernetes secrets in a user-friendly format.
    """
    try:
        if export:
            secret_data = get_secret_full(secret_name)
            if secret_data:
                yaml_output = create_exportable_yaml(secret_data, secret_name)
                output.write(yaml_output)
                if output.name != "<stdout>":
                    console.print(
                        f"✅ Secret '{secret_name}' exported to {output.name}"
                    )
        else:
            secrets = get_secret_data(secret_name)
            if secrets:
                print_table(secrets, secret_name)
    except SecretNotFoundError:
        console.print_exception(show_locals=True)
