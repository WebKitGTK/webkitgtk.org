<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/xml; charset=utf-8" />
    <meta http-equiv="expires" content="0" />
    <meta name="robots" content="index,follow" />
    <meta name="language" content="en" />
    <meta name="author" content="Christian Dywan" />
    <meta name="description" content="The WebKitGTK+ webpage." />
    <meta name="keywords" content="WebKit,GTK,GTK+,WebKitGtk,WebKitGTK+,GtkWebKit" />
    <!--<link rel="shortcut icon" href="webkitgtk.png" />-->
    <link title="default" rel="stylesheet" type="text/css" href="style.css" />
    <title>The WebKitGTK+ webpage</title>
  </head>
  <body>
    <div id="container">
      <div id="header">
        <h1>WebKitGTK+</h1>
      </div>

      <?php
      if (!isset ($_GET['page']))
          $_GET['page'] = 'about';

      function current_page ($current)
        {
          if ($current == $_GET['page'])
            echo ' class="current"';
        }

      ?>

      <div id="menu">
        <table>
          <tr>
            <td><a title="Learn what WebKitGTK+ is"
              href="./"<?php current_page('about')?>>About</a></td>
            <td><a title="Documentation for users and developers"
              href="./?page=documentation"<?php current_page('documentation')?>>Documentation</a></td>
            <!--<td><a title="What you can do with WebKitGTK+"
              href="./?page=features"<?php current_page('features')?>>Features</a></td>-->
            <td><a title="Download the latest version of WebKitGTK+"
              href="./?page=download"<?php current_page('download')?>>Download</a></td>
            <!--<td><a title="Applications using WebKitGTK+ today"
              href="./?page=applications"<?php current_page('applications')?>>Applications</a></td>-->
            <td><a title="Find out how to help out"
              href="./?page=contribute"<?php current_page('contribute')?>>Contribute</a></td>
            <td><a title="Find out how to get in touch"
              href="./?page=contact"<?php current_page('contact')?>>Contact</a></td>
          </tr>
        </table>
      </div>

      <div id="content">
      <?php

      switch ($_GET['page'])
        {
          case 'about':?>

        <h2><a name="WhatIsGTK">What is WebKitGTK+ anyway?</a></h2>

        <p>WebKitGTK+ is the port of the portable web rendering engine
	  <a href="http://webkit.org/">WebKit</a> to the GTK+ platform.
	  Random tidbits about WebKitGTK+ can be found at
	  <a href="http://live.gnome.org/WebKitGtk">GNOME's Wiki</a>.</p>

        <?php
          break;
          case "documentation":?>

        <h2><a name="Documentation">Documentation</a></h2>

	<h3>API Reference for developers</h3>
        <p>We provide complete documentation of the public API, with examples
           when possible by using gtk-doc.</p>

        <p><a href="http://webkitgtk.org/reference/webkitgtk/stable/index.html">API Reference for developers (stable)</a></p>
	<p><a href="http://webkitgtk.org/reference/webkitgtk/unstable/index.html">API Reference for developers (unstable)</a></p>

	<p>WebKit2 preliminary API documentation. Take into account that WebKit2 is still under development, 
           so the API might change.</p>

	<p><a href="http://webkitgtk.org/reference/webkit2gtk/unstable/index.html">WebKit2 preliminary API Reference for developers (unstable)</a></p>

	<h3>Additional documentation</h3>
	<p><a href="http://webkitgtk.org/Cookbook 0.1b.pdf">Cook book (PDF)</a>, by Bob Murphy</p>

        <p><a href="gcds.html">Presentation introducing WebKitGTK+</a> (GCDS 2009)<br>
           By Christian Dywan, Gustavo Noronha Silva, Xan Lopez</p>

        <?php
          break;
          case "download":?>

        <h2><a name="Download">Download WebKitGTK+ now!</a></h2>

        <h3>Stable tree</h3>

        <p>Download the current stable release of WebKitGTK+:</p>

        <p><a href="releases/webkitgtk-1.10.2.tar.xz">WebKitGTK+ 1.10.2 (8.6 MB)</a></p>

        <p>The stable tree is maintained in the svn repository at webkit.org:</p>

        <p><pre>svn co http://svn.webkit.org/repository/webkit/releases/WebKitGTK/webkit-1.10</pre></p>

        <h3>Development tree</h3>

        <p>You can also download the latest development release:</p>

        <p><a href="releases/webkitgtk-1.11.91.tar.xz">WebKitGTK+ 1.11.91 (9.3 MB)</a></p>

        <p>Or checkout the development tree of WebKit from svn:</p>

        <p><pre>svn co http://svn.webkit.org/repository/webkit/trunk</pre></p>

        <p>Alternatively there is a git mirror for your convenience:</p>

        <p><pre>git clone git://git.webkit.org/WebKit.git</pre></p>


        <?php
          break;
          case "contact":?>

	<h2><a name="Contact">Get in touch!</a></h2>

	<p>We use mailing lists and IRC as our main communication channels.
	You can find us in the <b>#webkit</b>, and <b>#webkitgtk+</b>
	channels of the FreeNode network - <i>irc.freenode.net</i>.</p>

	<p>To get in touch using e-mail subscribe to the
	<a href="http://lists.webkit.org/mailman/listinfo/webkit-gtk">webkit-gtk</a>
	mailing list. There are <a href="http://lists.webkit.org/mailman/listinfo">other
	mailing lists</a>, please check their descriptions before posting!</p>

        <?php
          break;
          case "contribute":?>

        <h2><a name="Contribute">How can I help out?</a></h2>

        <p>Checkout the source code, build WebKit from trunk and test it.
           Report bugs at the <a href="http://bugs.webkit.org">bug tracker</a>,
           look for existing <a href="https://bugs.webkit.org/buglist.cgi?query_format=advanced&short_desc_type=allwordssubstr&short_desc=&long_desc_type=substring&long_desc=gtk&bug_file_loc_type=allwordssubstr&bug_file_loc=&keywords_type=allwords&keywords=&bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&emailassigned_to1=1&emailtype1=substring&email1=&emailassigned_to2=1&emailreporter2=1&emailcc2=1&emailtype2=substring&email2=&bugidtype=include&bug_id=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&cmdtype=doit&order=Reuse+same+sort+as+last+time&field0-0-0=noop&type0-0-0=noop&value0-0-0="
           >WebKitGTK+ bugs</a>.</p>
	<h3>Mailing Lists</h3>
	<p>For archives and information on how to subscribe, visit our 
	   <a href="http://lists.webkit.org/mailman/listinfo/webkit-gtk">mailing list information page</a>.
	 </p>

	<h3>Developing</h3>
        <p>To build and test WebKitGTK+, follow the <a href="http://trac.webkit.org/wiki/BuildingGtk">instructions on the wiki</a>.
           For another good starting point see the <a href="http://trac.webkit.org/wiki/HackingGtk">Hacker's guide to WebKitGTK+</a>.</p>

        <?php
          break;
          default:?>

        <h2><a name="NotFound">Not Found</a></h2>

        <p>There is no page here.</p>

        <?php
        }?>
      </div>

      <div id="footer">Copyright © 2009 The WebKitGTK+ Team<br>
                       Hosting kindly provided by <a href="http://www.igalia.com">Igalia</a></div>

    </div>

  </body>
</html>
