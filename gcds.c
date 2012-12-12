/* Copyright (c) 2009 Christian Dywan <christian@twotoasts.de>
   This code is licensed under the terms of the expat license */

/* gcc -o wk wk.c $(pkg-config --cflags --libs webkit-1.0) -Wall -O1 -g */

#include <webkit/webkit.h>
#include <JavaScriptCore/JavaScript.h>

static GtkWidget* register_button = NULL;

const gchar* form_markup =
  "<body style=\"background-color:#EF8E3A;\"><form>"
  "Name <b>(required)</b><br>"
  "<input type=\"text\" onkeyup=\"setCanRegister (this.value != '')\"><br>"
  "Favourite animal<br>"
  "<input type=\"text\" style=\"color: #000; background-color:#A9F796;\"><br>"
  "Favourite colour:<br>"
  "<object type=\"application/x-gtk-color-button\" "
  "style=\"height: 2em; width: 10em;\"></object><br>"
  "</form></body>";

static void
color_button_color_set_cb (GtkWidget* button,
                           gpointer   userdata)
{
  GtkWidget* web_view = GTK_WIDGET (userdata);
  GdkColor color;
  gchar* script;

  gtk_color_button_get_color (GTK_COLOR_BUTTON (button), &color);
  script = g_strdup_printf ("document.body.style.backgroundColor = "
    "\"#%x%x%x\";", color.red / 256, color.green / 256, color.blue / 256);
  webkit_web_view_execute_script (WEBKIT_WEB_VIEW (web_view), script);
}

static GtkWidget*
web_view_create_plugin_widget_cb (GtkWidget*   web_view,
                                  const gchar* mime_type,
                                  const gchar* uri,
                                  GHashTable*  param,
                                  gpointer     userdata)
{
  if (g_str_equal (mime_type, "application/x-gtk-color-button"))
    {
      GtkWidget* button = gtk_color_button_new ();
      GdkColor color;
      gdk_color_parse ("#EF8E3A", &color);
      gtk_color_button_set_color (GTK_COLOR_BUTTON (button), &color);
      g_signal_connect (button, "color-set",
                        G_CALLBACK (color_button_color_set_cb), web_view);
      return button;
    }
  return NULL;
}

static JSValueRef
set_can_register_cb (JSContextRef     js_context,
                     JSObjectRef      js_function,
                     JSObjectRef      js_this,
                     size_t           argument_count,
                     const JSValueRef js_arguments[],
                     JSValueRef*      js_exception)
{
  JSValueRef js_value = JSValueMakeNull (js_context);

  if (argument_count == 1
    && JSValueGetType (js_context, js_arguments[0]) == kJSTypeBoolean)
    {
      bool sensitive = JSValueToBoolean (js_context, js_arguments[0]);
      gtk_widget_set_sensitive (register_button, sensitive == true);
    }

  return js_value;
}

int
main (int    argc,
      gchar* argv[])
{
  GtkWidget* window;
  GtkWidget* vbox;
  GtkWidget* scrolled;
  GtkWidget* web_view;
  GtkWidget* button_box;
  WebKitWebFrame* web_frame;
  JSGlobalContextRef js_context;
  JSObjectRef js_global;
  JSStringRef js_function_name;
  JSObjectRef js_set_can_register;

  if (!g_thread_supported ())
    g_thread_init (NULL);
  gtk_init_check (&argc, &argv);

  window = gtk_window_new (GTK_WINDOW_TOPLEVEL);
  gtk_window_set_title (GTK_WINDOW (window), "WebKitGTK+ API Demo");
  gtk_window_set_default_size (GTK_WINDOW (window), 640, 240);
  g_signal_connect (window, "destroy", G_CALLBACK (gtk_main_quit), NULL);
  vbox = gtk_vbox_new (FALSE, 4);
  gtk_container_add (GTK_CONTAINER (window), vbox);

  scrolled = gtk_scrolled_window_new (NULL, NULL);
  gtk_scrolled_window_set_policy (GTK_SCROLLED_WINDOW (scrolled),
                                  GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
  gtk_box_pack_start (GTK_BOX (vbox), scrolled, TRUE, TRUE, 0);
  web_view = webkit_web_view_new ();
  gtk_container_add (GTK_CONTAINER (scrolled), web_view);
  webkit_web_view_load_string (WEBKIT_WEB_VIEW (web_view), form_markup, "text/html", "UTF-8", "");
  g_signal_connect (web_view, "create-plugin-widget",
                    G_CALLBACK (web_view_create_plugin_widget_cb), NULL);

  button_box = gtk_hbutton_box_new ();
  gtk_box_pack_start (GTK_BOX (vbox), button_box, FALSE, FALSE, 0);
  register_button = gtk_button_new_with_mnemonic ("Send _Registration");
  gtk_widget_set_sensitive (register_button, FALSE);
  gtk_box_pack_start (GTK_BOX (button_box), register_button, FALSE, FALSE, 0);

  web_frame = webkit_web_view_get_main_frame (WEBKIT_WEB_VIEW (web_view));
  js_context = webkit_web_frame_get_global_context (web_frame);
  js_global = JSContextGetGlobalObject (js_context);
  js_function_name = JSStringCreateWithUTF8CString ("setCanRegister");
  js_set_can_register = JSObjectMakeFunctionWithCallback (js_context,
    js_function_name, (JSObjectCallAsFunctionCallback)set_can_register_cb);
  JSObjectSetProperty (js_context, js_global, js_function_name, js_set_can_register, 0, NULL);
  JSStringRelease (js_function_name);

  gtk_widget_show_all (window);

  gtk_main ();

  return 0;
}

