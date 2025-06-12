import subprocess
import re
import base64
import json
import yaml

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, OptionList
from textual.widgets.option_list import Option

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


def get_secrets_list():
    """Get list of available secrets from kubectl."""
    out = subprocess.Popen(
        ["kubectl", "get", "secrets", "-o", "jsonpath='{.items[*].metadata.name}'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = out.communicate()

    if stderr:
        console.print(stderr)
        return []

    # Parse the output and extract secret names
    output = stdout.decode("utf-8").strip("'")
    if not output:
        return []

    return output.split()


class SecretSelector(App):
    """Textual app for selecting secrets."""

    def __init__(self, secrets):
        super().__init__()
        self.secrets = secrets
        self.selected_secret = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            OptionList(*[Option(secret) for secret in self.secrets]),
            id="secrets-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Configure the app when it starts."""
        self.title = "🔓 Kubesecret - Select Secret"
        self.sub_title = "Use ↑/↓ to navigate, Enter to select, q to quit"

        # Focus on the option list
        option_list = self.query_one(OptionList)
        option_list.focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        self.selected_secret = str(event.option.prompt)
        self.exit()

    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "q":
            self.exit()


def select_secret_interactive(secrets):
    """Display secrets and allow user to select one interactively using Textual."""
    if not secrets:
        console.print("❌ No secrets found in the current namespace")
        return None

    if len(secrets) == 1:
        console.print(f"📋 Found 1 secret: [magenta]{secrets[0]}[/magenta]")
        if Confirm.ask("Select this secret?", default=True):
            return secrets[0]
        return None

    # Use Textual for interactive selection
    try:
        app = SecretSelector(secrets)
        app.run()
        return app.selected_secret
    except Exception:
        # Fallback to numbered selection if Textual fails
        console.print("📋 Available Secrets")

        table = Table()
        table.add_column("Index", justify="right", style="cyan", no_wrap=True)
        table.add_column("Secret Name", style="magenta")

        for i, secret in enumerate(secrets, 1):
            table.add_row(str(i), secret)

        console.print(table)

        from rich.prompt import Prompt

        while True:
            try:
                choice = Prompt.ask(f"Select a secret (1-{len(secrets)})", default="1")
                index = int(choice) - 1
                if 0 <= index < len(secrets):
                    return secrets[index]
                else:
                    console.print(
                        f"❌ Please enter a number between 1 and {len(secrets)}"
                    )
            except ValueError:
                console.print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return None


@click.command()
@click.argument("secret_name", required=False)
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

    If SECRET_NAME is provided, display that specific secret.
    If no SECRET_NAME is provided, enter interactive mode to select from available secrets.
    """
    try:
        # Interactive mode: no secret name provided
        if not secret_name:
            secrets = get_secrets_list()
            selected_secret = select_secret_interactive(secrets)

            if not selected_secret:
                return

            secret_name = selected_secret

        # Process the secret (either provided directly or selected interactively)
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
