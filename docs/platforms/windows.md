# Windows Platform Guide

This guide covers Windows-specific setup, configuration, and troubleshooting for PlaywrightAuthor.

## Quick Start

```powershell
# Install PlaywrightAuthor
pip install playwrightauthor

# First run - may prompt for UAC elevation
python -c "from playwrightauthor import Browser; Browser().__enter__()"
```

## Security & Permissions

### User Account Control (UAC)

PlaywrightAuthor may require elevated permissions for:
- Installing Chrome for Testing
- Accessing protected directories
- Modifying system settings

#### Running with Elevation

```python
import ctypes
import sys
import os

def is_admin():
    """Check if running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the current script with admin privileges."""
    if is_admin():
        return True
    else:
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        return False

# Use in your script
if not is_admin():
    print("Requesting administrator privileges...")
    if run_as_admin():
        sys.exit(0)

# Your PlaywrightAuthor code here
from playwrightauthor import Browser
with Browser() as browser:
    # Elevated browser session
    pass
```

### Windows Defender & Antivirus

#### Adding Exclusions

```powershell
# PowerShell (Run as Administrator)

# Add PlaywrightAuthor data directory to exclusions
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\playwrightauthor"

# Add Chrome for Testing to exclusions
Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\ms-playwright"

# Add Python scripts directory
Add-MpPreference -ExclusionPath "$env:USERPROFILE\AppData\Local\Programs\Python"

# Add specific process exclusions
Add-MpPreference -ExclusionProcess "chrome.exe"
Add-MpPreference -ExclusionProcess "python.exe"
```

#### Programmatic Exclusion Management

```python
import subprocess
import os

def add_defender_exclusion(path: str):
    """Add path to Windows Defender exclusions."""
    try:
        cmd = [
            'powershell', '-ExecutionPolicy', 'Bypass',
            '-Command', f'Add-MpPreference -ExclusionPath "{path}"'
        ]
        
        # Run with elevation
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            print(f"Added {path} to Windows Defender exclusions")
        else:
            print(f"Failed to add exclusion: {result.stderr}")
            
    except Exception as e:
        print(f"Error adding exclusion: {e}")

# Add PlaywrightAuthor directories
playwrightauthor_dir = os.path.join(os.environ['LOCALAPPDATA'], 'playwrightauthor')
add_defender_exclusion(playwrightauthor_dir)
```

### PowerShell Execution Policies

#### Setting Execution Policy

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single session
powershell -ExecutionPolicy Bypass -File script.ps1
```

#### Python Integration

```python
import subprocess

def run_powershell_script(script: str, bypass_policy: bool = True):
    """Run PowerShell script with optional policy bypass."""
    cmd = ['powershell']
    
    if bypass_policy:
        cmd.extend(['-ExecutionPolicy', 'Bypass'])
    
    cmd.extend(['-Command', script])
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True
    )
    
    return result.stdout, result.stderr

# Example: Check Chrome installation
script = '''
    $chrome = Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | 
              Where-Object { $_.DisplayName -like "*Google Chrome*" }
    if ($chrome) {
        Write-Output "Chrome installed at: $($chrome.InstallLocation)"
    } else {
        Write-Output "Chrome not found in registry"
    }
'''

output, error = run_powershell_script(script)
print(output)
```

## Windows-Specific Paths

### Chrome Installation Locations

```python
import os
import winreg

def find_chrome_windows():
    """Find Chrome installation on Windows."""
    potential_paths = [
        # 64-bit Chrome on 64-bit Windows
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        
        # User-specific installation
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        
        # Chrome for Testing
        os.path.expandvars(r"%LOCALAPPDATA%\ms-playwright\chromium-*\chrome-win\chrome.exe"),
        
        # Chocolatey installation
        r"C:\ProgramData\chocolatey\bin\chrome.exe",
        
        # Scoop installation  
        os.path.expandvars(r"%USERPROFILE%\scoop\apps\googlechrome\current\chrome.exe")
    ]
    
    # Check registry for Chrome location
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe") as key:
            chrome_path = winreg.QueryValue(key, None)
            if os.path.exists(chrome_path):
                return chrome_path
    except:
        pass
    
    # Check standard paths
    for path in potential_paths:
        expanded = os.path.expandvars(path)
        if os.path.exists(expanded):
            return expanded
        
        # Handle wildcards
        if '*' in expanded:
            import glob
            matches = glob.glob(expanded)
            if matches:
                return matches[0]
    
    return None
```

### Profile Storage

```python
def get_windows_profile_paths():
    """Get Windows-specific profile paths."""
    return {
        'playwrightauthor_data': os.path.expandvars(r'%LOCALAPPDATA%\playwrightauthor'),
        'playwrightauthor_cache': os.path.expandvars(r'%LOCALAPPDATA%\playwrightauthor\Cache'),
        'chrome_user_data': os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data'),
        'temp_profiles': os.path.expandvars(r'%TEMP%\playwrightauthor_profiles')
    }

