---
layout: post
title: Non-free files in some versions of WebKitGTK+
---

We have noticed that some releases of WebKitGTK+ contain files that are
covered by a license that does not allow redistribution.

We have replaced those images with free equivalents, and have released
WebKitGTK+ 2.2.8, 2.4.6, 2.5.90 and 2.6.0. These releases only contain
free images.

### What files are affected?

The Web Inspector images, located under Source/WebInspectorUI/UserInterface/Images/

### What releases contain the non-free files?

 - The 2.1.92 release
 - The 2.2.x series (excluding 2.2.8 and higher)
 - The 2.3.x series
 - The 2.4.x series (excluding 2.4.6 and higher)
 - The 2.5.x series (excluding 2.5.90 and higher)

### What happens now with the affected releases?

We have removed them from the archive, replacing them with new
tarballs. The new tarballs have an 'a' appended to the version number
("2.1.92a", "2.4.3a", etc) and have the non-free images removed or
replaced with the free ones where possible, but are else identical to
the old ones.

If you use any of the affected WebKitGTK+ releases, we urge you to
upgrade to a version without the non-free images.
