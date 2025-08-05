# Authentication

PlaywrightAuthor provides seamless authentication handling through persistent browser profiles and guided onboarding workflows. This eliminates the need to re-authenticate for every automation session.

## How Authentication Works

PlaywrightAuthor uses persistent Chrome user profiles to maintain login sessions:

1. **Profile Persistence**: Login data is stored in a Chrome user profile
2. **Session Reuse**: Subsequent automation runs use the existing authenticated session
3. **Guided Onboarding**: Interactive guidance for initial authentication setup
4. **Cross-Site Support**: Works with any website that supports persistent cookies

## Basic Authentication Setup

### First-Time Setup

```python
from playwrightauthor import Browser

# First run - will guide you through authentication
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    
    # PlaywrightAuthor will detect if you're not logged in
    # and provide guidance for authentication
```

### Automatic Authentication Detection

PlaywrightAuthor can detect authentication status:

```python
from playwrightauthor import Browser
from playwrightauthor.auth import is_authenticated

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    
    # Check if authenticated
    if is_authenticated(page, site="github"):
        print("Already logged in!")
    else:
        print("Authentication required")
        # Trigger onboarding flow
```

## Onboarding Workflow

### Interactive Onboarding

When authentication is needed, PlaywrightAuthor provides guided assistance:

```python
from playwrightauthor import Browser
from playwrightauthor.onboarding import OnboardingManager

with Browser() as browser:
    onboarding = OnboardingManager(browser)
    
    # Start guided onboarding for GitHub
    success = onboarding.guide_authentication(
        site="github",
        target_url="https://github.com/settings/profile"
    )
    
    if success:
        print("Authentication completed successfully!")
```

### Onboarding HTML Template

PlaywrightAuthor serves a local HTML page for guidance:

```html
<!-- Served at http://localhost:8080/onboarding -->
<!DOCTYPE html>
<html>
<head>
    <title>PlaywrightAuthor - Authentication Setup</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .step { margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }
        .success { border-color: #28a745; background: #f8fff9; }
        .warning { border-color: #ffc107; background: #fffbf0; }
    </style>
</head>
<body>
    <h1>Authentication Setup Guide</h1>
    <div class="step">
        <h3>Step 1: Login to your account</h3>
        <p>A browser window will open. Please log into your account normally.</p>
    </div>
    <div class="step">
        <h3>Step 2: Verify access</h3>
        <p>Navigate to a protected page to confirm your login worked.</p>
    </div>
    <div class="step success">
        <h3>Step 3: Complete setup</h3>
        <p>Your session will be saved for future automation runs!</p>
    </div>
</body>
</html>
```

## Site-Specific Authentication

### GitHub Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth.github import GitHubAuth

with Browser() as browser:
    github_auth = GitHubAuth(browser)
    
    # Check authentication status
    if not github_auth.is_authenticated():
        # Guide through GitHub login
        github_auth.authenticate()
    
    # Now access protected GitHub features
    page = browser.new_page()
    page.goto("https://github.com/settings/profile")
    
    # Automation with authenticated session
    name = page.input_value("#user_profile_name")
    print(f"GitHub username: {name}")
```

### Gmail Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth.gmail import GmailAuth

with Browser() as browser:
    gmail_auth = GmailAuth(browser)
    
    # Authenticate with Gmail
    if not gmail_auth.is_authenticated():
        gmail_auth.authenticate()
    
    # Access Gmail
    page = browser.new_page()
    page.goto("https://mail.google.com")
    
    # Work with authenticated Gmail session
    page.wait_for_selector("[data-tooltip='Compose']")
    page.click("[data-tooltip='Compose']")
```

### LinkedIn Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth.linkedin import LinkedInAuth

with Browser() as browser:
    linkedin_auth = LinkedInAuth(browser)
    
    # Handle LinkedIn authentication
    if not linkedin_auth.is_authenticated():
        linkedin_auth.authenticate()
    
    # Navigate to LinkedIn features
    page = browser.new_page()
    page.goto("https://www.linkedin.com/feed/")
    
    # Perform LinkedIn automation
    page.wait_for_selector("[data-test-id='feed-tab']")
