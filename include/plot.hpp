#ifndef RB_AOAPLOT_H
#define RB_AOAPLOT_H

#include "rbtypes.hpp"
#include "utils.hpp"
#include "grid.hpp"
#include "places.hpp"

#ifdef _USEGL
#include "lodepng.h"
#include "plot_gltxt.hpp"
#include <GL/glew.h>
#include <GL/glu.h>
#endif

#include <gtk/gtk.h>
#include <gdk/gdk.h>
#include <glib.h>
#include <glib/gprintf.h>
#include <cairo.h>
#include <stdio.h>
#include <vector>

float extra_pt[2], ex2[2];
float image_offset_factor = 0.02; // border size plotted around map area

/*
  Global Surfaces
*/
static cairo_surface_t *gtk_cairo_surf = NULL;
static cairo_surface_t *csurf = NULL;

inline void imscale(float xy[2], float coord[2], float sshift[4], float imsz[4]);
inline void arscale(float xy[2], float coord[2], float arr[4], float sshift[4], float imsz[4]);
void gtk_writePNG(GtkWidget* widget, float w, float h, std::string="cairotest.png");

static void gtk_paintGrid(GtkWidget *widget, cairo_t *cr, gpointer data); // default plot func

#ifdef _USEGL
static bool render_GL(GtkGLArea* area_GL, GdkGLContext *context_GL); // default render func (GL)
static void realize_GL(GtkGLArea* widget); // realize func
static void unrealize_GL(GtkGLArea* widget); // unrealize func
static void resize_GL(GtkGLArea *area,
		      gint       width,
		      gint       height,
		      gpointer   user_data);
#endif

struct gtkGridData { // gdata struct
  const char di = 'g';
  std::vector<GridRect> gvec;
  RoadStore mvec; // normalized roads
  std::vector<County> counties;
  float startpt[2] = {0.5,0.5};
  float w=800, h=800;
  std::string fn = RB_DATA_PATH+"/imgrid.png";
  void (*pfunc)(GtkWidget *widget,cairo_t *cr,gpointer data) = &gtk_paintGrid;
#ifdef _USEGL
  bool (*rfunc)(GtkGLArea* area_GL, GdkGLContext *context_GL) = &render_GL;
#endif
  gtkGridData(){}
};

static gtkGridData* gdata;
static int pi = 0; // reset plot flag


#ifdef _USEGL

/* GL Map Stuff */
GLuint tex_id; // Name of texture for map


static void realize_GL(GtkGLArea* area)
{
  gtk_gl_area_make_current(area);
  // If there were errors during the initialization or
  // when trying to make the context current, this
  // function will return a #GError for you to catch
  if (gtk_gl_area_get_error (area) != NULL)
    return;

  GLenum glew_err = glewInit();
  if(GLEW_OK != glew_err)
    std::cout << "GLEW Error: " << glewGetErrorString(glew_err) << std::endl;
  
  glViewport(0, 0, gdata->w, gdata->h);
  glDisable(GL_DEPTH_TEST);
  glActiveTexture(GL_TEXTURE0);
  glClearColor(1.0, 1.0, 1.0, 1.0); // clear buffer
  glClear(GL_COLOR_BUFFER_BIT); glClear(GL_SRC_ALPHA); glClear(GL_POINT_SMOOTH); glClear(GL_STENCIL_BUFFER_BIT);
  glClear(GL_BLEND); glClear(GL_TEXTURE_2D);
  glEnable(GL_BLEND); glEnable(GL_POINT_SMOOTH);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glGenTextures(1, &tex_id);
  glBindTexture(GL_TEXTURE_2D, tex_id);
  init_font_resources(); // initialize resources for drawing text
}

static void unrealize_GL(GtkGLArea* widget)
{
  free_resources();
  glDeleteTextures(1, &tex_id);
  glClear(GL_COLOR_BUFFER_BIT); glClear(GL_SRC_ALPHA); glClear(GL_POINT_SMOOTH); glClear(GL_STENCIL_BUFFER_BIT);
  glClear(GL_BLEND); glClear(GL_TEXTURE_2D);
}

static void resize_GL(GtkGLArea *area,
		      gint       width,
		      gint       height,
		      gpointer   user_data)
{
  glViewport(0, 0, gdata->w, gdata->h);
  glMatrixMode(GL_TEXTURE_2D);
  glLoadIdentity();
}

