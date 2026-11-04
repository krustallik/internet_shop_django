# Project assessment

## Verdict

**Worth keeping as an academic and portfolio prototype.** This is more than a static mock-up: it has a real Django catalog, search and category filtering, a session-backed bag, promotions, user accounts, reviews, models, and Django Admin. Those features make it a useful demonstration of a small multi-app web project.

It should be presented as a learning project, not a production-ready online shop. There is no payment processor, shipping integration, inventory reservation, or cart checkout workflow. The separate legacy single-product route only records a demo order and does not collect money.

## Work completed

- Replaced the inconsistent storefront styling with a responsive English Northline design system.
- Added an editorial catalog hero, category navigation, clearer product cards, product details, review summaries, and mobile layouts.
- Created synthetic English product copy and original SVG illustrations for a repeatable portfolio catalog.
- Added an idempotent `seed_demo` management command and documented local setup.
- Made the cart and promo code controls clearer; promo application is available without creating an account, and removal uses a CSRF-protected POST.
- Removed the inert checkout link. The bag now states that payment and shipment are not available in this demo.
- Fixed the product detail view so its computed rating, distribution, and review context reaches the template.
- Removed a redundant admin middleware that intercepted Django’s own admin login. Django Admin now handles access through its built-in authentication and staff permissions.
- Changed demo orders to start in a “New” state and limited order confirmation pages to the signed-in owner.
- Added the missing product-offer, promo-code creation/list, and promo usage-report templates for the existing discount views.
- Replaced the unsupported CKEditor 4 dependency with a plain text field rendered with escaping. This removes an outdated editor bundle from the project and keeps the details field simple.
- Added local configuration for the secret key, debug mode, allowed hosts, database path, and media path.

## Remaining work before a real deployment

1. Implement a complete checkout, payment gateway integration, order lifecycle, receipts, and shipping workflow.
2. Add inventory rules and validate product availability and prices server-side at order creation.
3. Review account and uploaded-image validation, privacy, retention, and storage policies.
4. Configure a production database, HTTPS, secure cookies, static/media storage, logging, backups, and deployment automation.
5. Add automated coverage for account flows, bag totals, promotion edge cases, permissions, and orders.

The repository also contains its original tracked database and legacy uploaded media. This work used an isolated local demo database and synthetic SVGs for the screenshots; no existing database content or original uploads were used to create the preview.
