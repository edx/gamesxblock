# Games XBlock

An XBlock for adding interactive **Flashcards** and **Matching** games to edX courses.

> **Note:** No frontend UI is implemented for block configuration — full authoring support requires an MFE (Micro Frontend) configured for the platform.

---

## Features

| | |
|---|---|
| 🃏 **Two game types** | Flashcards and Matching |
| 🖼️ **Image support** | JPG, PNG, GIF, WebP, SVG for terms and definitions |
| 🔀 **Card shuffling** | Re-randomized on every page load when enabled |
| ⏱️ **Timer & best time** | Optional timer with per-student personal best (Matching) |
| 📄 **Pagination** | 5 pairs per page for large card sets |
| 🎉 **Confetti** | Animation on matching game completion |
| 🔒 **Encrypted answer keys** | Correct pairs never exposed in page source |
| 💾 **Configurable storage** | Django default storage or S3 |
| 🚩 **Waffle-flag gated** | Enable/disable at runtime without a redeploy |
| 🌐 **i18n support** | English and Latin-American Spanish included |

---

## Game Types

**🃏 Flashcards** — Single-card flip view. Navigate forward/backward through cards with a progress counter. Images supported on both sides.

**🔗 Matching** — Two-column click-to-match interface. Paginated (5 pairs/page), optional timer, tracks personal best, confetti on completion.

---

## Requirements

| Dependency | Version |
|------------|---------|
| Python | 3.8+ |
| Django | 2.2+ |
| XBlock | 1.2.0+ |
| web-fragments | 0.3.0+ |
| django-waffle | 5.0.0 |
| edx-toggles | 5.4.1 |
| cryptography | 3.4.8+ |

---

## Installation

```bash
pip install edx-games
```

---

## Usage

    1. In **Studio**, go to **Settings → Advanced Settings**.
    2. Add `"games"` to the **Advanced Module List** and click **Save Changes**.
    3. In your unit, click **Add New Component → Advanced → Games**.
    4. Click **Edit**, select a game type, add cards, configure shuffle/timer, and click **Save**.

---

## Configuration

### Waffle Flag

| Flag | Default | Description |
|------|---------|-------------|
| `legacy_studio.enable_games_xblock` | `False` | Enables the XBlock in Legacy Studio |

```bash
# Enable
./manage.py waffle_flag legacy_studio.enable_games_xblock --everyone --create
# Disable
./manage.py waffle_flag legacy_studio.enable_games_xblock --deactivate
```

### Storage Backend

By default, images use Django's `default_storage`. Override with `GAMESXBLOCK_STORAGE` in your LMS and CMS settings:

```python
# Filesystem
GAMESXBLOCK_STORAGE = {
    "storage_class": "django.core.files.storage.FileSystemStorage",
    "settings": {"location": "/path/to/media/games", "base_url": "/media/games/"},
}

# S3
GAMESXBLOCK_STORAGE = {
    "storage_class": "storages.backends.s3boto3.S3Boto3Storage",
    "settings": {"bucket_name": "my-bucket", "location": "games", "querystring_auth": True},
}
```

---

## Security

| | |
|---|---|
| 🔐 **Answer-key encryption** | Matching pairs encrypted with Fernet (AES + HMAC), key derived from block ID |
| 🕵️ **JS obfuscation** | Random variable names, element IDs, and function names on every render |
| ✅ **Image uploads** | Extension whitelist; files deduplicated by MD5 hash |

---