void drawCountyPolyGL(County& ct, float clinewidth, float cbound[4], float ccolor[4], float sshift[4], float imsz[4], GLenum polymode);

// OpenGL backend render function, gdata->rfunc

static bool render_GL(GtkGLArea* area_GL, GdkGLContext *context_GL)
{
  // glViewport(0, 0, gdata->w, gdata->h);
  std::cout << "render_GL called!\n";
  {
    float imsz[4] = { (float)2.0, (float)2.0, 0, 0};
    float sshift[4] = { -1, -1, 1, 1 }; // sshift opengl
    float wys = (float)gtk_widget_get_allocated_height(GTK_WIDGET(area_GL));
    float wxs = (float)gtk_widget_get_allocated_width(GTK_WIDGET(area_GL));
    glDisable(GL_BLEND);
    glClearColor(1.0, 1.0, 1.0, 1.0); // clear buffer
    glClear(GL_COLOR_BUFFER_BIT); glClear(GL_SRC_ALPHA); glClear(GL_POINT_SMOOTH);
    glClear(GL_BLEND); glClear(GL_TEXTURE_2D); glClear(GL_STENCIL_BUFFER_BIT);
    glEnable(GL_BLEND); glEnable(GL_POINT_SMOOTH); glEnable(GL_TEXTURE_2D);
    glDisable(GL_DEPTH_TEST);
    glDeleteTextures(1, &tex_id);
    glActiveTexture(GL_TEXTURE0);
    glGenTextures(1, &tex_id);
    glBindTexture(GL_TEXTURE_2D, tex_id);
    
    glMatrixMode(GL_TEXTURE_2D);
    glLoadIdentity();
    glScalef(gdata->w/wxs, gdata->h/wys, 1.0);
    float xy[2], xy1[2];

    /*
      Plot County GL Background
    */
    float cbound[4] = {0}; // county bounding box (to calculate center for label placement)
    float ccolorFill[4] = {150.0/255, 150./255, 70./255, 1.0}; // county fill color
    for(County& ct: gdata->counties)
      {
	if(ct.avail)
	  {
	    ct.print_county();
	    drawCountyPolyGL(ct, 1, cbound, ccolorFill, sshift, imsz, GL_FILL); // draw county polygon
	  }
      }
      
      /*
	Plot Roads GL
      */
      int ctt=0;
      glPointSize(2);
      for(PointRoad& rd: gdata->mvec)
	{
	  glBegin(GL_LINE_STRIP);
	  glColor4f(0.3, 0.3, 0.3, 1.0); // roads GL
	  for(Point<BasePoint>& pt: rd)
	    {
	      xy[0] = pt[0];
	      xy[1] = 1-pt[1];
	      imscale(xy, xy, sshift, imsz);
	      glVertex2f(xy[0], xy[1]);
	      xy1[0] = pt[0];
	      xy1[1] = 1-pt[1];
	      imscale(xy1, xy1, sshift, imsz);
	      if(lindist(xy1, xy) >= mindist*2)
		glVertex2f(xy1[0], xy1[1]);
	    }
	  glEnd();
	  ctt++;
	}
      
      /*
	Plot Grids GL
      */
      glPointSize(7);
      for(GridRect& gr: gdata->gvec) // grids GL
	{
	  if(gr.use && gr.avail)
	    {
	      glBegin(GL_POLYGON);
	      glColor4f(0.95, 0.15, 0.15, 0.7); // avail grid
	      glLineWidth(1.5);
	      
	      xy[0] = gr.xr[0]; xy[1] = 1-gr.yr[0];
	      imscale(xy, xy, sshift, imsz);
	      glVertex2f(xy[0], xy[1]);

	      xy[0] = gr.xr[0]; xy[1] = 1-gr.yr[1];
	      imscale(xy, xy, sshift, imsz);
	      glVertex2f(xy[0], xy[1]);

	      xy[0] = gr.xr[1]; xy[1] = 1-gr.yr[1];
	      imscale(xy, xy, sshift, imsz);
	      glVertex2f(xy[0], xy[1]);

	      xy[0] = gr.xr[1]; xy[1] = 1-gr.yr[0];
	      imscale(xy, xy, sshift, imsz);
	      glVertex2f(xy[0], xy[1]);
	      glEnd();
	    }
	}

      /*
	Plot Start Point GL
      */
      glPointSize(10.0);
      glBegin(GL_POINTS);
      glColor4f(0.95, 0.2, 0.2, 1.0); // start point GL
      xy[0] = 0.5; xy[1] = 0.5;
      imscale(xy, xy, sshift, imsz);
      glVertex2f(xy[0], xy[1]);
      glVertex2f(xy[0], xy[1]);
      glEnd();
      glFlush();
      
      /*
	Plot Counties GL (outline, text)
      */
      float ccolorOutline[4] = {0.0, 0.0, 230./255, 1.0}; // county outline color
      float clw = 7.00; // boundary linewidth
      for(County& ct: gdata->counties)
	{
	  if(ct.avail)
	    {
	      ct.print_county();
	      drawCountyPolyGL(ct, clw, cbound, ccolorOutline, sshift, imsz, GL_POINT); // draw county polygon
	      glFlush();
	    }
	}
      
      /*
	Plot Text
      */
      int ctext_color[4] = {255, 255, 255, 255};
      std::cout << "plotting text for counties... (OpenGL)\n";
      for(County& ct: gdata->counties)
	{
	  if(ct.avail)
	    {
	      ct.print_county();
	      xy[0] = ct.label_loc[0];
	      xy[1] = 1-ct.label_loc[1];
	      imscale(xy, xy, sshift, imsz);
	      std::cout << "(GLtext) (xoffset,yoffset)=" << xy[0] << "," << xy[1] << std::endl;
	      render_text(ct.name.c_str(), xy[0], xy[1],
			  ctext_color, GTK_WIDGET(area_GL), tex_id, gdata->w, gdata->h); // draw text for county name label
	      glFlush();
	    }
	}
    }
  pi = 1;
  return TRUE;
}

