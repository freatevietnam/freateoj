# FreateOJ: Freate Online Judge

[![Build Status](https://github.com/freatevietnam/freateoj/workflows/build/badge.svg)](https://github.com/freatevietnam/freateoj/actions/)
[![AGPL License](https://img.shields.io/badge/license-AGPLv3.0-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)
[![Discord link](https://img.shields.io/discord/1517871991573581975?color=%237289DA&label=Discord&logo=Discord)](https://discord.com/invite/fC3kG3hQyn)

FreateOJ is an online judge serving as the official judge for Freate programming contests.

## Features

- Support for **56+ programming languages** (C, C++, Java, Python, and more)
- **MathJax 3.2.0** for rendering LaTeX math with `$` and `$$` delimiters
- **Contest formats**: IOI-style, ICPC-style, and custom formats
- **Real-time updates** via Socket.IO
- **Batch rejudging** and problem versioning
- **Dark/Light theme** support
- **Docker-based judge** for secure code execution

## Math Syntax

FreateOJ uses `$` as the default inline math delimiter and `$$` for display math.

```markdown
Inline: $x^2 + y^2 = z^2$
Display: $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
```

See the full [Math Syntax Guide](docs/MATH_SYNTAX.md) for details.

## Installation

Refer to the [installation documentation](docs/docs/site/installation.md).

- Define `FREATEOJ_PROBLEM_DATA_ROOT` in `local_settings.py` (path to problems' tests directory)
- Use `memcached` or `redis` for caching instead of default local-memory caching

### Demo Data

```bash
python manage.py loaddata demo
```

This creates a superuser account with username `admin` and password `admin`.

## Contributing

See [contributing.md](contributing.md) for guidelines.

## Security

Report security vulnerabilities to **freatevietnam@gmail.com**. See [SECURITY.md](SECURITY.md) for details.

## Credits

Ideas and inspiration for FreateOJ are taken from:

- [VNOJ - Viet Nam Online Judge](https://github.com/VNOI-Admin/OJ)
- [OREOJ - ORE Online Judge](https://ojkhanhhoa.site/)

## License

FreateOJ is licensed under the [GNU Affero General Public License v3.0](LICENSE).
