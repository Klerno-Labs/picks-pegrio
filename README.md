# Picks by Pegrio

This repository contains the maintained static site served at picks.pegrio.com.
Article HTML is the source. `build.py` validates it; it does not regenerate copy.
The former generator is preserved in Git history and must not be used to replace
current pages.

Before release:

```sh
python3 build.py
node --test scripts/analytics.test.mjs
```

Keep all guide URLs unless a deliberate redirect or retirement is reviewed.
Do not invent hands-on tests, measurements, reviews, credentials, ratings or
product results. A source check must link the primary source, state its real date
and distinguish manufacturer claims from independent results. Article corrections
must be visible. Unverified prices and rankings are not product structured data.

Use the shared consent-aware analytics loader once per full page. Do not insert
page-specific Google scripts. Keep private evidence and credentials out of this
public repository. Run local checks before a production deployment and verify
the current canonical hostname after release; preview success alone is insufficient.
