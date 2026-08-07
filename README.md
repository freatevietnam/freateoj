# FreateOJ: Freate Online Judge

<p align="center">
  <img src="https://raw.githubusercontent.com/freatevietnam/freateoj/main/resources/icons/logo.png" alt="FreateOJ Logo" width="120" />
</p>

<p align="center">
  <b>A modern, high-performance, and scalable Online Judge platform for competitive programming and contest hosting.</b>
</p>

<p align="center">
  <a href="https://github.com/freatevietnam/freateoj/actions"><img src="https://github.com/freatevietnam/freateoj/workflows/build/badge.svg" alt="Build Status" /></a>
  <a href="http://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/license-AGPLv3.0-blue.svg" alt="AGPL License" /></a>
  <a href="https://discord.gg/fC3kG3hQyn"><img src="https://img.shields.io/discord/1517871991573581975?color=%237289DA&label=Discord&logo=Discord" alt="Discord" /></a>
  <a href="https://freatevietnam.github.io/freateoj-docs/"><img src="https://img.shields.io/badge/docs-freateoj--docs-brightgreen" alt="Documentation" /></a>
</p>

---

## 📖 Overview

**FreateOJ** is an advanced open-source Online Judge platform designed for hosting algorithmic programming contests, educational coding assessments, and automated code evaluation. Built on Django and modern web technologies, FreateOJ powers competitive programming communities with real-time scoreboards, high-throughput sandboxed judging, and rich interactive discussion features.

---

## ✨ Key Features

- ⚡ **Multi-Language Support**: Support for over **56 programming languages** (C, C++, Python, Java, Rust, Go, Pascal, Kotlin, Swift, and more).
- 🏆 **Versatile Contest Formats**:
  - **IOI / Partial Scoring**: Subtask-based scoring with partial credit.
  - **ICPC / Penalty-based**: Time penalty scoring with instant freeze & unfreeze options.
  - **Custom Rules**: Support for custom scoring plugins and rating systems.
- 👻 **Contest Replay & Ghost Merging**:
  - Integrated `merge_replay_data` management tool to import historical contest runs as ghost participants.
  - Separate Official vs. Ghost ranking view toggles.
- 💬 **Lazy-Loaded & Paginated Discussions**:
  - High-performance threaded comments with deferred AJAX loading and Digg-style pagination.
  - Live preview editor (Martor) with full Markdown and LaTeX math support.
- 📐 **MathJax 3.2 Integration**: Native LaTeX math rendering with standard `$` (inline) and `$$` (display) delimiters.
- 🔄 **Real-Time Updates**: Live submission status stream, judge connection health, and leaderboard updates via WebSockets.
- 🛡️ **Secure Sandboxed Judging**: Isolated execution using Linux cgroups and Docker containers for secure resource restriction (memory, CPU, syscall filtering).
- 🎨 **Modern Responsive UI**: SCSS-driven styling with dark/light themes, clean statistics, and accessible navigation.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.11+ / Django 4.2+ |
| **Asynchronous Tasks** | Celery, Redis |
| **Database** | MySQL / MariaDB / PostgreSQL |
| **Frontend & Styling** | Vanilla JavaScript, jQuery, SCSS/Sass, Ace Editor, Martor |
| **Math & Rendering** | MathJax 3.2.0 |
| **Judge Engine** | Bridged Protocol, Cgroups Sandbox, Docker |
| **Process Manager** | Supervisor / Systemd |

---

## 🚀 Quick Start & Installation

### Prerequisites

Ensure your host environment meets the following requirements:
- **Python**: 3.11+
- **Node.js**: 18+ & `npm` / `npx`
- **Database**: MySQL / MariaDB 10.5+ or PostgreSQL 14+
- **Cache**: Redis / Memcached
- **System**: Linux (Ubuntu 20.04/22.04 LTS recommended)

### 1. Repository Setup

```bash
# Clone the repository
git clone https://github.com/freatevietnam/freateoj.git
cd freateoj

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (`local_settings.py`)

Create `dmoj/local_settings.py` based on `dmoj/local_settings.py.template`:

```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'freateoj',
        'USER': 'freateoj',
        'PASSWORD': 'your_secure_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# Key Directories