```

## Custom Authentication Patterns

### Custom Site Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth import BaseAuth

class CustomSiteAuth(BaseAuth):
    def __init__(self, browser, site_url: str):
        super().__init__(browser)
        self.site_url = site_url
    
    def is_authenticated(self) -> bool:
        """Check if user is logged in"""
        page = self.browser.new_page()
        page.goto(self.site_url)
        
        # Look for login indicators
        login_button = page.query_selector("text=Login")
        user_menu = page.query_selector("[data-testid='user-menu']")
        
        page.close()
        return user_menu is not None and login_button is None
    
    def authenticate(self) -> bool:
        """Guide user through authentication"""
        if self.is_authenticated():
            return True
        
        # Open login page
        page = self.browser.new_page()
        page.goto(f"{self.site_url}/login")
        
        # Wait for user to complete login
        self._wait_for_authentication(page)
        
        return self.is_authenticated()
    
    def _wait_for_authentication(self, page):
        """Wait for user to complete login process"""
        print("Please complete login in the browser window...")
        
        # Wait for successful login indicators
        try:
            page.wait_for_selector("[data-testid='user-menu']", timeout=300000)  # 5 minutes
            print("Authentication successful!")
        except TimeoutError:
            print("Authentication timeout - please try again")

# Usage
with Browser() as browser:
    auth = CustomSiteAuth(browser, "https://example.com")
    auth.authenticate()
```

### Multi-Factor Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth import MFAHandler

class MFAAuth:
    def __init__(self, browser):
        self.browser = browser
        self.mfa_handler = MFAHandler()
    
    def handle_mfa_flow(self, page):
        """Handle various MFA methods"""
        # Check for MFA prompt
        if page.query_selector("text=Enter verification code"):
            return self._handle_code_verification(page)
        elif page.query_selector("text=Use your authenticator app"):
            return self._handle_app_verification(page)
        elif page.query_selector("text=Check your phone"):
            return self._handle_sms_verification(page)
        
        return True
    
    def _handle_code_verification(self, page):
        """Handle manual code entry"""
        print("Please enter the verification code in the browser")
        
        # Wait for code to be entered
        page.wait_for_function(
            "document.querySelector('[name=verification_code]').value.length >= 6"
        )
        
        # Submit form
        page.click("button[type=submit]")
        return True
    
    def _handle_app_verification(self, page):
        """Handle authenticator app verification"""
        print("Please use your authenticator app and enter the code")
        
        # Wait for successful verification
        page.wait_for_url("**/dashboard", timeout=120000)
        return True

# Usage with MFA
with Browser() as browser:
    mfa_auth = MFAAuth(browser)
    
    page = browser.new_page()
    page.goto("https://secure-site.com/login")
    
    # Fill login form
    page.fill("#username", "your_username")
    page.fill("#password", "your_password")
    page.click("#login-button")
    
    # Handle MFA if required
    mfa_auth.handle_mfa_flow(page)
```

## Profile Management for Authentication

### Named Authentication Profiles

```python
from playwrightauthor import Browser, BrowserConfig
from pathlib import Path

def create_auth_profile(profile_name: str):
    """Create a named profile for specific authentication"""
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    return BrowserConfig(user_data_dir=str(profile_dir))

# Use different profiles for different accounts
github_config = create_auth_profile("github_work")
gmail_config = create_auth_profile("gmail_personal")

# Work account automation
with Browser(config=github_config) as browser:
    page = browser.new_page()
    page.goto("https://github.com/settings")

# Personal account automation  
with Browser(config=gmail_config) as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
```

### Profile Switching

```python
from playwrightauthor.auth import ProfileManager

profile_manager = ProfileManager()

# Switch between profiles
profiles = {
    "work": "/path/to/work/profile",
    "personal": "/path/to/personal/profile",
    "testing": "/path/to/test/profile"
}

for name, path in profiles.items():
    config = BrowserConfig(user_data_dir=path)
    
    with Browser(config=config) as browser:
        print(f"Using {name} profile")
        page = browser.new_page()
        page.goto("https://github.com")
        
        # Check which account is logged in
        if page.query_selector("[data-testid='header-user-menu']"):
            user = page.text_content("[data-testid='header-user-menu'] img")
            print(f"Logged in as: {user}")
```

## Session Validation and Refresh

### Session Health Checks

```python
from playwrightauthor.auth import SessionValidator

