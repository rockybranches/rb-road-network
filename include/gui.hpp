#ifndef AOAGUI_H
#define AOAGUI_H

#include <gtk/gtk.h>
#include <glib.h>
#include <glib/gprintf.h>
#include <stdio.h>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <chrono>

#include "rbtypes.hpp"
#include "utils.hpp"
#include "places.hpp"
#include "pre_gui.hpp"
#include "plot.hpp"

#ifdef _USEGL
#include <GL/glew.h>
#include <GL/glu.h>
#endif

static int width, height;
static GtkWidget *canvas;
static GtkWidget* spinner;
static GtkWidget* load_label;
static GtkWidget* tons_entry;
static GtkWidget* ptable_text;
static GtkWidget* ptable_label;
static GtkNotebook* notebook;

GtkWidget* window;
GtkWidget* about_window;

static bool road_params_changed = true;
PreGuiProcessor processor;

extern "C" {
  void on_about_response(GtkDialog*dialog, gint response, gpointer user_data);
  void on_about_close(GtkDialog*dialog, gpointer user_data);
  
  // GTK Callbacks
  void main_window_aoa_destroy_cb();

  // menuitem callback functions
  void on_import_roads_button_clicked_cb(GtkMenuItem* menuitem,
					 gpointer data);
  void on_new_button_clicked_cb(GtkMenuItem* menuitem,
				gpointer data);
  void on_saveas_button_clicked_cb(GtkMenuItem* menuitem,
				   gpointer data);
  void on_quit_button_clicked_cb(GtkMenuItem* menuitem,
				 gpointer data);
  void on_ptable_quit_activate(GtkMenuItem* menuitem,
			       gpointer data);
  void on_help_activate_cb(GtkMenuItem* menuitem,
			   gpointer data);
  void on_about_main_activate(GtkMenuItem* menuitem,
			      gpointer data);  
  
  // button callback functions
  void on_find_area_button_clicked_cb(GtkWidget *widget,
				      GdkEventButton *event,
				      gpointer data);
  void on_create_poptable_btn_clicked(GtkWidget *widget,
				      GdkEventButton *event,
				      gpointer data);

  // entry callback functions
  bool on_latlong_entry_editing_done_cb(GtkWidget* entry,
					gpointer data);
  bool on_radius_entry_editing_done_cb(GtkWidget* entry,
				       gpointer data);
  bool on_stride_entry_editing_done_cb(GtkWidget* entry,
				       gpointer data);
  bool on_imsz_entry_editing_done_cb(GtkWidget* entry,
				     gpointer data);
  bool zoom_entry_editing_done_cb(GtkWidget* entry,
				  gpointer data);
  
}

GtkWidget* message_dialog(std::string msg, GtkWidget* widget);

// Gtk callbacks
void main_window_aoa_destroy_cb()
{
  std::cout << "main_window_aoa_destroy_cb() called...\n";
  delete gdata;
  fclose(stdout);
  gtk_main_quit();
#ifdef _WIN32
  // pthread_exit(NULL);
  exit(0);
#endif
  exit(0);
}

// menuitem callbacks

void on_about_response(GtkDialog*dialog, gint response, gpointer user_data)
{
  gtk_widget_hide(GTK_WIDGET(dialog));
}

void on_about_close(GtkDialog*dialog, gpointer user_data)
{
  gtk_window_close(GTK_WINDOW(dialog));
}

void on_about_main_activate(GtkMenuItem* menuitem,
			    gpointer data)
{
  gtk_widget_show_all(GTK_WIDGET(about_window));
}

void on_help_activate_cb(GtkMenuItem* menuitem,
		      gpointer data)
{
  GtkWidget* msgd = message_dialog("(1) Enter the start coordinate, and adjust the other area parameters.\n\n"
				   "(2) Click 'Find Area!' to compute the Area of Availability via the roads.\n\n"
				   "(3) Set the population table options.\n\n"
				   "(4) Click 'Create Pop. Table!' to create the population table from the plotted area.\n"
				   "...You will be prompted to save the area image and the population table text to file.\n", window);
  gint res = gtk_dialog_run(GTK_DIALOG(msgd));
  gtk_widget_destroy (msgd);
}

