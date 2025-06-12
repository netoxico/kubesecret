# Kubesecret

A CLI tool for Kubernetes secrets that provides a user-friendly way to view secret data. It fetches secrets using `kubectl` and displays them in a formatted table with base64-decoded values.

## Why use kubesecret?

While `kubectl` can retrieve secrets, kubesecret offers several advantages:

- **🔍 Readable output**: View decoded secret values in a formatted table instead of raw base64
- **🧹 Clean exports**: Automatically removes cluster-specific metadata for portable YAML manifests  
- **⚡ Simple commands**: Single command instead of complex kubectl pipes and base64 decoding
- **🎨 Better UX**: Rich formatting with syntax highlighting vs plain YAML output
- **🚀 Focused tool**: Purpose-built for secret management workflows

**Compare this:**
```bash
# kubectl approach (complex)
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
kubectl get secret my-secret -o yaml | kubectl neat > clean-secret.yaml

# kubesecret approach (simple)  
kubesecret my-secret
kubesecret my-secret --export -o clean-secret.yaml
```

## Features

- 🔓 View Kubernetes secret data in a readable format
- 📊 Rich table output with syntax highlighting  
- 🔍 Base64 decoding of secret values
- ⚡ Simple command-line interface

## Prerequisites

- `kubectl` installed and configured
- Access to a Kubernetes cluster

## Installation

### Using uv (recommended)
```bash
uv tool install kubesecret
```

### Using pip
```bash
pip install kubesecret
```

### Development installation
```bash
uv tool install -e .
```

## Usage

```bash
# View secret data in a formatted table
kubesecret <secret-name>

# Export secret as YAML manifest
kubesecret <secret-name> --export

# Export to file
kubesecret <secret-name> --export --output secret.yaml
```

### Examples

```bash
# View a secret named 'my-app-secrets'
kubesecret my-app-secrets

# Export secret as YAML to stdout
kubesecret my-app-secrets --export

# Export secret to file for deployment in another cluster
kubesecret my-app-secrets -e -o production-secret.yaml

# View a secret in a specific namespace (using kubectl context)
kubectl config set-context --current --namespace=my-namespace
kubesecret my-app-secrets
```

### Export Features

- **Sanitized output**: Removes cluster-specific metadata (resourceVersion, uid, etc.)
- **Portable YAML**: Ready to apply in different clusters
- **Base64 preserved**: Maintains original secret encoding
- **Flexible output**: Export to file or stdout

## Requirements

- Python ≥ 3.6
- kubectl configured with cluster access