class SessionValidator:
    def __init__(self, browser):
        self.browser = browser
    
    def validate_session(self, site: str) -> bool:
        """Validate that session is still active"""
        validators = {
            "github": self._validate_github_session,
            "gmail": self._validate_gmail_session,
            "linkedin": self._validate_linkedin_session,
        }
        
        validator = validators.get(site)
        if validator:
            return validator()
        
        return False
    
    def _validate_github_session(self) -> bool:
        """Check GitHub session validity"""
        page = self.browser.new_page()
        page.goto("https://api.github.com/user")
        
        # Check for valid API response
        is_valid = "login" in page.text_content("body")
        page.close()
        
        return is_valid
    
    def refresh_session_if_needed(self, site: str):
        """Refresh session if validation fails"""
        if not self.validate_session(site):
            print(f"Session expired for {site}, re-authenticating...")
            # Trigger re-authentication flow
            auth_handlers = {
                "github": GitHubAuth,
                "gmail": GmailAuth,
                "linkedin": LinkedInAuth,
            }
            
            auth_class = auth_handlers.get(site)
            if auth_class:
                auth = auth_class(self.browser)
                auth.authenticate()

# Usage
with Browser() as browser:
    validator = SessionValidator(browser)
    
    # Validate before automation
    validator.refresh_session_if_needed("github")
    
    # Proceed with automation
    page = browser.new_page()
    page.goto("https://github.com/settings")
```

## Security Best Practices

### Secure Profile Storage

```python
import os
from pathlib import Path
from playwrightauthor import BrowserConfig

def create_secure_profile(profile_name: str):
    """Create profile with secure permissions"""
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    # Set secure permissions (owner read/write only)
    os.chmod(profile_dir, 0o700)
    
    return BrowserConfig(user_data_dir=str(profile_dir))
```

### Environment-Based Configuration

```python
import os
from playwrightauthor import Browser, BrowserConfig

def get_auth_config():
    """Get authentication config from environment"""
    # Don't hardcode sensitive paths
    profile_path = os.getenv("PLAYWRIGHT_PROFILE_PATH")
    if not profile_path:
        raise ValueError("PLAYWRIGHT_PROFILE_PATH environment variable required")
    
    return BrowserConfig(user_data_dir=profile_path)

# Usage
config = get_auth_config()
with Browser(config=config) as browser:
    # Authenticated automation
    pass
```

### Credential Management

```python
from playwrightauthor.auth import CredentialManager

class CredentialManager:
    def __init__(self):
        self.credentials = {}
    
    def store_credential(self, site: str, username: str, encrypted_token: str):
        """Store encrypted credentials securely"""
        self.credentials[site] = {
            "username": username,
            "token": encrypted_token,
            "expires_at": None
        }
    
    def get_credential(self, site: str):
        """Retrieve and decrypt credentials"""
        return self.credentials.get(site)
    
    def is_credential_valid(self, site: str) -> bool:
        """Check if stored credential is still valid"""
        cred = self.get_credential(site)
        if not cred:
            return False
        
        # Check expiration
        if cred.get("expires_at"):
            from datetime import datetime
            return datetime.now() < cred["expires_at"]
        
        return True
```

## Troubleshooting Authentication

### Common Authentication Issues

1. **Session Expired**:
```python
# Detect and handle expired sessions
try:
    page.goto("https://secure-site.com/protected")
    if "login" in page.url:
        # Session expired, re-authenticate
        auth.authenticate()
        page.goto("https://secure-site.com/protected")
except Exception as e:
    print(f"Authentication error: {e}")
```

2. **Profile Corruption**:
```python
from playwrightauthor.auth import ProfileRepair

repair = ProfileRepair()
if repair.is_profile_corrupted(profile_path):
    repair.backup_profile(profile_path)
    repair.create_fresh_profile(profile_path)
```

3. **Cookie Issues**:
```python
# Clear specific site cookies
page.context.clear_cookies(url="https://problematic-site.com")

# Or clear all cookies
page.context.clear_cookies()
```

## Next Steps

- Explore [Advanced Features](advanced-features.md) for complex authentication scenarios
- Check [Troubleshooting](troubleshooting.md) for authentication-specific issues
- Review [API Reference](api-reference.md) for authentication method details
- Learn about [Browser Management](browser-management.md) for profile handling