void drawCountyPolyGL(County& ct, float clinewidth, float cbound[4], float ccolor[4], float sshift[4], float imsz[4], GLenum polymode)
{
  float xy0[2], xy[2], xy1[2];
  glColor4f(ccolor[0], ccolor[1], ccolor[2], ccolor[3]); // set color for county boundary/fill
  glPointSize(clinewidth); // set linewidth for county boundary
  glPolygonMode(GL_FRONT_AND_BACK, polymode); // set polygon mode (options: GL_FILL, GL_LINE, GL_POINT)
  glBegin(GL_POLYGON);
  int ii=0;
  for(auto side: ct.shape->sides)
    {
      // if(ii < (int)ct.shape->sides.size()-1)
	{
	  xy[0] = side.a[0]; xy[1] = 1-side.a[1];
	  imscale(xy, xy, sshift, imsz);
	  xy1[0] = side.b[0]; xy1[1] = 1-side.b[1];
	  imscale(xy1, xy1, sshift, imsz);
	  if(lindist(xy, xy1) < 0.05)
	  {
	    glTexCoord2f(xy[0], xy[1]);
	    glVertex2f(xy[0], xy[1]);
	    glVertex2f(xy[0], xy[1]);
	    glTexCoord2f(xy1[0], xy1[1]);
	    glVertex2f(xy1[0], xy1[1]);
	    glVertex2f(xy1[0], xy1[1]);
	  }
	  xy0[0] = xy[0]; xy0[1] = xy[1];
	}
      ii++;
    }
  glEnd();
  glPolygonMode(GL_FRONT_AND_BACK, GL_FILL); // set polygon mode to default
}

#endif


/* **************** End of GL-only code **************** */


inline void imscale(float xy[2], float coord[2], float sshift[4], float imsz[4])
{
  xy[0] = sshift[0] + (sshift[2]-sshift[0])*(coord[0]-0.0)/(1.0-0.0);
  xy[1] = sshift[1] + (sshift[3]-sshift[1])*(coord[1]-0.0)/(1.0-0.0);
}

inline void arscale(float xy[2], float coord[2], float arr[4], float sshift[4], float imsz[4])
{
  xy[0] = sshift[0] + (sshift[2]-sshift[0])*(coord[0]-arr[0])/(arr[1]-arr[0]);
  xy[1] = sshift[1] + (sshift[3]-sshift[1])*(coord[1]-arr[2])/(arr[3]-arr[2]);
}

