# Changelog

## [v1.0.1] - 2026-02-02

### Fixed
- Resolved intermittent bot stops by migrating to `httpx` for asynchronous HTTP requests.
- Enhanced logging for better troubleshooting of API interactions.

## [v1.0.0] - 2026-01-31

### Added
- Initial release of ShigureCafeBot.
- Implemented Telegram bot using `python-telegram-bot` framework.
- Support for `/start` command with usage instructions.
- Support for `/chatid` command to retrieve Telegram Chat ID for configuration.
- Support for `/audit <audit_code>` command to verify registrations and generate invite links.
- Integration with ShigureCafeBackend API for registration verification.
- Dynamic generation of temporary (10 minutes) and single-use Telegram group invite links.
- Docker and Docker Compose configuration for containerized deployment.
- Environment variable support for flexible configuration.
