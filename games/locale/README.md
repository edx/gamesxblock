# Translations

## Quick Start

Extract translatable strings:
```bash
make extract_translations
```

Compile translations:
```bash
make compile_translations
```

## Files

- `games/locale/en/LC_MESSAGES/django-partial.po` - Source strings
- `games/locale/<locale>/LC_MESSAGES/django.po` - Translations per locale
- `games/locale/<locale>/LC_MESSAGES/django.mo` - Compiled translations

## Locales

**Available:** en  
**Planned:** ar, es_419, fr, zh_CN
