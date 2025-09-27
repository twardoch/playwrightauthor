# Platform-Specific Guides

PlaywrightAuthor works across Windows, macOS, and Linux. Each platform has its quirks.

## Choose Your Platform

### [macOS Guide](macos.md)
- M1 vs Intel setup
- Security permissions
- Homebrew notes
- Gatekeeper workarounds

### [Windows Guide](windows.md)
- UAC settings
- Antivirus exceptions
- PowerShell policies
- Windows Defender tweaks

### [Linux Guide](linux.md)
- Distribution-specific steps
- Docker use
- Desktop environments
- Headless servers

## Quick Platform Detection

```python
from playwrightauthor import Browser
import platform

system = platform.system()
print(f"Running on: {system}")

# Platform-specific config
if system == "Darwin":  # macOS
    with Browser(args=["--disable-gpu-sandbox"]) as browser:
        pass
elif system == "Windows":
    with Browser(viewport_height=900) as browser:
        pass
else:  # Linux
    with Browser(headless=True) as browser:
        pass
```

## Common Cross-Platform Issues

### Chrome Installation Paths

| Platform | Default Chrome Locations |
|----------|-------------------------|
| **macOS** | `/Applications/Google Chrome.app`<br>`~/Applications/Google Chrome.app`<br>`/Applications/Chrome for Testing.app` |
| **Windows** | `C:\Program Files\Google\Chrome\Application\chrome.exe`<br>`C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`<br>`%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe` |
| **Linux** | `/usr/bin/google-chrome`<br>`/usr/bin/chromium`<br>`/snap/bin/chromium`<br>`/usr/bin/google-chrome-stable` |

### Profile Storage Locations

| Platform | PlaywrightAuthor Data Directory |
|----------|--------------------------------|
| **macOS** | `~/Library/Application Support/playwrightauthor/` |
| **Windows** | `%LOCALAPPDATA%\playwrightauthor\` |
| **Linux** | `~/.local/share/playwrightauthor/` |

### Environment Variables

Supported on all platforms:

```bash
# Custom Chrome path
export PLAYWRIGHTAUTHOR_CHROME_PATH="/path/to/chrome"

# Debug port
export PLAYWRIGHTAUTHOR_DEBUG_PORT="9333"

# Verbose logging
export PLAYWRIGHTAUTHOR_VERBOSE="true"

# Data directory
export PLAYWRIGHTAUTHOR_DATA_DIR="/custom/path"
```

## Docker Support

For consistent behavior across platforms:

```dockerfile
FROM python:3.12-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install PlaywrightAuthor
RUN pip install playwrightauthor

# Your application
COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

## Security Considerations

### macOS
- Terminal/IDE needs Accessibility permissions
- Chrome code signing checks
- Keychain for credentials

### Windows
- May need Administrator rights
- Defender scanning affects performance
- Credential Manager support

### Linux
- SELinux/AppArmor rules
- X11 vs Wayland
- sudo for system Chrome

## Performance

| Platform | Cold Start | Warm Start | Memory | Best For |
|----------|------------|------------|--------|----------|
| **macOS** | 2-3s | 0.5s | ~250MB | Development |
| **Windows** | 3-5s | 1s | ~300MB | Enterprise |
| **Linux** | 1-2s | 0.3s | ~200MB | Servers |

## Platform Optimizations

### macOS
```python
# Retina display support
with Browser(device_scale_factor=2) as browser:
    pass
```

### Windows
```python
# Proxy settings
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
```

### Linux
```python
# Headless mode
with Browser(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox']
) as browser:
    pass
```

## Resources

- [Installation Guide](../installation.md)
- [Troubleshooting](../auth/troubleshooting.md)
- [Performance Tips](../performance/optimization.md)
- [Docker Deployment](../deployment/docker.md)