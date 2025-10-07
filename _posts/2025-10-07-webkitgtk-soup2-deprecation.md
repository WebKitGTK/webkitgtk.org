---
title: Sunsetting libsoup 2 support in WebKitGTK
layout: post
author: aperez
date: 2025-10-07T10:58:00+03:00
---

## Summary

* Networking support for the WebKit GTK and WPE ports uses the
  [libsoup](https://libsoup.gnome.org/) library.

* In 2021 [libsoup had an API/ABI break](https://blog.tingping.se/2021/02/23/future-of-libsoup.html),
  resulting in the 3.0 major release.

* Since October 2021, *stable* releases after 2.34.0 of WebKitGTK and WPE
  have had support for using either libsoup version 2 or version 3. This
  was done in order to give developers time to migrate their applications.

* The WPE port removed support to use libsoup 2 [in May 2024](https://github.com/WebKit/WebKit/pull/28332),
  and 2.46.0 was the first *stable* release to support only libsoup 3.

* WebKitGTK 2.52.0, due in March 2026, will be the first *stable* release to
  ship without support for libsoup 2; the code is already [being
  removed](https://github.com/WebKit/WebKit/pull/51819) from the *main*
  development branch.

## What is libsoup?

The [libsoup](https://libsoup.gnome.org/) library provides HTTP networking
support for applications, using [GObject](https://docs.gtk.org/gobject/)
to integrate tightly with the GLib event loop.

The GTK and WPE WebKit ports use libsoup as a client for accessing network
resources using the HTTP, HTTP/2, and WebSocket protocols. As the library
supports being also used for serving content, this is used to to provide
embedded HTTP servers for WebDriver usage, to run tests, and more.


## Why is libsoup 2 support being phased out?

[Removing](https://github.com/WebKit/WebKit/pull/51819) the code needed to
support libsoup 2 will ease the maintenance burden on the team that develops
WebKitGTK and WPE. Additionally, it is our responsibility to nudge WebKit users
towards using libsoup 3, which is receiving active maintenance.

As of October 2025, Linux distributions like Debian or Chimera no longer
provide libsoup 2 packages and their WebKitGTK packages use libsoup 3. Other
distributions [like Arch Linux](https://archlinux.org/todo/libsoup-2-eol/) are
actively working on removing libsoup 2 from their repositories, or no longer
provide a WebKitGTK package built with libsoup 2, as is the case of Ubuntu
and Fedora.

The four and a half years since the first stable WebKitGTK release (2.34.0,
October 2021) with support for libsoup 3, and the first stable release that
will no longer support libsoup 2 (2.52.0, due in March 2026) should have
provided enough time for developers to migrate their applications.


## How can applications be migrated?

Applications that use the `webkit2gtk-4.0` API can easily migrate to the `4.1`
one: the only difference between those is that the former uses the old libsoup
2, while the latter uses libsoup 3.

- If your application uses **only** functionality provided WebKitGTK, changing
  the dependency on the `webkit2gtk-4.0` pkg-config module to `webkit2gtk-4.1`
  and rebuilding should be enough in most cases.

- If any other libraries used by the application also require libsoup, make
  sure those are also using libsoup 3.

- If your application code uses functionality from libsoup itself, follow the
  [migration guide](https://libsoup.gnome.org/libsoup-3.0/migrating-from-libsoup-2.html)
  included in the libsoup 3 manual.
