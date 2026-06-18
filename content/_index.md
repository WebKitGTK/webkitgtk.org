+++
template = "index.html"
+++

<picture class="full pixels">
    <source srcset="assets/splash-dark.png" media="(prefers-color-scheme: dark)">
    <img src="assets/splash.png">
</picture>

WebKitGTK is a full-featured port of the WebKit rendering engine,
suitable for projects requiring any kind of web integration, from hybrid
HTML/CSS applications to full-fledged web browsers. It offers WebKit's
full functionality and is useful in a wide range of systems from desktop
computers to embedded systems like phones, tablets, and televisions.
WebKitGTK is made by a lively community of developers and designers,
who hope to bring the web platform to everyone.
It's the official web engine of the GNOME platform and is used in
browsers such as [Epiphany](https://apps.gnome.org/Epiphany),
[Wike](https://apps.gnome.org/Wike/), and
[Web Apps](https://codeberg.org/eyekay/webapps). Accessibility is a core
value — we are committed to making the web work for individuals of all
ages and abilities.

<img src="assets/webkit-windows.webp" class="filterimg" alt="webkit browsers" />

## Web process separation

Since adding support for WebKit2, it's possible to build applications that use
the web platform with increased security and responsiveness. The web is a
jungle, but web pages cannot crash the main application or freeze the UI.

## Support for audio and video

The web isn't just for reading words. We drive development of the
[GStreamer](https://gstreamer.freedesktop.org) WebKit backend and support full
integration of video into page content and the HTML canvas element. Currently
we are working to finish support for [WebAudio](https://www.w3.org/TR/webaudio/)
and [WebRTC](https://webrtc.org).

## 3D CSS and accelerated rendering

WebKitGTK can use the GPU to enable smooth page compositing and scrolling, as
well as 3D CSS transforms and 3D HTML canvas (otherwise known as
[WebGL](https://www.khronos.org/webgl/)). This
makes WebKitGTK suitable for a whole range of games and visualization
applications.



