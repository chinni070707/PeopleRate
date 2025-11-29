# OAuth Setup Guide for PeopleRate

## Overview
PeopleRate now supports OAuth 2.0 login with 4 providers:
- **Google** (OpenID Connect)
- **LinkedIn** (OAuth 2.0)
- **Facebook** (Graph API)
- **GitHub** (OAuth Apps)

## Benefits of OAuth Login
✅ **One-click signup** - Faster onboarding for users  
✅ **Email verification** - Automatically verified emails  
✅ **LinkedIn badge** - Auto-verified when using LinkedIn OAuth  
✅ **Reputation bonus** - +10 reputation for OAuth signups  
✅ **Better security** - No password management needed

## Setup Instructions

### 1. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Set **Authorized redirect URIs**:
   - Development: `http://localhost:8000/auth/oauth/google/callback`
   - Production: `https://yourapp.com/auth/oauth/google/callback`
7. Copy **Client ID** and **Client Secret**
8. Add to `.env`:
   ```bash
   GOOGLE_CLIENT_ID=your_client_id_here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_client_secret_here
   ```

### 2. LinkedIn OAuth Setup
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create new app
3. Under **Auth** tab, add redirect URLs:
   - Development: `http://localhost:8000/auth/oauth/linkedin/callback`
   - Production: `https://yourapp.com/auth/oauth/linkedin/callback`
4. Request OAuth scopes: `r_liteprofile`, `r_emailaddress`
5. Copy **Client ID** and **Client Secret**
6. Add to `.env`:
   ```bash
   LINKEDIN_CLIENT_ID=your_client_id_here
   LINKEDIN_CLIENT_SECRET=your_client_secret_here
   ```

### 3. Facebook OAuth Setup
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create new app → **Consumer** type
3. Add **Facebook Login** product
4. Under **Settings** → **Basic**, copy App ID and App Secret
5. Under **Facebook Login** → **Settings**, add Valid OAuth Redirect URIs:
   - Development: `http://localhost:8000/auth/oauth/facebook/callback`
   - Production: `https://yourapp.com/auth/oauth/facebook/callback`
6. Add to `.env`:
   ```bash
   FACEBOOK_CLIENT_ID=your_app_id_here
   FACEBOOK_CLIENT_SECRET=your_app_secret_here
   ```

### 4. GitHub OAuth Setup
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - Application name: `PeopleRate`
   - Homepage URL: `https://yourapp.com`
   - Authorization callback URL:
     - Development: `http://localhost:8000/auth/oauth/github/callback`
     - Production: `https://yourapp.com/auth/oauth/github/callback`
4. Copy **Client ID** and **Client Secret**
5. Add to `.env`:
   ```bash
   GITHUB_CLIENT_ID=your_client_id_here
   GITHUB_CLIENT_SECRET=your_client_secret_here
   ```

## Environment Variables (.env)
After setting up OAuth apps, your `.env` should have:

```bash
# MongoDB
MONGODB_URL=mongodb+srv://USERNAME:PASSWORD@CLUSTER_URL/
DATABASE_NAME=peopleRate_db

# JWT Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth Providers (Optional - app works without them)
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Environment
ENVIRONMENT=development  # or production
CORS_ORIGINS=http://localhost:8000,https://yourapp.com
```

## Testing OAuth Flow

### Development Testing
1. Ensure `.env` has at least one OAuth provider configured
2. Start server: `python -m uvicorn main:app --reload`
3. Go to: `http://localhost:8000/auth`
4. Click any OAuth button (Google, LinkedIn, Facebook, GitHub)
5. Authorize the app
6. Get redirected back with automatic login

### What Happens During OAuth
1. User clicks "Continue with Google" (or other provider)
2. Redirected to provider's login page
3. User authorizes PeopleRate app
4. Provider redirects to `/auth/oauth/{provider}/callback`
5. Backend exchanges code for access token
6. Backend fetches user profile from provider
7. Backend creates/updates user account
8. Backend creates OAuth account link
9. User logged in with JWT token
10. Redirected to homepage

## OAuth Account Linking
Users can link multiple OAuth accounts to same PeopleRate account:
- Email matching: If OAuth email matches existing user, accounts are linked
- Manual linking: API endpoint `/api/oauth/linked-accounts` shows linked accounts
- Unlinking: API endpoint `/api/oauth/unlink/{provider}` removes OAuth link

## Security Features
✅ **State parameter** - CSRF protection (handled by authlib)  
✅ **Token validation** - OAuth tokens verified with provider  
✅ **Secure storage** - Tokens stored in database (not exposed to client)  
✅ **Email verification** - OAuth emails trusted as verified  
✅ **HTTPS required** - Production OAuth requires HTTPS  

## API Endpoints

### OAuth Login
- **GET** `/auth/oauth/{provider}` - Initiate OAuth flow (provider: google, linkedin, facebook, github)
- **GET** `/auth/oauth/{provider}/callback` - OAuth callback handler

### OAuth Account Management
- **GET** `/api/oauth/linked-accounts` - List user's linked OAuth accounts (requires auth)
- **DELETE** `/api/oauth/unlink/{provider}` - Unlink OAuth account (requires auth)

## Troubleshooting

### "Provider not configured" error
**Solution:** Add OAuth credentials to `.env` file

### "Redirect URI mismatch" error
**Solution:** Ensure callback URL in provider dashboard matches exactly:
- Development: `http://localhost:8000/auth/oauth/{provider}/callback`
- Production: `https://yourapp.com/auth/oauth/{provider}/callback`

### "Email not provided" error
**Solution:** 
- Google: Ensure `email` scope is included
- LinkedIn: Request `r_emailaddress` permission
- Facebook: Request `email` permission
- GitHub: User must have public email or grant email access

### OAuth button not showing
**Solution:** 
- Check browser console for errors
- Verify OAuth CSS styles loaded
- Ensure auth.html has OAuth buttons section

## Production Checklist
- [ ] All OAuth apps verified (remove "testing" mode)
- [ ] Production callback URLs added to all providers
- [ ] HTTPS enabled for production domain
- [ ] Environment variables set on hosting platform (Render.com)
- [ ] OAuth consent screens configured with privacy policy
- [ ] Terms of Service linked in OAuth consent
- [ ] Scopes minimized (only request what's needed)
- [ ] Test all 4 OAuth providers in production

## Optional: MVP Mode
If you don't want to configure OAuth for MVP testing:
- **App works without OAuth** - Traditional email/password login still available
- OAuth buttons show but give "not configured" error
- No functionality lost - OAuth is enhancement only

## Benefits for Launch
- **Faster signups** - 60% of users prefer OAuth over forms
- **Higher conversion** - One-click login reduces friction
- **Better trust** - LinkedIn verification badge increases credibility
- **Lower support** - No "forgot password" issues for OAuth users
- **Viral potential** - LinkedIn OAuth can auto-suggest connections to review

---

**Status:** ✅ OAuth fully implemented (backend + frontend)  
**Configured:** ⏸️ Pending OAuth app creation (optional for MVP)  
**Ready for:** MVP testing with email/password, production launch with OAuth
