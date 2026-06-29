# Changelog

All notable changes to FreateOJ will be documented in this file.

## [Unreleased]

### Added
- OTP email verification system (8-char code, 60-min expiry)
- Modern SCSS design system with light/dark theme support
- CSS animations (fadeIn, fadeInUp, scaleIn, etc.)
- `EMAIL_VERIFICATION_ENABLED` setting for toggling email verification
- `ResendVerificationView` and `RegistrationCompleteView`
- Professional documentation files (CODE_OF_CONDUCT, SECURITY, CHANGELOG)
- Socket.IO real-time event system
- Room-based event broadcasting for efficiency

### Changed
- Rebranded from VNOJ/VNOI to FreateOJ/Freate
- All URLs updated to freate.io.vn domain
- GitHub org changed from Freate-Admin to freatevietnam
- Facebook link updated to freatevietnam
- Discord invite updated to discord.gg/fC3kG3hQyn
- Default theme set to light mode
- MathJax default inline math delimiter changed to `$`
- Migrated from MariaDB to PostgreSQL
- Demo data dates updated to 2026-06-20
- Documentation migrated to markdown (no external links)

### Fixed
- CSS 404 errors (symlinked resources to static)
- MathJax typesetPromise race condition
- JavaScript null reference errors in submit form
- Jinja2 template syntax for URL tags
- Socket.IO event posting (increased POST body limit to 65KB)
- PostgreSQL compatibility (LOCK TABLE, bitand on booleans)

## [1.0.0] - 2026-06-20

### Added
- Initial FreateOJ release
- Forked from DMOJ online-judge
- PostgreSQL support
- Custom contest formats (FreateOJ points)
- OTP email verification
- Modern frontend design