void on_import_roads_button_clicked_cb(GtkMenuItem* menuitem,
				       gpointer data)
{
  GtkWidget *dialog;
  GtkFileChooserAction action = GTK_FILE_CHOOSER_ACTION_OPEN;
  gint res;
  dialog = gtk_file_chooser_dialog_new ("Open Roads shapefile (*.shp)",
				        NULL,
					action,
					("_Cancel"),
					GTK_RESPONSE_CANCEL,
					("_Open"),
					GTK_RESPONSE_ACCEPT,
					NULL);
  res = gtk_dialog_run (GTK_DIALOG (dialog));
  if (res == GTK_RESPONSE_ACCEPT)
    {
      char *filename;
      GtkFileChooser *chooser = GTK_FILE_CHOOSER (dialog);
      filename = gtk_file_chooser_get_filename (chooser);
      shapefn = std::string(filename);
      processor.loadRoads(&road_params_changed, &gdata);
      g_free (filename);
    }
  gtk_widget_destroy (dialog);
}

void on_new_button_clicked_cb(GtkMenuItem* menuitem,
			      gpointer data)
{
  pi = 0;
  clear_surface();
  gdata->counties.empty();
  gdata->mvec.empty();
}

void on_quit_button_clicked_cb(GtkMenuItem* menuitem,
			       gpointer data)
{
  std::cout << "quit button clicked.\n";
  main_window_aoa_destroy_cb();
}

void error_dialog(std::string err, GtkWidget* widget);
void error_dialog(std::string err, GtkWidget* widget)
{
  GtkDialogFlags flags = GTK_DIALOG_DESTROY_WITH_PARENT;
  GtkWidget *dialog;
  dialog = gtk_message_dialog_new (NULL,
				   flags,
				   GTK_MESSAGE_ERROR,
				   GTK_BUTTONS_CLOSE,
				   "Error: “%s”",
				   err.c_str());
  gtk_dialog_run (GTK_DIALOG (dialog));
  gtk_widget_destroy (dialog);
}

GtkWidget* message_dialog(std::string msg, GtkWidget* widget)
{
  GtkDialogFlags flags = GTK_DIALOG_DESTROY_WITH_PARENT;
  GtkWidget *dialog;
  dialog = gtk_message_dialog_new (NULL,
				   flags,
				   GTK_MESSAGE_INFO,
				   GTK_BUTTONS_CLOSE,
				   "“%s”",
				   msg.c_str());
  return dialog;
}


// button callbacks

void on_create_poptable_btn_clicked(GtkWidget *widget,
				    GdkEventButton *event,
				    gpointer data)
{
  // if(!processor.done||road_params_changed)
  //   {
  //   }
  on_find_area_button_clicked_cb(widget, event, data);
  gtk_main_iteration();
  on_saveas_button_clicked_cb((GtkMenuItem*)widget,data);
  gtk_main_iteration();
}

#ifndef _WIN32
#include <thread>
#else
#include <pthread.h>
#endif

void *do_calcs(gpointer ddat)
{
  // load roads, calculate grid
  processor.done = false;
  gtk_grab_add((GtkWidget*)load_label);
  processor.process(&road_params_changed, &gdata);
  gtk_grab_remove((GtkWidget*)load_label);
  #ifdef _WIN32
  pthread_exit(NULL);
  #endif
}

