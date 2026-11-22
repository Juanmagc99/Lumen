# Proposal

## Why

Starting the development environment currently requires several manual commands and terminals. A consistent entry point will make routine development easier and give future services a predictable place to integrate.

## What Changes

- Add a root Makefile with discoverable setup and development lifecycle commands.
- Start PostgreSQL, apply migrations, and run the API and web development server in the background; provide status and logs.
- Stop and restart managed services safely while retaining database data and avoiding unrelated processes.
- Load local development settings from an ignored `.env` file, with a credential-free `.example.env` template.
- Document prerequisites, local secret handling, usage, failure recovery, and how to extend the tooling.

## Capabilities

### New Capabilities

- `local-development-environment`: Commands for preparing, starting, inspecting, and stopping the local development environment.

### Modified Capabilities

None.

## Impact

The root Makefile, Windows-oriented helper scripts, ignore rules, and README will change. Existing Docker Compose, uv, npm, PostgreSQL, API, and Vite workflows remain the underlying tools. This is local development tooling, not production deployment.