void gtk_writePNG(GtkWidget* widget, float w, float h, std::string fn)
{
  printf("writing to png (gtk)...%s\n",fn.c_str());

  GdkPixbuf *dest;

  if(!use_GL)
    {
      gint wx, wy;
      gtk_widget_translate_coordinates(widget, gtk_widget_get_toplevel(widget), 0, 0, &wx, &wy);
      gtk_widget_queue_draw(widget);
      dest = gdk_pixbuf_get_from_window(gtk_widget_get_window(widget), wx, wy,
					gtk_widget_get_allocated_width(widget),
					gtk_widget_get_allocated_height(widget) );
      gdk_pixbuf_save(dest, fn.c_str(), "png", NULL, NULL);
    }
  else
    {
#ifdef _USEGL
      gint wx, wy;
      gtk_widget_translate_coordinates(gtk_widget_get_toplevel(GTK_WIDGET(widget)), GTK_WIDGET(widget), 0, 0, &wx, &wy);
      std::cout << "writePNG : wx = " << wx << " wy = " << wy << std::endl;
      int winh = gdk_window_get_height(gtk_widget_get_window(widget));
      int winw = gdk_window_get_width(gtk_widget_get_window(widget));
      std::cout << "writePNG : winh = " << winh << " winw = " << winw << std::endl;
      gint width = (gint)gdata->w;
      gint height = (gint)gdata->h;
      int cstride = width * 4;
      glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_id, 0);
      glPixelStorei (GL_PACK_ALIGNMENT, 4);
      glPixelStorei (GL_PACK_ROW_LENGTH, width);
      std::vector<unsigned char> imdata_c(height*cstride);
      glReadPixels(-wx, winh-height+wy, width, height, GL_RGBA, GL_UNSIGNED_BYTE, imdata_c.data());
      glPixelStorei (GL_PACK_ROW_LENGTH, 0);
      glBindFramebuffer (GL_FRAMEBUFFER, 0);
      glFlush();
      
      // lodepng
      std::vector<unsigned char> imdata_o;
      for(int i=0; i < height; i++)
	{
	  imdata_o.insert(imdata_o.begin()+i*cstride,
			  imdata_c.end()-cstride*(i+1),
			  imdata_c.end()-cstride*i);
	}
      unsigned error = lodepng::encode(fn.c_str(), imdata_o, width, height);
      std::cout << "lodepng error " << error << std::endl;
      std::cout << "finished gtk_writePNG : " << fn << std::endl;
#endif
    }
}

void cairo_writePNG(std::string fn);
static void clear_surface (void);
static void cairo_GridImagePlot(GtkWidget *widget,
				cairo_t *cr,
				gpointer data);
void plotScaleBar(float imsz[4], float sshift[4], cairo_t*cr);
void newFig(float imsz[4], float sshift[4], cairo_t*cr);
void plotStart(cairo_t *cr, float start[2], float imsz[4], float sshift[4]);
void plotCounties(cairo_t *cr, std::vector<County> cts, float imsz[4], float sshift[4]);
void plotRoads(cairo_t *cr, std::vector<PointRoad> prs, float imsz[4], float sshift[4]);

void plotStart(cairo_t *cr, float start[2], float imsz[4], float sshift[4])
{
  std::cout << "plot start!" << std::endl;
  cairo_set_line_cap  (cr, CAIRO_LINE_CAP_ROUND); /* Round dot*/
  float xy[2];
  imscale(xy, start, sshift, imsz);
  cairo_set_source_rgba (cr, 0., 0.5, 0.5, 1.0);
  cairo_set_line_width (cr, 10.0);
  cairo_move_to(cr, xy[0], xy[1]); cairo_line_to(cr, xy[0], xy[1]);
  cairo_stroke(cr);
}