# Create profile directory with proper permissions
import win32security
import win32api

def create_secure_directory(path: str):
    """Create directory with restricted permissions."""
    os.makedirs(path, exist_ok=True)
    
    # Get current user SID
    username = win32api.GetUserName()
    domain = win32api.GetDomainName()
    
    # Set permissions to current user only
    sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
    dacl = win32security.ACL()
    
    # Add permission for current user
    user_sid = win32security.LookupAccountName(domain, username)[0]
    dacl.AddAccessAllowedAce(
        win32security.ACL_REVISION,
        win32security.FILE_ALL_ACCESS,
        user_sid
    )
    
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)
```

## Display & DPI Handling

### High DPI Support

```python
import ctypes

def enable_dpi_awareness():
    """Enable DPI awareness for high-resolution displays."""
    try:
        # Windows 10 version 1703+
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except:
        try:
            # Windows 8.1+
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
        except:
            # Windows Vista+
            ctypes.windll.user32.SetProcessDPIAware()

# Enable before creating browser
enable_dpi_awareness()

from playwrightauthor import Browser

# Get current DPI scale
def get_dpi_scale():
    """Get current DPI scaling factor."""
    hdc = ctypes.windll.user32.GetDC(0)
    dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return dpi / 96.0  # 96 is standard DPI

scale_factor = get_dpi_scale()

with Browser(device_scale_factor=scale_factor) as browser:
    # Browser with proper DPI scaling
    pass
```

### Multi-Monitor Setup

```python
import win32api
import win32con

def get_monitor_info():
    """Get information about all monitors."""
    monitors = []
    
    def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        info = win32api.GetMonitorInfo(hMonitor)
        monitors.append({
            'name': info['Device'],
            'work_area': info['Work'],
            'monitor_area': info['Monitor'],
            'is_primary': info['Flags'] & win32con.MONITORINFOF_PRIMARY
        })
        return True
    
    win32api.EnumDisplayMonitors(None, None, monitor_enum_proc, 0)
    return monitors

# Position browser on specific monitor
monitors = get_monitor_info()
if len(monitors) > 1:
    # Use second monitor
    second_monitor = monitors[1]
    x = second_monitor['work_area'][0]
    y = second_monitor['work_area'][1]
    
    with Browser(args=[f'--window-position={x},{y}']) as browser:
        # Browser opens on second monitor
        pass
```

## Performance Optimization

### Windows-Specific Chrome Flags

```python
WINDOWS_CHROME_FLAGS = [
    # GPU acceleration
    '--enable-gpu-rasterization',
    '--enable-features=VaapiVideoDecoder',
    '--ignore-gpu-blocklist',
    
    # Memory management
    '--max_old_space_size=4096',
    '--disable-background-timer-throttling',
    
    # Windows-specific
    '--disable-features=RendererCodeIntegrity',
    '--no-sandbox',  # May be needed on some Windows configs
    
    # Network
    '--disable-features=NetworkService',
    '--disable-web-security',  # For local file access
    
    # Performance
    '--disable-logging',
    '--disable-gpu-sandbox',
    '--disable-software-rasterizer'
]

with Browser(args=WINDOWS_CHROME_FLAGS) as browser:
    # Optimized for Windows
    pass
```

### Process Priority Management

```python
import psutil
import win32api
import win32process
import win32con

def set_chrome_priority(priority_class=win32process.NORMAL_PRIORITY_CLASS):
    """Set Chrome process priority."""
    for proc in psutil.process_iter(['pid', 'name']):
        if 'chrome' in proc.info['name'].lower():
            try:
                handle = win32api.OpenProcess(
                    win32con.PROCESS_ALL_ACCESS, 
                    True, 
                    proc.info['pid']
                )
                win32process.SetPriorityClass(handle, priority_class)
                win32api.CloseHandle(handle)
            except:
                pass

# Set Chrome to high priority
set_chrome_priority(win32process.HIGH_PRIORITY_CLASS)
```

## Troubleshooting

### Common Windows Issues

#### Issue 1: Chrome Won't Launch

```python
def diagnose_chrome_windows():
    """Diagnose Chrome issues on Windows."""
    import subprocess
    
    diagnostics = []
    
    # Check if Chrome is installed
    chrome_path = find_chrome_windows()
    diagnostics.append({
        'check': 'Chrome installed',
        'passed': chrome_path is not None,
        'details': chrome_path or 'Not found'
    })
    
    # Check Windows Defender
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-MpPreference | Select-Object ExclusionPath'],
            capture_output=True,
            text=True
        )
        has_exclusion = 'playwrightauthor' in result.stdout
        diagnostics.append({
            'check': 'Windows Defender exclusion',
            'passed': has_exclusion,
            'details': 'Excluded' if has_exclusion else 'Not excluded'
        })
    except:
        pass
    
    # Check if port 9222 is available
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9222))
        sock.close()
        port_available = result != 0
        diagnostics.append({
            'check': 'Debug port available',
            'passed': port_available,
            'details': 'Available' if port_available else 'In use'
        })
    except:
        pass
    
    # Check UAC level
    try:
        result = subprocess.run(
            ['reg', 'query', r'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System',
             '/v', 'ConsentPromptBehaviorAdmin'],
            capture_output=True,
            text=True
        )
        uac_level = 'Unknown'
        if '0x0' in result.stdout:
            uac_level = 'Never notify'
        elif '0x5' in result.stdout:
            uac_level = 'Always notify'
        
        diagnostics.append({
            'check': 'UAC level',
            'passed': True,
            'details': uac_level
        })
    except:
        pass
    
    # Print results
    print("Chrome Diagnostics for Windows:")
    print("-" * 50)
    for diag in diagnostics:
        status = "PASS" if diag['passed'] else "FAIL"
        print(f"{status} {diag['check']}: {diag['details']}")
    
    return all(d['passed'] for d in diagnostics)

