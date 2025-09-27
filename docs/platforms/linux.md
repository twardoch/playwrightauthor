# Linux Platform Guide

This guide covers Linux-specific setup, configuration, and troubleshooting for PlaywrightAuthor across various distributions.

## Quick Start

```bash
# Install PlaywrightAuthor
pip install playwrightauthor

# Install Chrome dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2

# First run
python -c "from playwrightauthor import Browser; Browser().__enter__()"
```

## Distribution-Specific Installation

### Ubuntu/Debian

```bash
# Add Google Chrome repository
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | \
    sudo tee /etc/apt/sources.list.d/google-chrome.list

# Install Chrome
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Or install Chromium
sudo apt-get install -y chromium-browser
```

### Fedora/CentOS/RHEL

```bash
# Add Chrome repository
sudo dnf config-manager --set-enabled google-chrome
cat << EOF | sudo tee /etc/yum.repos.d/google-chrome.repo
[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
EOF

# Install Chrome
sudo dnf install -y google-chrome-stable

# Or install Chromium
sudo dnf install -y chromium
```

### Arch Linux

```bash
# Install from AUR
yay -S google-chrome

# Or install Chromium
sudo pacman -S chromium
```

### Alpine Linux (Minimal/Docker)

```bash
# Install Chromium and dependencies
apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    font-noto-emoji
```

### Automated Distribution Detection

```python
import subprocess
import os

def detect_distribution():
    """Detect Linux distribution."""
    if os.path.exists('/etc/os-release'):
        with open('/etc/os-release') as f:
            info = dict(line.strip().split('=', 1) 
                       for line in f if '=' in line)
            return {
                'id': info.get('ID', '').strip('"'),
                'name': info.get('NAME', '').strip('"'),
                'version': info.get('VERSION_ID', '').strip('"')
            }
    return None

def install_chrome_dependencies():
    """Install Chrome dependencies based on distribution."""
    distro = detect_distribution()
    if not distro:
        print("Could not detect distribution")
        return
    
    print(f"Detected: {distro['name']} {distro['version']}")
    
    commands = {
        'ubuntu': [
            'sudo apt-get update',
            'sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2'
        ],
        'debian': [
            'sudo apt-get update',
            'sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2'
        ],
        'fedora': [
            'sudo dnf install -y nss nspr atk cups-libs'
        ],
        'centos': [
            'sudo yum install -y nss nspr atk cups-libs'
        ],
        'arch': [
            'sudo pacman -Sy --noconfirm nss nspr atk cups'
        ]
    }
    
    distro_id = distro['id'].lower()
    if distro_id in commands:
        for cmd in commands[distro_id]:
            print(f"Running: {cmd}")
            subprocess.run(cmd, shell=True)
    else:
        print(f"No automatic installation for {distro_id}")
```

## Docker Configuration

### Basic Dockerfile

```dockerfile
FROM python:3.12-slim

# Install Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Chrome dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    # Additional tools
    xvfb \
    x11vnc \
    fluxbox \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install PlaywrightAuthor
RUN pip install playwrightauthor

# Create non-root user
RUN useradd -m -s /bin/bash automation
USER automation
WORKDIR /home/automation

# Copy your application
COPY --chown=automation:automation . .

# Run with virtual display
CMD ["xvfb-run", "-a", "--server-args=-screen 0 1280x720x24", "python", "app.py"]
```

### Docker Compose with VNC Access

```yaml
version: '3.8'

services:
  playwrightauthor:
    build: .
    environment:
      - DISPLAY=:99
      - PLAYWRIGHTAUTHOR_HEADLESS=false
    volumes:
      - ./data:/home/automation/data
      - /dev/shm:/dev/shm  # Shared memory for Chrome
    ports:
      - "5900:5900"  # VNC port
    command: |
      bash -c "
        Xvfb :99 -screen 0 1280x720x24 &
        fluxbox &
        x11vnc -display :99 -forever -usepw -create &
        python app.py
      "
    shm_size: '2gb'  # Increase shared memory
    
  # Optional: Selenium Grid compatibility
  selenium-hub:
    image: selenium/hub:latest
    ports:
      - "4444:4444"
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: playwrightauthor
spec:
  replicas: 3
  selector:
    matchLabels:
      app: playwrightauthor
  template:
    metadata:
      labels:
        app: playwrightauthor
    spec:
      containers:
      - name: automation
        image: your-registry/playwrightauthor:latest
        env:
        - name: PLAYWRIGHTAUTHOR_HEADLESS
          value: "true"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: 1Gi
```

