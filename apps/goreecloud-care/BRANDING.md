# GoreeCloud Care Branding

Product name: **GoreeCloud Care**  
Repository: `GoreeCloud/goreecloud-zorin-os`  
Component path: `apps/goreecloud-care/`  
Production application identifier reserved: `com.goreecloud.care`  
Development application identifier: `com.goreecloud.care.dev`

## Canonical identity authority

The authoritative GoreeCloud Care application icon is maintained centrally at:

`GoreeCloud/goreecloud-branding-assets/products/care/app-icon.svg`

Canonical asset blob at the initial dev18 synchronization checkpoint:

`c4568ce4b24b9eb47971ec522317b737f1a509c8`

The Care repository-local packaging copy at `packaging/icons/com.goreecloud.care.svg` is a derivative required for offline Debian packaging. It must remain synchronized with the canonical branding-assets source and must not become a competing branding authority.

## Identity direction

The Care icon uses the current GoreeCloud product-icon construction language: a rounded-square field, a restrained teal-to-blue gradient, and simple high-contrast white geometry. Its heart outline communicates care and stewardship; the central plus form communicates positive maintenance and restoration without implying medical diagnosis, security certification, or a generic GoreeCloud platform mark.

The platform-wide GoreeCloud logo must not replace this product-specific Care identity.

## Consumer usage

The Development desktop entry uses `Icon=com.goreecloud.care`, and the Debian package installs the canonical derivative at:

`/usr/share/icons/hicolor/scalable/apps/com.goreecloud.care.svg`

Future application windows, launchers, websites, App Store surfaces, documentation, and other Care consumers must use this identity or a governed derivative from the same canonical asset. Do not independently redraw, recolor, or substitute an unrelated symbolic icon when the Care identity is available.

## Glaze UI boundary

The canonical icon establishes product identity; it does not by itself prove final GLAZE UI conformance. Care's native GTK visual system remains governed by the current Stable GLAZE UI consumer requirements documented in `GLAZE-UI-CONFORMANCE.md` and still requires rendered target acceptance for the release candidate.