void plotCounties(cairo_t *cr, std::vector<County> cts, float imsz[4], float sshift[4])
{
  
  printf("plotting counties...\n");
  float xy[2]; float xy1[2];
  if((int)cts.size()==1)
    cts.at(0).avail = true;
  double cbounds[4] = {0}; // (x1, y1) , (x2, y2)
  float ccolors[4] = {0.0, 209./255, 209./255, 0.85};
  cairo_set_source_rgba (cr, ccolors[0], ccolors[1], ccolors[2], ccolors[3]);
  cairo_set_line_width (cr, 2.45*imsz[0]/600.0);
  int skipix=10, cii=0;
  for(County& ct: cts)
    {
      if(ct.avail)
	{
	  ct.print_county();
	  cairo_new_path(cr);
	  for(auto side: ct.shape->sides)
	    {
	      if((cii % skipix) == 0)
		{
		  xy[0] = side.a[0]; xy[1] = side.a[1];
		  imscale(xy, xy, sshift, imsz);
		  xy1[0] = side.b[0]; xy1[1] = side.b[1];
		  imscale(xy1, xy1, sshift, imsz);
		  if(xy1[0] > sshift[0] && xy1[0] < sshift[2] && xy1[1] > sshift[1] && xy1[1] < sshift[3])
		    {
		      cairo_move_to(cr, xy[0], xy[1]); cairo_line_to(cr, xy1[0], xy1[1]);
		      cairo_stroke_preserve(cr);
		    }
		  cairo_set_source_rgba (cr, ccolors[0], ccolors[1], ccolors[2], ccolors[3]);
		  cairo_set_line_width (cr, 2.45*imsz[0]/600.0);
		}
	      skipix++;
	    }
	  xy[0] = ct.shape->sides.at(0).a[0]; xy[1] = ct.shape->sides.at(0).a[1];
	  imscale(xy, xy, sshift, imsz);
	  cairo_move_to(cr, xy1[0], xy1[1]); cairo_line_to(cr, xy[0], xy[1]);
	  cairo_stroke_preserve(cr);
	  cairo_close_path(cr);
	  cairo_path_extents(cr, &cbounds[0], &cbounds[1], &cbounds[2], &cbounds[3]); // compute bounding box for placing the label
	  ct.label_loc[0] = (cbounds[2]+cbounds[0])/2.0;
	  ct.label_loc[1] = (cbounds[3]+cbounds[1])/2.0;
	  cairo_stroke(cr);
	}
    }
  
  for(County& ct: cts)
    {
      if(ct.avail)
	{
	  cairo_text_extents_t te;
	  cairo_text_extents (cr, ct.name.c_str(), &te);
	  float xl = ct.label_loc[0];
	  float yl = ct.label_loc[1];
	  
	  if(xl < sshift[0])
	    xl = sshift[0]*1.02;
	  if(xl > sshift[2])
	    xl = sshift[2]/1.02;
	  if(yl < sshift[1])
	    yl = sshift[1]*1.02;
	  if(yl > sshift[3])
	    yl = sshift[3]/1.02;
	  
	  // text background
	  cairo_set_source_rgba (cr, ccolors[0]*0.9, ccolors[1]*0.9, ccolors[2]*0.9, 0.95);
	  cairo_rectangle(cr, xl-te.width*0.05, yl-te.height*1.3,
			  te.width*1.25, te.height*1.45);
	  cairo_stroke_preserve(cr);
	  cairo_fill(cr);
	  
	  // county text label
	  cairo_select_font_face (cr, "Arial", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_BOLD);
	  cairo_set_font_size (cr, 18);
	  cairo_set_source_rgba (cr, 0., 0., 0., 1.);
	  std::cout << "county bounds: " << " " << cbounds[0] << " " << cbounds[1]
		    << " " << cbounds[2] << " " << cbounds[3] << std::endl;
	  cairo_move_to(cr, xl, yl);
	  cairo_show_text (cr, ct.name.c_str());
	}
    }
}

void plotRoads(cairo_t *cr, std::vector<PointRoad> prs, float imsz[4], float sshift[4])
{
  printf("plotting roads..\n");
  cairo_set_line_cap  (cr, CAIRO_LINE_CAP_ROUND); /* Round dot*/
  cairo_set_source_rgba (cr,0.5,0.5,0.5,0.95);
  cairo_set_line_width (cr, 2.0*imsz[0]/600.0);
  float xy[2];
  int skipix = 5;
  for(PointRoad& rd: prs)
    {
      int skipc = 0;
      for(Point<BasePoint>& pt: rd)
	{
	  if(skipc==0)
	    {
	      xy[0] = pt[0];
	      xy[1] = pt[1];
	      imscale(xy, xy, sshift, imsz);
	      cairo_move_to(cr, xy[0], xy[1]);
	      skipc++;
	      continue;
	    }
	    {
	      xy[0] = pt[0];
	      xy[1] = pt[1];
	      // cairo_set_source_rgba (cr,1,1,1,1);
	      // cairo_set_line_width (cr, 2.0*imsz[0]/600.0);
	      imscale(xy, xy, sshift, imsz);
	      cairo_line_to(cr, xy[0], xy[1]);
	      cairo_stroke_preserve(cr);
	      skipc=0;
	    }
	}
      cairo_stroke(cr);
    }
}

