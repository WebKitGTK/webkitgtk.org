---
layout: default
---

![Screenshot of Epiphany using WebKitGTK](/images/screenshot.png)

## Web content rendering ##

WebKitGTK is a full-featured port of the WebKit rendering engine,
suitable for projects requiring any kind of web integration, from hybrid
HTML/CSS applications to full-fledged web browsers. It offers WebKit's
full functionality and is useful in a wide range of systems from desktop
computers to embedded systems like phones, tablets, and televisions.
WebKitGTK is made by a lively community of developers and designers,
who hope to bring the web platform to everyone.
It's the official web engine of the GNOME platform and is used in
browsers such as [Epiphany](http://projects.gnome.org/epiphany/),
[Eolie](https://wiki.gnome.org/Apps/Eolie), and
[Tangram](https://github.com/sonnyp/Tangram).

## Web process separation ##

Since adding support for WebKit2, it's possible to build applications that
use the web platform with increased security and responsiveness. The web
is a jungle, but web pages cannot crash the main application or freeze the
UI. WebKitGTK also uses process separation to seamlessly support GTK 2 plugins
(like Flash) in GTK 3 applications.

## Accessibility ##

Access is one of our core values. For this reason, we are committed to making
the web work for individuals of all ages and abilities, from all walks of life,
all over the world.

## Support for audio and video ##

The web isn't just for reading words. We drive development of the GStreamer
WebKit backend and support full integration of video into page
content and the HTML canvas element. Currently we are working to finish
support for WebAudio and WebRTC.

## 3D CSS and accelerated rendering ##

WebKitGTK can use the GPU to enable smooth page compositing and
scrolling, as well as 3D CSS transforms and 3D HTML canvas (otherwise
known as WebGL). This makes WebKitGTK suitable for a whole range
of games and visualization applications.
