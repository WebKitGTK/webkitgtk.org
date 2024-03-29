const baseURLApiLevelSuffix = (function (uri) {
  const slashPos = uri.lastIndexOf("/");
  const dashPos = uri.lastIndexOf("-", slashPos);
  return uri.substring(dashPos, slashPos + 1);
})(window.location.href);
baseURLs = [
  ["GLib", "https://docs.gtk.org/glib/"],
  ["GObject", "https://docs.gtk.org/gobject/"],
  ["Gio", "https://docs.gtk.org/gio/"],
  ["Gdk", "https://docs.gtk.org/gdk3/"],
  ["Gtk", "https://docs.gtk.org/gtk3/"],
  ["JavaScriptCore", "../javascriptcoregtk" + baseURLApiLevelSuffix],
  ["WebKit2", "../webkit2gtk" + baseURLApiLevelSuffix],
  ["WebKit2WebExtension", "../webkit2gtk-web-extension" + baseURLApiLevelSuffix],
]