void plotGrid(cairo_t *cr, std::vector<GridRect> gvec, float imsz[4], float sshift[4])
{
  std::cout << "plotting grid..." << std::endl;
  cairo_set_operator(cr, CAIRO_OPERATOR_OVER);
  cairo_set_line_width (cr, 0.85*imsz[0]/600.0);
  float ul[2];
  for(GridRect& gr: gvec)
    {
      ul[0]=gr.xr[0]; ul[1]=gr.yr[0];
      imscale(ul,ul,sshift,imsz);
      if(gr.use)
	{
	  if(gr.avail)
	    {
	      cairo_set_source_rgba (cr,0.9,0.05,0.05,0.55);
	      cairo_rectangle(cr, ul[0], ul[1], gr.w*imsz[0], gr.h*imsz[1]);
	      cairo_set_source_rgba (cr,0.9,0.05,0.05,0.55);
	      cairo_fill(cr);
	    }
	}
    }
}

void plotScaleBar(float imsz[4], float sshift[4], cairo_t*cr)
{
  /* 
     plot scale bar
  */
  cairo_set_line_cap  (cr, CAIRO_LINE_CAP_SQUARE); /* square for scale bar */
  float scale_ratio = 0.4; // percentage of the total width to use (area)
  float sbar_c[4] = {204.0/255.0, 1.0, 204.0/255.0, 1.0}; // scale color
  float sbar_loc[2] = { sshift[0]*1.14, sshift[2]*0.99 };
  cairo_set_source_rgba(cr, sbar_c[0], sbar_c[1], sbar_c[2], sbar_c[3]);
  cairo_rectangle(cr, sbar_loc[0], sbar_loc[1], imsz[0]*scale_ratio, imsz[1]*0.2);
  cairo_fill(cr);
  std::string stxt = std::to_string((marr[1]-marr[0])*scale_ratio/1e3);
  stxt.erase(stxt.find(".")+2, std::string::npos);
  std::string scale_text = "[ ";
  scale_text += stxt + " km";
  scale_text += " ]";
  std::cout << "scale bar display text = " << scale_text << std::endl;
  cairo_select_font_face (cr, "monospace", CAIRO_FONT_SLANT_NORMAL, CAIRO_FONT_WEIGHT_BOLD);
  cairo_set_font_size (cr, 18.0*(1.0-0.5*zoom));
  cairo_text_extents_t tebk;
  cairo_text_extents (cr, scale_text.c_str(), &tebk);
  float stxt_loc[2] = { sbar_loc[0]+imsz[0]*scale_ratio/2-tebk.width/2.,
			sbar_loc[1]+tebk.height };
  cairo_set_source_rgba(cr,sbar_c[0]/4.,sbar_c[1]/4.,sbar_c[2]/3.,1); // text front color
  cairo_move_to (cr, stxt_loc[0], stxt_loc[1]);
  cairo_show_text (cr, scale_text.c_str());
  cairo_stroke(cr);
  
  // draw the scale bar symbol
  cairo_set_line_width (cr, 3.0);
  float woff=1.25, hoff=0.45;
  cairo_move_to(cr, 4*woff+sbar_loc[0]+woff*scale_ratio, stxt_loc[1]-hoff*imsz[1]*scale_ratio*0.08);
  cairo_line_to(cr, 4*woff+sbar_loc[0]+woff*scale_ratio, stxt_loc[1]*(1+0.01*hoff));
  cairo_stroke(cr); // leftv
  
  cairo_move_to(cr, 4*woff+sbar_loc[0]+woff*scale_ratio, stxt_loc[1]*(1+0.01*hoff));
  cairo_line_to(cr, 4*woff+sbar_loc[0]+woff*imsz[0]*0.75*scale_ratio, stxt_loc[1]*(1+0.01*hoff));
  cairo_stroke(cr); // horz
  
  cairo_move_to(cr, 4*woff+sbar_loc[0]+woff*imsz[0]*0.75*scale_ratio, stxt_loc[1]-hoff*imsz[1]*scale_ratio*0.08);
  cairo_line_to(cr, 4*woff+sbar_loc[0]+woff*imsz[0]*0.75*scale_ratio, stxt_loc[1]*(1+0.01*hoff));
  cairo_stroke(cr); // rightv
}

