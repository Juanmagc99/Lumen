.PHONY: help setup dev-start dev-stop dev-restart dev-status dev-logs
.DEFAULT_GOAL := help

help:
	@echo Lumen local development commands:
	@echo   make setup        Install locked API and web dependencies
	@echo   make dev-start    Start database, API, worker and web in the background
	@echo   make dev-stop     Stop managed services, retaining database data
	@echo   make dev-restart  Restart managed services
	@echo   make dev-status   Show service status
	@echo   make dev-logs     Show recent service logs
	@echo Requirements: Windows PowerShell 5.1, GNU Make, uv, Python 3.13, Node.js 24 and Docker Compose.

setup dev-start dev-stop dev-restart dev-status dev-logs:
	@powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File scripts/dev.ps1 $@