## Display Server Configuration

### X11 Setup

```python
import os
import subprocess

def setup_x11_display():
    """Setup X11 display for GUI mode."""
    # Check if display is set
    if 'DISPLAY' not in os.environ:
        # Try to detect running X server
        try:
            result = subprocess.run(['pgrep', 'Xorg'], capture_output=True)
            if result.returncode == 0:
                os.environ['DISPLAY'] = ':0'
            else:
                print("No X server detected, running headless")
                return False
        except:
            return False
    
    # Test X11 connection
    try:
        subprocess.run(['xset', 'q'], capture_output=True, check=True)
        return True
    except:
        print(f"Cannot connect to X11 display {os.environ.get('DISPLAY')}")
        return False

# Configure browser based on display availability
from playwrightauthor import Browser

has_display = setup_x11_display()
with Browser(headless=not has_display) as browser:
    # Browser runs in GUI mode if display available
    pass
```

### Wayland Support

```python
def setup_wayland():
    """Setup for Wayland display server."""
    # Check if running under Wayland
    if os.environ.get('WAYLAND_DISPLAY'):
        print("Wayland detected")
        
        # Use Xwayland if available
        if subprocess.run(['which', 'Xwayland'], capture_output=True).returncode == 0:
            os.environ['GDK_BACKEND'] = 'x11'
            return True
        else:
            # Native Wayland (experimental)
            os.environ['CHROMIUM_FLAGS'] = '--ozone-platform=wayland'
            return True
    
    return False

# Browser with Wayland support
wayland_args = []
if setup_wayland():
    wayland_args.extend([
        '--ozone-platform=wayland',
        '--enable-features=UseOzonePlatform'
    ])

with Browser(args=wayland_args) as browser:
    pass
```

### Virtual Display (Xvfb)

```python
import subprocess
import time
import atexit

class VirtualDisplay:
    """Manage Xvfb virtual display."""
    
    def __init__(self, width=1280, height=720, display_num=99):
        self.width = width
        self.height = height
        self.display_num = display_num
        self.xvfb_process = None
        
    def start(self):
        """Start Xvfb."""
        cmd = [
            'Xvfb',
            f':{self.display_num}',
            '-screen', '0',
            f'{self.width}x{self.height}x24',
            '-ac',  # Disable access control
            '+extension', 'GLX',
            '+render',
            '-noreset'
        ]
        
        self.xvfb_process = subprocess.Popen(cmd)
        time.sleep(1)  # Give Xvfb time to start
        
        # Set DISPLAY environment variable
        os.environ['DISPLAY'] = f':{self.display_num}'
        
        # Register cleanup
        atexit.register(self.stop)
        
    def stop(self):
        """Stop Xvfb."""
        if self.xvfb_process:
            self.xvfb_process.terminate()
            self.xvfb_process.wait()

# Use virtual display for headless operation
vdisplay = VirtualDisplay()
vdisplay.start()

with Browser() as browser:
    # Browser runs with virtual display
    page = browser.new_page()
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
```

## Security Configuration

### SELinux Configuration

```bash
# Check SELinux status
sestatus

# Create custom policy for Chrome
cat > chrome_playwright.te << 'EOF'
module chrome_playwright 1.0;

require {
    type chrome_t;
    type user_home_t;
    type tmp_t;
    class file { read write create unlink };
    class dir { read write add_name remove_name };
}

# Allow Chrome to access user home
allow chrome_t user_home_t:dir { read write add_name remove_name };
allow chrome_t user_home_t:file { read write create unlink };

# Allow Chrome to use /tmp
allow chrome_t tmp_t:dir { read write add_name remove_name };
allow chrome_t tmp_t:file { read write create unlink };
EOF

# Compile and install policy
checkmodule -M -m -o chrome_playwright.mod chrome_playwright.te
semodule_package -o chrome_playwright.pp -m chrome_playwright.mod
sudo semodule -i chrome_playwright.pp
```

