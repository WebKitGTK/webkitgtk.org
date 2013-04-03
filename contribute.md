---
layout: one-column
main-title: Contribute
section: contribute
---

## How can I help out? ##

Checkout the source code, build WebKit from trunk and test it.

Report bugs at the [bug tracker](http://bugs.webkit.org), look for existing [WebKitGTK+ bugs](https://bugs.webkit.org/buglist.cgi?query_format=advanced&short_desc_type=allwordssubstr&short_desc=&long_desc_type=substring&long_desc=gtk&bug_file_loc_type=allwordssubstr&bug_file_loc=&keywords_type=allwords&keywords=&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&emailassigned_to1=1&emailtype1=substring&email1=&emailassigned_to2=1&emailreporter2=1&emailcc2=1&emailtype2=substring&email2=&bugidtype=include&bug_id=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&cmdtype=doit&order=Reuse+same+sort+as+last+time&field0-0-0=noop&type0-0-0=noop&value0-0-0=).

### Mailing Lists ###

For archives and information on how to subscribe, visit our [mailing list information page](http://lists.webkit.org/mailman/listinfo/webkit-gtk).

### Developing ###

To build and test WebKitGTK+, follow the [instructions on the wiki](http://trac.webkit.org/wiki/BuildingGtk).

For a good starting point see the [Hacker's guide to WebKitGTK+](http://trac.webkit.org/wiki/HackingGtk).

After fetching the sources you can build WebKitGTK+ from the source tree like this:

    mkdir WebKitBuild
    cd WebKitBuild
    ../autogen.sh
    make

The build is pretty much a normal autotools build, so you can look at `configure --help` for build options or specify `--prefix=/usr`.

Have a look at the [Coding Style](http://webkit.org/coding/coding-style.html) used in WebKit.

### Testing ###

Run regression tests:

    WebKitBuild/Programs/DumpRenderTree
    WebKitBuild/Programs/UnitTests
    WebKitBuild/Programs/GtkLauncher