void on_find_area_button_clicked_cb(GtkWidget *widget,
				    GdkEventButton *event,
				    gpointer data)
{

  std::chrono::high_resolution_clock::time_point dt0 = std::chrono::high_resolution_clock::now();
  
  gtk_widget_show(spinner);
  gtk_widget_set_visible(load_label,FALSE);
  gtk_label_set_text((GtkLabel*)load_label, "Loading...");
  gtk_widget_set_visible(load_label,TRUE);
  gtk_grab_add((GtkWidget*)spinner);
  g_idle_add((GSourceFunc)gtk_spinner_start,(GtkSpinner*)spinner);
  gtk_grab_remove((GtkWidget*)spinner);
  gtk_widget_queue_resize(GTK_WIDGET(window));
  gtk_widget_show_all(window);
  if(road_params_changed)
    {
      processor.done = false;
      
#ifndef _WIN32
      
      // Linux behavior:
      std::thread(do_calcs,nullptr).detach();
      while(true)
	{
	  if(processor.done)
	    break;
	  while(gtk_events_pending())
	    {
	      if(processor.done)
		break;
	      gtk_main_iteration();
	    }
	}
#else
      
      // Windows behavior:
      pthread_t pth;
      int rc = pthread_create(&pth, NULL, do_calcs, nullptr);
      if (rc)
	{
	  printf("ERROR; return code from pthread_create() is %d\n", rc);
	  exit(-1);
	}
      int tdone = -1;
      while(!(processor.done) && tdone!=0)
	{
	  tdone = _pthread_tryjoin(pth, NULL);
	  gtk_main_iteration();
	}
      gtk_spinner_stop((GtkSpinner*)spinner);
#endif
      
      road_params_changed = false;
    }
  gtk_label_set_text((GtkLabel*)load_label, "Plotting...");
  pi = 0;
#ifdef _USEGL
  std::cout << "drawing to canvas..." << std::endl;
  gtk_gl_area_queue_render((GtkGLArea*) canvas);
#else
  std::cout << "drawing to canvas..." << std::endl;
  gtk_widget_queue_draw(canvas);
#endif
  std::cout << "done drawing.\n";
  gtk_spinner_stop((GtkSpinner*)spinner);
  gtk_label_set_text((GtkLabel*)load_label, "Complete.");
  gtk_widget_set_visible(load_label,FALSE);
  g_idle_remove_by_data((GtkSpinner*)spinner);
  gtk_widget_show_all(window);
  gtk_widget_set_visible(load_label,FALSE);
  gtk_notebook_set_current_page(notebook, 1); // go to canvas tab
  int cii=0;
  while(gtk_events_pending() && cii < 10)
    {
      gtk_main_iteration(); cii++;
    }
  
  std::chrono::high_resolution_clock::time_point dt1 = std::chrono::high_resolution_clock::now();
  std::chrono::duration<float> dtime_span =
    std::chrono::duration_cast<std::chrono::duration<float>>(dt1-dt0);
  std::cout << "Find Area (Calculation + Plot) Time: " << dtime_span.count() << " seconds.\n";
}

