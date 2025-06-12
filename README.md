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
- 🎯 **Interactive mode**: Browse and select secrets with arrow key navigation
- 📋 Visual secret browser with professional terminal UI

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

### Direct Secret Access
```bash
# View secret data in a formatted table
kubesecret <secret-name>

# Export secret as YAML manifest (creates <secret-name>.yaml file)
kubesecret <secret-name> --export

# Export to specific file
kubesecret <secret-name> --export --output secret.yaml
```

### Interactive Mode
```bash
# Launch interactive secret browser (no secret name required)
kubesecret

# Interactive mode with export option (creates <selected-secret>.yaml file)
kubesecret --export
```

When you run `kubesecret` without a secret name, it enters **interactive mode** with a beautiful terminal interface where you can:
- 🎯 Browse all available secrets in your current namespace
- ⌨️ Navigate with arrow keys (↑/↓)
- ⏎ Select secrets with Enter
- 🚪 Exit with 'q' or Ctrl+C

### Examples

#### Direct Access
```bash
# View a secret named 'my-app-secrets'
kubesecret my-app-secrets

# Export secret as YAML file (creates my-app-secrets.yaml)
kubesecret my-app-secrets --export

# Export secret to file for deployment in another cluster
kubesecret my-app-secrets -e -o production-secret.yaml
```

#### Interactive Mode
```bash
# Browse all secrets interactively
kubesecret

# Interactive browse and export selected secret (creates <selected-secret>.yaml)
kubesecret --export

# View secrets in a specific namespace (using kubectl context)
kubectl config set-context --current --namespace=my-namespace
kubesecret  # Now shows secrets from my-namespace
```

### Export Features

- **Sanitized output**: Removes cluster-specific metadata (resourceVersion, uid, etc.)
- **Portable YAML**: Ready to apply in different clusters
- **Base64 preserved**: Maintains original secret encoding
- **Auto-file creation**: Creates `<secret-name>.yaml` files automatically when using `--export`
- **Flexible output**: Export to file or stdout

## Requirements

- Python ≥ 3.6
- kubectl configured with cluster access

## Interactive Mode

The interactive mode provides a modern terminal UI powered by [Textual](https://github.com/Textualize/textual) that makes browsing secrets intuitive and efficient:

- **Professional Interface**: Clean, responsive terminal UI with header, footer, and focused navigation
- **Smooth Navigation**: Flicker-free scrolling through long lists of secrets
- **Keyboard Shortcuts**: Standard arrow key navigation with Enter to select
- **Visual Feedback**: Clear highlighting of selected items
- **Namespace Aware**: Automatically shows secrets from your current kubectl context/namespace
- **Fallback Support**: Gracefully falls back to numbered selection if needed

Perfect for:
- 🔍 **Discovery**: When you don't know the exact secret name
- 📋 **Browsing**: Exploring what secrets exist in a namespace  
- ⚡ **Quick Access**: Faster than typing long secret names
- 🎯 **Visual Selection**: See all options before choosing
