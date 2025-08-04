# Platform-Specific Guides

PlaywrightAuthor is designed to work seamlessly across Windows, macOS, and Linux. However, each platform has unique considerations for optimal setup and operation.

## 📱 Choose Your Platform

### [macOS Guide](macos.md)
- M1/Intel differences
- Security permissions setup
- Homebrew integration
- Gatekeeper handling

### [Windows Guide](windows.md)
- UAC considerations
- Antivirus whitelisting
- PowerShell execution policies
- Windows Defender configuration

### [Linux Guide](linux.md)
- Distribution-specific installation
- Docker containerization
- Desktop environment considerations
- Headless server setup

## 🎯 Quick Platform Detection

```python
from playwrightauthor import Browser
import platform

system = platform.system()
print(f"Running on: {system}")

# Platform-specific configuration
if system == "Darwin":  # macOS
    # macOS specific settings
    with Browser(args=["--disable-gpu-sandbox"]) as browser:
        # Your automation code
        pass
elif system == "Windows":
    # Windows specific settings
    with Browser(viewport_height=900) as browser:
        # Your automation code
        pass
else:  # Linux
    # Linux specific settings
    with Browser(headless=True) as browser:
        # Your automation code
        pass
```

## 🔧 Common Cross-Platform Issues

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

All platforms support these environment variables:

```bash
# Custom Chrome executable path
export PLAYWRIGHTAUTHOR_CHROME_PATH="/path/to/chrome"

# Custom debug port
export PLAYWRIGHTAUTHOR_DEBUG_PORT="9333"

# Enable verbose logging
export PLAYWRIGHTAUTHOR_VERBOSE="true"

# Custom data directory
export PLAYWRIGHTAUTHOR_DATA_DIR="/custom/path"
```

## 🐳 Docker Support

For consistent cross-platform behavior, use our Docker image:

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

## 🔐 Security Considerations by Platform

### macOS
- Terminal/IDE needs Accessibility permissions
- Chrome requires code signing validation
- Keychain access for secure credential storage

### Windows
- Run as Administrator may be required
- Windows Defender real-time scanning impacts
- Credential Manager integration

### Linux
- SELinux/AppArmor policies
- X11 vs Wayland display servers
- sudo requirements for system Chrome

## 📊 Performance Characteristics

| Platform | Cold Start | Warm Start | Memory Usage | Best For |
|----------|------------|------------|--------------|----------|
| **macOS** | 2-3s | 0.5s | ~250MB | Development |
| **Windows** | 3-5s | 1s | ~300MB | Enterprise |
| **Linux** | 1-2s | 0.3s | ~200MB | Servers |

## 🚀 Platform-Specific Optimizations

### macOS
```python
# Optimize for Retina displays
with Browser(device_scale_factor=2) as browser:
    # High DPI screenshots
    pass
```

### Windows
```python
# Handle Windows-specific paths
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
```

### Linux
```python
# Headless optimization
with Browser(
    headless=True,
    args=['--no-sandbox', '--disable-setuid-sandbox']
) as browser:
    # Server-side automation
    pass
```

## 📚 Additional Resources

- [Installation Guide](../installation.md)
- [Troubleshooting Guide](../auth/troubleshooting.md)
- [Performance Optimization](../performance/optimization.md)
- [Docker Deployment](../deployment/docker.md)