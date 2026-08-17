---
name: apple-app-bundle-registration
description: Guides a solo or small-team iOS developer through registering a new app under an existing Apple Developer Program account — creating the Bundle ID / App ID, setting up the App Store Connect app record, and wiring it into Xcode and Firebase. Use this whenever the user wants to register a new iOS app, create a Bundle ID, set up an App ID with capabilities like Sign in with Apple or Push Notifications, create a new app in App Store Connect, or start a new app under an existing Apple Developer account. Also trigger on phrases like "register my app", "set up a new Bundle ID", "add another app to my developer account", or "create an App Store Connect listing." This skill assumes Apple Developer Program enrollment is already complete — it does not cover the enrollment/signup process itself.
---

# Apple App Bundle Registration

A step-by-step workflow for registering a new iOS app's Bundle ID / App ID in the
Apple Developer Portal, creating the matching app record in App Store Connect, and
wiring the Bundle ID correctly into Xcode and (optionally) Firebase.

This is designed for solo or small-team developers, especially non-technical or
semi-technical builders working with an AI coding assistant (e.g. Claude Code),
who are registering one of potentially several apps under a single Apple Developer
account.

**Prerequisite:** The user must already be enrolled in the Apple Developer Program
(Individual or Organization). If they haven't enrolled yet, direct them to
developer.apple.com to enroll first — this skill starts after that's done.

---

## Step 1: Gather the basics

Before touching the Apple Developer portal, confirm with the user:

1. **App name** — the human-readable name (e.g. "Duefly")
2. **Bundle ID** — reverse-domain format, e.g. `com.[namespace].[appname]`
   - If the user already has a personal or studio namespace from a previous app
     (e.g. `com.ninjabuilds`), reuse it for consistency across their apps.
   - If this is their first app, help them pick a namespace — a personal name,
     handle, or studio brand works well. Keep it short and something they'll want
     to reuse across future apps.
3. **Capabilities needed now** — ask what the app needs, e.g.:
   - Sign in with Apple (needed for most consumer apps with accounts)
   - Push Notifications (needed for real-time features, chat, alerts)
   - iCloud (needed for CloudKit sync)
   - Others can always be added later by editing the App ID, so don't over-ask —
     just cover what's needed for the *current* build phase.

Do not proceed to Step 2 until the Bundle ID is confirmed. Typos here cause
downstream signing errors that are annoying to debug later.

---

## Step 2: Register the App ID (Apple Developer Portal)

Walk the user through these steps. If a step-by-step UI card tool is available,
use it — this workflow benefits from clear numbered steps. Otherwise, present as
a numbered list.

1. Go to developer.apple.com and sign in
2. Account → Certificates, IDs & Profiles → Identifiers
3. Click "+" to register a new identifier
4. Select "App IDs" → Continue → select "App" → Continue
5. Description: enter the app name (human-readable label, not shown publicly)
6. Bundle ID: select "Explicit" (not Wildcard), enter the confirmed Bundle ID
7. Scroll down and check any capabilities identified in Step 1
8. Continue → review the Bundle ID for typos → Register
9. Confirm the app now appears in the Identifiers list

---

## Step 3: Create the App Record (App Store Connect)

1. Go to appstoreconnect.apple.com and sign in
2. Apps → click "+" → New App
3. Platform: iOS (or the relevant platform)
4. Name: the app's public display name — note this must be globally unique
   across the entire App Store, separate from Bundle ID uniqueness. If taken,
   the user will need a variant of the name (not the Bundle ID).
5. Primary language: user's default
6. Bundle ID: select from the dropdown — should show the one just registered
   in Step 2
7. SKU: any unique internal string, not shown publicly (e.g. `[appname]001`)
8. User Access: default unless adding collaborators
9. Click Create

---

## Step 4: Wire it into build tools

- **Xcode**: Project settings → Signing & Capabilities → set Bundle Identifier
  to match exactly.
- **Firebase** (if used): when registering the iOS app in the Firebase console,
  use the same Bundle ID so `GoogleService-Info.plist` is scoped correctly.
- Emphasize to the user: **all of these must match character-for-character**:
  - Apple Developer Portal App ID
  - App Store Connect app record
  - Xcode Bundle Identifier
  - Firebase iOS app registration (if applicable)

Recommend copy-pasting the Bundle ID rather than retyping it at each step to
avoid mismatches — this is the most common source of signing errors.

---

## Common snags to warn users about proactively

- **Bundle ID mismatch** between Xcode and the portal → signing errors. Fix:
  copy-paste, don't retype.
- **App display name already taken** on the App Store — this is independent of
  Bundle ID availability. The user can keep their Bundle ID and pick a different
  public name.
- **Forgot a capability** during App ID registration (e.g. Push Notifications) —
  not a problem, they can go back and edit the App ID later to add it. No need
  to re-register from scratch.
- **Multiple apps, one account** — this is fully supported. The Apple Developer
  Program fee covers the account, not per-app. Just repeat this whole workflow
  with a new Bundle ID for each app, ideally reusing the same namespace.

---

## After registration

Offer to log the newly registered app for the user's own reference, e.g. a table:

| App Name | Bundle ID | Date Registered | Capabilities Enabled |
|---|---|---|---|
| Duefly | com.ninjabuilds.duefly | 2026-08-17 | Sign in with Apple |

If the user is tracking multiple apps, suggest maintaining this table in a
shared notes file or project doc so they have a running record across apps.