### AppArmor Configuration

```bash
# Create AppArmor profile for Chrome
sudo tee /etc/apparmor.d/usr.bin.google-chrome << 'EOF'
#include <tunables/global>

/usr/bin/google-chrome-stable {
  #include <abstractions/base>
  #include <abstractions/nameservice>
  #include <abstractions/user-tmp>
  
  # Chrome binary
  /usr/bin/google-chrome-stable mr,
  /opt/google/chrome/** mr,
  
  # User data
  owner @{HOME}/.local/share/playwrightauthor/** rw,
  owner @{HOME}/.config/google-chrome/** rw,
  
  # Shared memory
  /dev/shm/** rw,
  
  # System access
  /proc/*/stat r,
  /proc/*/status r,
  /sys/devices/system/cpu/** r,
}
EOF

# Load profile
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.google-chrome
```

### Running as Non-Root

```python
import os
import pwd
import grp

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    """Drop root privileges."""
    if os.getuid() != 0:
        # Not running as root
        return
    
    # Get uid/gid from names
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid
    
    # Remove group privileges
    os.setgroups([])
    
    # Set new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)
    
    # Verify
    print(f"Dropped privileges to {uid_name}:{gid_name}")

# Create non-privileged user for Chrome
def setup_chrome_user():
    """Create dedicated user for Chrome."""
    try:
        subprocess.run([
            'sudo', 'useradd',
            '-m',  # Create home directory
            '-s', '/bin/false',  # No shell
            '-c', 'PlaywrightAuthor Chrome User',
            'chrome-automation'
        ], check=True)
    except:
        pass  # User might already exist

# Run Chrome as non-root
if os.getuid() == 0:
    setup_chrome_user()
    drop_privileges('chrome-automation', 'chrome-automation')

with Browser() as browser:
    # Chrome runs as non-root user
    pass
```

## Performance Optimization

### Linux-Specific Chrome Flags

```python
LINUX_CHROME_FLAGS = [
    # Memory optimization
    '--memory-pressure-off',
    '--max_old_space_size=4096',
    '--disable-dev-shm-usage',  # Use /tmp instead of /dev/shm
    
    # GPU optimization
    '--disable-gpu-sandbox',
    '--disable-setuid-sandbox',
    '--no-sandbox',  # Required in Docker
    
    # Performance
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-breakpad',
    '--disable-software-rasterizer',
    
    # Stability
    '--disable-features=RendererCodeIntegrity',
    '--disable-background-timer-throttling',
    
    # Linux specific
    '--no-zygote',  # Don't use zygote process
    '--single-process'  # Run in single process (containers)
]

# Additional flags for containers
if os.path.exists('/.dockerenv'):
    LINUX_CHROME_FLAGS.extend([
        '--disable-gpu',
        '--disable-features=dbus'
    ])

with Browser(args=LINUX_CHROME_FLAGS) as browser:
    # Optimized for Linux
    pass
```

### System Resource Management

```python
import resource

def set_resource_limits():
    """Set resource limits for Chrome processes."""
    # Limit memory usage to 2GB
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 * 1024 * 1024, -1))
    
    # Limit number of open files
    resource.setrlimit(resource.RLIMIT_NOFILE, (4096, 4096))
    
    # Limit CPU time (optional)
    # resource.setrlimit(resource.RLIMIT_CPU, (300, 300))  # 5 minutes

# Apply limits before starting Chrome
set_resource_limits()

# Monitor resource usage
def get_chrome_resources():
    """Get Chrome resource usage."""
    import psutil
    
    total_cpu = 0
    total_memory = 0
    chrome_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        if 'chrome' in proc.info['name'].lower():
            chrome_processes.append({
                'pid': proc.info['pid'],
                'cpu': proc.info['cpu_percent'],
                'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
            })
            total_cpu += proc.info['cpu_percent']
            total_memory += proc.info['memory_info'].rss
    
    return {
        'processes': chrome_processes,
        'total_cpu': total_cpu,
        'total_memory_mb': total_memory / 1024 / 1024
    }
```

## Troubleshooting

### Common Linux Issues