# Run diagnostics
diagnose_chrome_windows()
```

#### Issue 2: Permission Denied Errors

```python
import tempfile
import shutil

def fix_permission_issues():
    """Fix common permission issues on Windows."""
    
    # Option 1: Use temp directory
    temp_profile = os.path.join(tempfile.gettempdir(), 'playwrightauthor_temp')
    os.makedirs(temp_profile, exist_ok=True)
    
    # Option 2: Take ownership of directory
    def take_ownership(path):
        """Take ownership of a directory."""
        try:
            subprocess.run([
                'takeown', '/f', path, '/r', '/d', 'y'
            ], capture_output=True)
            
            subprocess.run([
                'icacls', path, '/grant', f'{os.environ["USERNAME"]}:F', '/t'
            ], capture_output=True)
            
            print(f"Took ownership of {path}")
        except Exception as e:
            print(f"Failed to take ownership: {e}")
    
    # Apply to PlaywrightAuthor directory
    pa_dir = os.path.join(os.environ['LOCALAPPDATA'], 'playwrightauthor')
    if os.path.exists(pa_dir):
        take_ownership(pa_dir)
```

#### Issue 3: Corporate Proxy Issues

```python
def setup_corporate_proxy():
    """Configure Chrome for corporate proxy."""
    import urllib.request
    
    # Get system proxy
    proxy = urllib.request.getproxies()
    
    proxy_args = []
    if 'http' in proxy:
        proxy_args.append(f'--proxy-server={proxy["http"]}')
    
    # Bypass proxy for local addresses
    proxy_args.append('--proxy-bypass-list=localhost,127.0.0.1,*.local')
    
    # Use with Browser
    with Browser(args=proxy_args) as browser:
        # Browser with proxy configuration
        pass
```

### Windows Services Integration

#### Running as Windows Service

```python
import win32serviceutil
import win32service
import win32event
import servicemanager

class PlaywrightAuthorService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'PlaywrightAuthorService'
    _svc_display_name_ = 'PlaywrightAuthor Browser Service'
    _svc_description_ = 'Manages Chrome browser for automation'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.browser = None
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        
        # Start browser
        from playwrightauthor import Browser
        self.browser = Browser().__enter__()
        
        # Wait for stop signal
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
        # Cleanup
        if self.browser:
            self.browser.__exit__(None, None, None)

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PlaywrightAuthorService)
```

## Security Best Practices

### Windows Credential Manager

```python
import win32cred

def save_credential(target: str, username: str, password: str):
    """Save credential to Windows Credential Manager."""
    credential = {
        'Type': win32cred.CRED_TYPE_GENERIC,
        'TargetName': target,
        'UserName': username,
        'CredentialBlob': password.encode('utf-16-le'),
        'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE,
        'Attributes': [],
        'Comment': 'Stored by PlaywrightAuthor'
    }
    
    win32cred.CredWrite(credential)
    print(f"Credential saved for {target}")

def get_credential(target: str):
    """Retrieve credential from Windows Credential Manager."""
    try:
        cred = win32cred.CredRead(target, win32cred.CRED_TYPE_GENERIC)
        username = cred['UserName']
        password = cred['CredentialBlob'].decode('utf-16-le')
        return username, password
    except:
        return None, None

# Example usage
save_credential('github.com', 'username', 'token')
username, password = get_credential('github.com')
```

### AppLocker Considerations

```powershell
# Check AppLocker policies
Get-AppLockerPolicy -Effective | Format-List

# Add Chrome to allowed applications
$rule = New-AppLockerPolicy -RuleType Exe -AllowRule -UserOrGroupSid S-1-1-0 `
    -Condition (New-AppLockerCondition -Path "%PROGRAMFILES%\Google\Chrome\Application\chrome.exe")
    
Set-AppLockerPolicy -PolicyObject $rule
```

## Additional Resources

- [Chrome Enterprise on Windows](https://support.google.com/chrome/a/answer/7587273)
- [Windows Security Baselines](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-security-baselines)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Windows Service Development](https://docs.microsoft.com/en-us/windows/win32/services/services)