void newFig(float imsz[4], float sshift[4], cairo_t*cr)
{

  /* figure background
   */
  cairo_set_source_rgb (cr, 0.3, 0.3, 0.3);
  cairo_rectangle (cr, 0., 0., imsz[0], imsz[1]);
  cairo_fill (cr); // fill grey background
  
  cairo_set_source_rgb (cr, 1., 1., 1.);
  cairo_set_line_width (cr, 10.0);
  cairo_rectangle (cr, sshift[0], sshift[1], sshift[2]-sshift[0], sshift[3]-sshift[1]);
  cairo_fill (cr); // fill black background
  
  // scale bar
  plotScaleBar(imsz, sshift, cr);
}

void cairo_writePNG(std::string fn)
{
  printf("writing to png (cairo)...%s\n",fn.c_str());
  cairo_surface_write_to_png(csurf, fn.c_str());
}

static void clear_surface (void)
{
  cairo_t *cr;
  cr = cairo_create (gtk_cairo_surf);
  cairo_set_source_rgb (cr, 1, 1, 1);
  cairo_paint (cr);
  cairo_destroy (cr);
}

static void cairo_GridImagePlot(GtkWidget *widget,
				cairo_t *cr,
				gpointer data)
{
  cairo_set_tolerance(cr, 0.8); // higher=performance, lower=quality; default is 0.1
  gint width, height;
  gtkGridData* gdat;
  gdat = (struct gtkGridData *)(data);
  width = (gint)gdat->w;
  height = (gint)gdat->h;
  csurf = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height);
  cairo_t* cr1 = cairo_create(csurf);
  cairo_set_source_surface(cr1, csurf, 0, 0);
  cairo_paint(cr1);
  cairo_set_tolerance(cr1, 0.8); // higher=performance, lower=quality; default is 0.1
  
  float imsz[4] = { (float)width, (float)height, 0, 0};
  float sshift[4] = { imsz[0]*image_offset_factor, imsz[1]*image_offset_factor,
		      imsz[0]-imsz[0]*image_offset_factor, imsz[1]-imsz[1]*image_offset_factor }; // sshift init
  
  /* Individual Plot Functions */

  newFig(imsz, sshift, cr1);
  plotRoads(cr1, gdat->mvec, imsz, sshift);
  plotGrid(cr1, gdat->gvec, imsz, sshift);
  plotStart(cr1, gdat->startpt, imsz, sshift);
  plotCounties(cr1, gdat->counties, imsz, sshift);
  plotScaleBar(imsz, sshift, cr1);
  cairo_writePNG(gdat->fn);
  cairo_destroy(cr1);
  if(csurf)
    {
      cairo_surface_destroy(csurf);
    }
  pi = 1;
}

static void gtk_paintGrid(GtkWidget *widget,
			  cairo_t *cr,
			  gpointer data) // called when canvas is drawn
{
  if(gtk_cairo_surf)
    cairo_surface_destroy(gtk_cairo_surf);
  
  if(pi==0)
    {
      cairo_GridImagePlot(widget, cr, data);
    }

  cairo_set_tolerance(cr, 0.8); // higher=performance, lower=quality; default is 0.1
  gint gwidth, gheight;
  gtkGridData* gdat;
  gdat = (struct gtkGridData *)(data);
  gwidth = (gint)gdat->w;
  gheight = (gint)gdat->h;
  gtk_cairo_surf = cairo_image_surface_create_from_png(gdat->fn.c_str());
  cairo_set_source_surface(cr, gtk_cairo_surf, 0, 0);
  cairo_paint(cr);
  gtk_widget_queue_draw (widget);
}

#endif