#### Issue 1: Missing Dependencies

```python
def check_chrome_dependencies():
    """Check for missing Chrome dependencies."""
    required_libs = [
        'libnss3.so',
        'libnspr4.so',
        'libatk-1.0.so.0',
        'libatk-bridge-2.0.so.0',
        'libcups.so.2',
        'libdrm.so.2',
        'libxkbcommon.so.0',
        'libxcomposite.so.1',
        'libxdamage.so.1',
        'libxrandr.so.2',
        'libgbm.so.1',
        'libpango-1.0.so.0',
        'libcairo.so.2',
        'libasound.so.2'
    ]
    
    missing = []
    for lib in required_libs:
        try:
            # Try to find library
            result = subprocess.run(
                ['ldconfig', '-p'], 
                capture_output=True, 
                text=True
            )
            if lib not in result.stdout:
                missing.append(lib)
        except:
            pass
    
    if missing:
        print("Missing libraries:")
        for lib in missing:
            print(f"  - {lib}")
        
        # Suggest installation commands
        distro = detect_distribution()
        if distro:
            if distro['id'] in ['ubuntu', 'debian']:
                print("\nInstall with:")
                print("sudo apt-get install libnss3 libnspr4 libatk1.0-0")
            elif distro['id'] in ['fedora', 'centos']:
                print("\nInstall with:")
                print("sudo dnf install nss nspr atk")
    else:
        print("All Chrome dependencies satisfied")

check_chrome_dependencies()
```

#### Issue 2: Chrome Crashes

```bash
# Enable core dumps for debugging
ulimit -c unlimited
echo '/tmp/core_%e_%p' | sudo tee /proc/sys/kernel/core_pattern

# Run Chrome with debugging
export CHROME_LOG_FILE=/tmp/chrome_debug.log
google-chrome --enable-logging --v=1 --dump-without-crashing
```

#### Issue 3: Permission Issues

```python
def fix_chrome_permissions():
    """Fix common permission issues."""
    import stat
    
    # Paths that need proper permissions
    paths_to_fix = [
        os.path.expanduser('~/.local/share/playwrightauthor'),
        '/tmp/playwrightauthor_cache',
        '/dev/shm'
    ]
    
    for path in paths_to_fix:
        if os.path.exists(path):
            try:
                # Ensure directory is writable
                os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
                print(f"Fixed permissions for {path}")
            except Exception as e:
                print(f"Could not fix {path}: {e}")

# Fix before running
fix_chrome_permissions()
```

### Systemd Service

```ini
# /etc/systemd/system/playwrightauthor.service
[Unit]
Description=PlaywrightAuthor Browser Service
After=network.target

[Service]
Type=simple
User=automation
Group=automation
WorkingDirectory=/opt/playwrightauthor
Environment="DISPLAY=:99"
Environment="PLAYWRIGHTAUTHOR_HEADLESS=true"
ExecStartPre=/usr/bin/Xvfb :99 -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
ExecStart=/usr/bin/python3 /opt/playwrightauthor/app.py
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/playwrightauthor/data

[Install]
WantedBy=multi-user.target
```

## Distribution-Specific Tips

### Ubuntu/Debian
- Use `snap` for easy Chrome installation: `sudo snap install chromium`
- Enable proposed repository for latest packages
- Use `unattended-upgrades` for automatic security updates

### Fedora/RHEL
- SELinux is enabled by default - configure policies
- Use `dnf` module streams for different Chrome versions
- Enable RPM Fusion for additional codecs

### Arch Linux
- AUR has latest Chrome builds
- Use `makepkg` flags for optimization
- Enable multilib for 32-bit compatibility

### Alpine Linux
- Minimal footprint ideal for containers
- Use `apk` with `--no-cache` flag
- Add `ttf-freefont` for font support

## Additional Resources

- [Chrome on Linux](https://www.chromium.org/developers/how-tos/get-the-code/chromium-linux)
- [Linux Containers](https://linuxcontainers.org/)
- [X11 Documentation](https://www.x.org/releases/current/doc/)
- [Wayland Protocol](https://wayland.freedesktop.org/)
- [systemd Services](https://www.freedesktop.org/software/systemd/man/systemd.service.html)