void on_saveas_button_clicked_cb(GtkMenuItem* menuitem,
				 gpointer data)
{
  GtkWidget *dialog;
  GtkFileChooser *chooser;
  GtkFileChooserAction action = GTK_FILE_CHOOSER_ACTION_SAVE;
  gint res;
  
  // save image dialog
  dialog = gtk_file_chooser_dialog_new ("Save Image (.png)",
					NULL,
					action,
					("_Cancel"),
					GTK_RESPONSE_CANCEL,
					("_Save"),
					GTK_RESPONSE_ACCEPT,
					NULL);
  chooser = GTK_FILE_CHOOSER (dialog);
  gtk_file_chooser_set_do_overwrite_confirmation (chooser, TRUE);
  gtk_file_chooser_set_current_name (chooser,
				     ("AreaOfAvailabilityImage.png"));
  res = gtk_dialog_run (GTK_DIALOG (dialog));
  if (res == GTK_RESPONSE_ACCEPT)
    {
      char *filename;
      filename = gtk_file_chooser_get_filename (chooser);
      if(use_GL)
	{
	  gtk_writePNG(GTK_WIDGET(canvas), gdata->w, gdata->h, filename);
	}
      else
	{
	  GdkPixbuf *dest;
	  dest = gdk_pixbuf_new_from_file(gdata->fn.c_str(), NULL);
	  gdk_pixbuf_save(dest, filename, "png", NULL, NULL);
	  if(dest)
	    g_object_unref(dest);
	}
      g_free (filename);
    }
  gtk_widget_destroy (dialog);
  gtk_notebook_set_current_page(notebook, 1);

  // save text dialog
  dialog = gtk_file_chooser_dialog_new ("Save Table Text (.txt)",
					NULL,
					action,
					("_Cancel"),
					GTK_RESPONSE_CANCEL,
					("_Save"),
					GTK_RESPONSE_ACCEPT,
					NULL);
  chooser = GTK_FILE_CHOOSER (dialog);
  gtk_file_chooser_set_do_overwrite_confirmation (chooser, TRUE);
  gtk_file_chooser_set_current_name (chooser,
				     ("CountyPopulationTable.txt"));
  res = gtk_dialog_run (GTK_DIALOG (dialog));
  if (res == GTK_RESPONSE_ACCEPT)
    {
      char *filename;
      filename = gtk_file_chooser_get_filename (chooser);
      {
	// create population table
	std::ostringstream text;
	text << "\\begin{tabular}{r|*{5}{l}}\n"
	     << "County & 2010 & 2015 & 2020 & 2025 & 2030 \\\\ \n"
	     << "\\hline\n";
	int totals[5] = {0};
	for(County& cty: gdata->counties)
	  {
	    if(cty.avail)
	      {
		text << cty.name;
		int tj=0;
		for(int& cpc: cty.pop.pops)
		  {
		    text << " & " << std::to_string(cpc);
		    totals[tj] += cpc;
		    tj++;
		  }
		text << "\\\\ \n";
	      }
	  }
	text << "\\\\ \n"
	     << "\\hline\\hline\n"
	     << "    Totals = ";
	for(int i=0; i < 5; i++)
	  {
	    text << " & " << totals[i];
	  }
	text << "\\newline\n"
	     << "\\end{tabular} \\\\ \n"
	     << "\\begin{tabular}{l|l}\n\\hline\\hline\n\\newline\n"
	     << " Population increase (2015 to 2030) & "
	     << std::fixed << (totals[4] - totals[1]) << " \\\\ \n"
	     << " Percent population increase & "
	     << std::fixed << std::setprecision(1) << 100.0*((float)(totals[4] - totals[1])/(float)totals[1]) << " \\\\ \n";
	const gchar* entrystr = gtk_entry_get_text((GtkEntry*)tons_entry);
	float tons_person = (float)std::atof(entrystr);
	text << " Tons needed by market (2015) & " << std::fixed << std::setprecision(1) <<
	  tons_person*totals[1] << "  (" <<  tons_person << " tons/person) \\\\ \n";
	text << " Tons needed by market (2030) & " << std::fixed << std::setprecision(1) <<
	  tons_person*totals[4] << "  (" <<  tons_person << " tons/person) \\\\ \n";
	text << " Increase in tons needed (2015 to 2030) & " << std::fixed << std::setprecision(1) <<
	  tons_person*(totals[4] - totals[1]) << " \\\\ \n";
	text << "\\end{tabular}\n";
	// save text to file
	std::ofstream ofs;
	ofs.open(filename);
	if(ofs.is_open())
	  {
	    std::cout << "opened poptable text file: " << filename << std::endl;
	    ofs << text.str();
	    std::cout << "wrote poptable text to file: " << filename << std::endl;
	    ofs.close();
	  }
	GtkTextBuffer* ptbuf = gtk_text_view_get_buffer((GtkTextView*)ptable_text);
	gtk_text_buffer_set_text(ptbuf, text.str().c_str(), -1);
	gtk_text_view_set_buffer((GtkTextView*)ptable_text, ptbuf);
      }
      gtk_label_set_text((GtkLabel*)ptable_label, filename);
      g_free (filename);
    }
  gtk_widget_destroy (dialog);
  gtk_notebook_set_current_page(notebook, 2);  
}

// GtkEntry callbacks

bool zoom_entry_editing_done_cb(GtkWidget* entry,
				gpointer data)
{
  float zoom_init = zoom;
  const gchar* entrystr = gtk_entry_get_text((GtkEntry*)entry);
  zoom = (float)atof(entrystr);
  if(zoom!=zoom_init)
    road_params_changed = true;
  return GDK_EVENT_PROPAGATE;
}

bool on_latlong_entry_editing_done_cb(GtkWidget* entry,
				      gpointer data)
{
  const gchar* entrystr = gtk_entry_get_text((GtkEntry*)entry);
  try {
    gchar** estr_split = g_strsplit(entrystr, ",", -1);
    if(sizeof(estr_split)==sizeof(gchar*))
      {
	std::string str_east = (std::string)(estr_split[0]);
	trim(str_east);
	std::string str_north = (std::string)(estr_split[1]);
	trim(str_north);
	float spi[2] = {start_point[0],start_point[1]};
	start_point[0] = (float)atof(str_east.c_str());
	start_point[1] = (float)atof(str_north.c_str());
	mercator(start_point);
	if(spi[0]!=start_point[0]||spi[1]!=start_point[1])
	  road_params_changed = true;
      }
    else
      {
	error_dialog("Enter coordinate in decimal degrees, e.g. -83.66, 33.445", entry);
      }
    g_strfreev(estr_split);
  } catch (std::exception& excep) {
      error_dialog("Enter coordinate in decimal degrees, e.g. -83.66, 33.25", entry);
  }
  return GDK_EVENT_PROPAGATE;
}

