#include <gtk/gtk.h>
#include "graph.hpp"
#include "utils.hpp"
#include "grid.hpp"
#include "plot.hpp"
#include <stdio.h>
#include "ogrsf_frmts.h"
#include <getopt.h>

int main(int argc, char* argv[])
{
  GDALAllRegister();  

  float rami_pt[2] = { -84.317, 34.7425 }; // rami's house
  float knox_pt[2] = { -84.508419, 34.220352 }; // Knox bridge road start coord
  float krog_pt[2] = { -84.275567, 33.791907 }; // Kroger (N Decatur)
  float home_pt[2] = { -84.2774617, 33.781112 }; // apartment
  float studio_pt[2] = { -81.964405, 31.9178347 }; // studio 178 hair salon (Glennville, GA)
  float montrose_pt[2] = {-83.1604122, 32.5570586};
  float rocky_b[2] = {-82.1472484, 33.5562623}; // evans home
  float road_p[2] = {-84.389964,33.744926}; // center of Atl
  float start_pt[2];

  start_pt[0] = road_p[0];
  start_pt[1] = road_p[1];

  printf("(mercator) rb->apt = %.4f km\n",mercdist(rocky_b, home_pt)/1e3);
  printf("(vincenty) rb->apt = %.4f km\n",vincenty(rocky_b[0], rocky_b[1], home_pt[0], home_pt[1])/1e3);
  
  float mstart[2] = {start_pt[0], start_pt[1]};
  mercator(mstart);
  printCoord(start_pt,"lat,long start:");
  printCoord(mstart,"mercator of start:");

  float radius = 20e3, mindist=10;
  int nthreads = 1;
  float stride[2]={0.1,0.1};
  char *rw = "w";

  if(argc > 1)
    {
      radius = (float)atof(argv[1]);
    }
  if(argc > 2)
    {
      mindist = (float)atof(argv[2]);
      stride[0] = (float)atof(argv[2]);
      stride[1] = (float)atof(argv[2]);
    }
  if(argc > 3)
    {
      printf("%s\n",argv[3]);
      rw = argv[3];
    }
  if(argc > 4)
    {
      nthreads = atoi(argv[4]);
    }

  
  float marr[4]={0,0,0,0};
  std::vector<PointRoad> rpvec;

  printf("radius=%.4f , mindist=%.4f , rw=%s\n",radius,mindist,rw);

  std::string fn_shp = std::string(std::getenv("RBPATH")) + "DQ_area_roads.shp";

  printf("opening shp...\n");
  rpvec = openSHP(mstart, radius, mindist, marr);
  printArea(marr);
  find_closest_pt(mstart, mstart, rpvec);
  normalize_pt(mstart,marr);
  printCoord(mstart,"normalized start=");

  printf("plotting...\n");
  gtkMercData md;
  md.startpt[0] = mstart[0]; md.startpt[1] = mstart[1];
  md.mvec = normalize_pts(rpvec,marr);

  GtkApplication *app = gtk_application_new("test.mercplot", G_APPLICATION_FLAGS_NONE);
  g_signal_connect (app, "activate", G_CALLBACK (activate), &md);
  int status;
  status = g_application_run (G_APPLICATION (app), NULL, NULL);
  g_object_unref (app);

  return status;
}
