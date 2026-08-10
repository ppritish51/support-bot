# SSO & Login

## Do you support single sign-on (SSO)?
Yes. SAML 2.0 SSO is available on Growth and Enterprise plans. An admin configures it in
Settings → Security → SSO by uploading the identity provider metadata (or entering the
SSO URL and certificate). We support Okta, Azure AD/Entra, Google Workspace, and any
SAML-compliant IdP.

## How do I enforce SSO for all members?
After SSO is verified, toggle Settings → Security → SSO → "Require SSO". This disables
password login for your domain so every member must authenticate through your IdP.
Existing API keys keep working — SSO governs human login, not machine access.

## Do you support SCIM user provisioning?
Yes, on Enterprise. SCIM 2.0 lets your IdP automatically create, update, and deactivate
members. When a user is removed in your IdP, SCIM deactivates their access here
automatically, so offboarding is handled in one place.

## Why can't a user log in after we enabled SSO?
Two common causes: the user's email in your IdP doesn't match their email here, or they're
trying the old password login while "Require SSO" is on. Have them use the SSO login URL,
and confirm their IdP email matches their member email exactly.

## How do sessions and 2FA work for password login?
Where SSO isn't enforced, members can enable two-factor authentication (TOTP) in Settings
→ Security. Sessions expire after 14 days of inactivity, and admins can force-log-out all
sessions for a member from the member's admin page.