FREATEOJ_PROBLEM_DATA_ROOT = '/var/dmoj/problems'
FREATEOJ_CONTEST_REPLAY_MEDIA_DIR = '/var/dmoj/replays'

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 3. Database Migration & Asset Compilation

```bash
# Run Django database migrations
python manage.py migrate

# Compile SCSS assets
npx sass resources/style.scss resources/style.css

# Collect static files
python manage.py collectstatic --no-input
```

### 4. Load Demo Data (Optional)

```bash
python manage.py loaddata demo
```
> **Default Admin Account**: Username: `admin` | Password: `admin`

### 5. Running local development server

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🧮 Math Syntax Guide

FreateOJ supports inline and display math syntax rendered via **MathJax 3.2.0**:

- **Inline Math**: Enclose expression in single dollar signs `$ ... $` or `\( ... \)`
  ```markdown
  The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.
  ```
- **Display Math**: Enclose expression in double dollar signs `$$ ... $$` or `\[ ... \]`
  ```markdown
  $$\sum_{k=1}^{n} k^3 = \left( \frac{n(n+1)}{2} \right)^2$$
  ```

For more examples, refer to the [Math Syntax Documentation](https://freatevietnam.github.io/freateoj-docs/#math-syntax).

---

## ⚙️ Useful Management Commands

| Command | Description |
| :--- | :--- |
| `python manage.py check` | Run system health and configuration sanity checks. |
| `python manage.py merge_replay_data <CONTEST_A> <CONTEST_B>` | Merge contest B's replay data into contest A as ghost users. |
| `python manage.py check_problem <CODE>` | Validate problem testcase configurations and metadata integrity. |
| `python manage.py rejudge <PROBLEM_OR_SUBMISSION>` | Queue rejudging for a problem or specific submission IDs. |

---

## 📚 Documentation & Resources

For detailed guides on setup, administration, and problem authoring, visit **[freatevietnam.github.io/freateoj-docs](https://freatevietnam.github.io/freateoj-docs/)**:

- 📖 [Installation Guide](https://freatevietnam.github.io/freateoj-docs/#installation)
- ⚖️ [Judge Execution Engine Setup](https://freatevietnam.github.io/freateoj-docs/#judge-setup)
- 📝 [Problem Package & Testcase Format](https://freatevietnam.github.io/freateoj-docs/#problem-format)
- 🔌 [REST API Reference](https://freatevietnam.github.io/freateoj-docs/#api)
- 🏅 [Contest Configuration & Scoring Rules](https://freatevietnam.github.io/freateoj-docs/#contest-formats)

---

## 🤝 Contributing

We welcome contributions from the community! Whether you are fixing bugs, improving UI accessibility, or translating documentation:

1. Fork the repository and create a feature branch (`git checkout -b feature/amazing-feature`).
2. Adhere to Python PEP8 and Django code conventions.
3. Submit a Pull Request detailing your changes.

Please refer to [CONTRIBUTING.md](contributing.md) for full guidelines.

---

## 🔒 Security

If you discover a security vulnerability within FreateOJ, please report it directly to **freatevietnam@gmail.com**. See [SECURITY.md](SECURITY.md) for our security policy and disclosure process.

---

## 🙏 Credits & Acknowledgments

FreateOJ draws inspiration, architecture patterns, and open-source contributions from:

- **[DMOJ (Don Mills Online Judge)](https://dmoj.ca/)** — Core architecture and judging protocol ([Source Code](https://github.com/DMOJ/online-judge))
- **[VNOJ (Viet Nam Online Judge)](https://github.com/VNOI-Admin/OJ)** — Community features and contest tools
- **[LQDOJ (Le Quy Don Online Judge)](https://lqdoj.edu.vn/)** — UI/UX improvements ([Source Code](https://github.com/LQDJudge/online-judge))
- **[OREOJ (ORE Online Judge)](https://ojkhanhhoa.site/)**
- **[CTOJ (Chuyen Tin Online Judge)](https://oj.chuyentin.pro/)**

---

## 📄 License

FreateOJ is released under the **[GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE)**.
