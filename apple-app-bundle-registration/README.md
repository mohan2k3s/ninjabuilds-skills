# Apple App Bundle Registration — Claude Skill

A reusable [Claude skill](https://docs.claude.com) that walks solo or small-team iOS
developers through registering a new app under an existing Apple Developer Program
account: creating the Bundle ID / App ID, setting up the App Store Connect app record,
and wiring it correctly into Xcode and Firebase.

Built for people building iOS apps with an AI coding assistant (e.g. Claude Code),
especially non-technical or semi-technical solo builders who may be registering
several apps under one Apple Developer account over time.

## What it does

- Confirms app name, Bundle ID, and required capabilities before touching Apple's UI
- Walks through registering the App ID in the Apple Developer Portal
- Walks through creating the matching app record in App Store Connect
- Explains how to wire the Bundle ID into Xcode and Firebase consistently
- Flags common mistakes (Bundle ID typos/mismatches, app name collisions, etc.)
- Suggests keeping a running log of registered apps for multi-app builders

## What it doesn't do

This skill assumes you're **already enrolled** in the Apple Developer Program
(Individual or Organization, $99/year). It does not walk through the enrollment
process itself — only per-app registration after enrollment is complete.

## Installation

1. Download `SKILL.md` from this repo (or the whole folder if you want the structure)
2. In Claude, use the skill upload/install flow, or place the file in your skills
   directory if you're running Claude Code / Claude Desktop with custom skills enabled
3. The skill will trigger automatically when you ask Claude to help register a new
   iOS app, create a Bundle ID, or set up an App Store Connect listing

## Usage example

> "I'm ready to register my second app under my developer account — it's called
> Foo, and my namespace is com.mystudio.*"

Claude will walk you through Bundle ID confirmation, Apple Developer Portal
registration, App Store Connect setup, and Xcode/Firebase wiring — the same
process step by step, for as many apps as you build.

## Contributing

If you hit an edge case this skill doesn't handle well (e.g. Organization-specific
steps, macOS/watchOS targets, additional capabilities), PRs welcome.

## License

MIT — use freely, modify for your own workflow.