bool on_imsz_entry_editing_done_cb(GtkWidget* entry,
				   gpointer data)
{
  const gchar* entrystr = gtk_entry_get_text((GtkEntry*)entry);
  gchar** estr_split = g_strsplit(entrystr, ",", -1);
  float iw, ih;
  if(sizeof(estr_split)==sizeof(gchar*))
    {
      try {
	std::string str0 = (std::string)(estr_split[0]);
	trim(str0);
	std::string str1 = (std::string)(estr_split[1]);
	trim(str1);
	iw = (float)atof(str0.c_str());
	ih = (float)atof(str1.c_str());
	if(iw!=gdata->w||ih!=gdata->h)
	  {
	    gdata->w = iw;
	    gdata->h = ih;
	    pi=1;
	    gtk_widget_set_size_request (canvas, gdata->w, gdata->h);
	    gtk_widget_queue_resize(GTK_WIDGET(canvas));
	    while(gtk_events_pending())
	      gtk_main_iteration();
	    if(use_GL)
	      {
		gtk_gl_area_queue_render((GtkGLArea*)canvas);
		gtk_widget_queue_resize(GTK_WIDGET(canvas));
	      }
	    else {
	      gtk_widget_queue_draw(canvas);
	    }
	    while(gtk_events_pending())
	      gtk_main_iteration();
	    gtk_widget_show_all(window);
	    while(gtk_events_pending())
	      gtk_main_iteration();
	    pi = 0;
	  }
      } catch (std::exception& excep) {
	error_dialog("Enter the width, height in pixels for the output image, e.g. 800, 800", entry);
      }
    }
  else
    {
      error_dialog("Enter the width, height in pixels for the output image, e.g. 800, 800", entry);
    }
  g_strfreev(estr_split);
  return GDK_EVENT_PROPAGATE;
}

bool on_stride_entry_editing_done_cb(GtkWidget* entry,
				     gpointer data)
{
  const gchar* entrystr = gtk_entry_get_text((GtkEntry*)entry);
  stride[0] = (float)(atof(entrystr));
  if(stride[0] < 0.01)
    stride[0] = 0.01;
  if(stride[0]!=stride[1])
    road_params_changed = true;
  stride[1] = stride[0];
  return GDK_EVENT_PROPAGATE;
}

bool on_radius_entry_editing_done_cb(GtkWidget* entry,
				     gpointer data)
{
  float radius_init = radius;
  const gchar* entrystr = gtk_entry_get_text((GtkEntry*)entry);
  radius = (float)(atof(entrystr) * 1e3);
  if(radius_init!=radius)
    road_params_changed = true;
  return GDK_EVENT_PROPAGATE;
}

void gtk_gui_start(int w, int h);

void gtk_gui_start(int w, int h)
{
  GtkBuilder *builder;
  width = w;
  height = h;
  gdata->w=w;
  gdata->h=h;
  gtk_init(0, NULL);
  if(use_GL)
    {
      builder =
	gtk_builder_new_from_file((RB_ROADNETWORK_RESOURCES_PATH+"/AoA_GL.glade").c_str());
    }
  else
    {
      builder =
	gtk_builder_new_from_file((RB_ROADNETWORK_RESOURCES_PATH + "/AoA.glade").c_str());
    }
  // windows
  window = GTK_WIDGET(gtk_builder_get_object(builder, "main_window_aoa"));
  about_window = GTK_WIDGET(gtk_builder_get_object(builder, "about_window"));
  // ptable widgets
  ptable_label = GTK_WIDGET(gtk_builder_get_object(builder, "poptable_label"));
  ptable_text = GTK_WIDGET(gtk_builder_get_object(builder, "poptable_text"));
  // main window widgets
  notebook = (GtkNotebook*)(GTK_WIDGET(gtk_builder_get_object(builder, "notebook")));
  load_label = GTK_WIDGET(gtk_builder_get_object(builder, "load_text"));
  tons_entry = GTK_WIDGET(gtk_builder_get_object(builder, "tons_entry"));
  GtkWidget* latlong_entry = GTK_WIDGET(gtk_builder_get_object(builder, "latlong_entry"));
  float startcoord[2];
  printf("start point in mercator: %.2f, %.2f meters\n",start_point[0], start_point[1]);
  invmercator(start_point[0], start_point[1], startcoord);
  printf("start point in dec degrees: %.3f, %.3f\n",startcoord[0], startcoord[1]);
  std::stringstream txtstream;
  std::string sc0, sc1;
  std::string latlong_txt;
  txtstream << std::fixed << std::setprecision(3) << startcoord[0] << ", " << startcoord[1];
  latlong_txt = txtstream.str();
  gtk_entry_set_text((GtkEntry*)latlong_entry, latlong_txt.c_str());
  g_signal_connect(GTK_WIDGET(latlong_entry), "focus-out-event", G_CALLBACK(on_latlong_entry_editing_done_cb), nullptr);
  g_signal_connect((GtkEntry*)latlong_entry, "editing-done", G_CALLBACK(on_latlong_entry_editing_done_cb), nullptr);
  GtkWidget* radius_entry = GTK_WIDGET(gtk_builder_get_object(builder, "radius_entry"));
  g_signal_connect(GTK_WIDGET(radius_entry), "focus-out-event", G_CALLBACK(on_radius_entry_editing_done_cb), nullptr);
  g_signal_connect((GtkEntry*)radius_entry, "editing-done", G_CALLBACK(on_radius_entry_editing_done_cb), nullptr);
  GtkWidget* stride_entry = GTK_WIDGET(gtk_builder_get_object(builder, "stride_entry"));
  g_signal_connect(GTK_WIDGET(stride_entry), "focus-out-event", G_CALLBACK(on_stride_entry_editing_done_cb), nullptr);
  g_signal_connect((GtkEntry*)stride_entry, "editing-done", G_CALLBACK(on_stride_entry_editing_done_cb), nullptr);
  GtkWidget* imsz_entry = GTK_WIDGET(gtk_builder_get_object(builder, "imsz_entry"));
  g_signal_connect(GTK_WIDGET(imsz_entry), "focus-out-event", G_CALLBACK(on_imsz_entry_editing_done_cb), nullptr);
  g_signal_connect((GtkEntry*)imsz_entry, "editing-done", G_CALLBACK(on_imsz_entry_editing_done_cb), nullptr);
  GtkWidget* zoom_entry = GTK_WIDGET(gtk_builder_get_object(builder, "zoom_entry"));
  g_signal_connect(GTK_WIDGET(zoom_entry), "focus-out-event", G_CALLBACK(zoom_entry_editing_done_cb), nullptr);
  g_signal_connect((GtkEntry*)zoom_entry, "editing-done", G_CALLBACK(zoom_entry_editing_done_cb), nullptr);
  canvas = GTK_WIDGET(gtk_builder_get_object(builder, "canvas"));
  gtk_widget_set_size_request (canvas, w, h);
  gtk_widget_queue_resize(GTK_WIDGET(canvas));
  gtk_builder_connect_signals(builder, NULL);
  
  // GL Canvas or Draw canvas
  if(use_GL)
    {
#ifdef _USEGL
      g_signal_connect(canvas, "render", G_CALLBACK(*(gdata->rfunc)), NULL);
      g_signal_connect(canvas, "realize", G_CALLBACK(realize_GL), NULL);
      g_signal_connect(canvas, "resize", G_CALLBACK(resize_GL), NULL);
      g_signal_connect(canvas, "unrealize", G_CALLBACK(unrealize_GL), NULL);
      gtk_gl_area_set_auto_render((GtkGLArea*) canvas, TRUE);
#endif
    }
  else
    {
      g_signal_connect(canvas, "draw", G_CALLBACK(*(gdata->pfunc)), gdata);
    }
  
  spinner = GTK_WIDGET(gtk_builder_get_object(builder, "spinner"));
  gtk_widget_set_size_request(spinner, 100, 100);
  GtkWidget* runbtn = GTK_WIDGET(gtk_builder_get_object(builder, "find_area_button"));
  GtkWidget* popbtn = GTK_WIDGET(gtk_builder_get_object(builder, "create_poptable_btn"));
  gtk_widget_set_size_request(runbtn, 5, 3);
  g_signal_connect(runbtn, "clicked", G_CALLBACK(on_find_area_button_clicked_cb), canvas);
  g_signal_connect(popbtn, "clicked", G_CALLBACK(on_create_poptable_btn_clicked), nullptr);
  g_signal_connect(window, "destroy", G_CALLBACK(main_window_aoa_destroy_cb), nullptr);
  g_object_unref(builder);
  
  gtk_widget_show_all(window);
  gtk_main();
}

#endif
