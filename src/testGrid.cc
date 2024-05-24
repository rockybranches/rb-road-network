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

  start_pt[0] = home_pt[0];
  start_pt[1] = home_pt[1];
  
  float mstart[2] = {start_pt[0], start_pt[1]};
  mercator(mstart);
  printCoord(start_pt,"lat,long start:");
  printCoord(mstart,"mercator of start:");

  bool pflag = true;
  float radius = 30e3, mindist=0.01;
  int nthreads = 1;
  float stride[2]={0.1,0.1};
  char *rw = "w";
  std::string fn_shp =  RB_ROADNETWORK_PATH + std::string("data/gis_osm_roads/gis_osm_roads_free_1.shp"); 
  
  int c;
  int digit_optind = 0;

  while(1)
    {
      int this_option_optind = optind ? optind : 1;
      int option_index = 0;
      static struct option long_options[] = { {"radius", required_argument, 0, 'r'},
					      {"stride", required_argument, 0, 's'},
					      {"rw",     required_argument, 0, 'w'},
					      {"shpfile",required_argument, 0, 'f'},
					      {"nthreads",required_argument, 0, 'h'},
					      {"plot",no_argument,0,'p'},
					      {"nplot",no_argument,0,'n'}};

      c = getopt_long(argc, argv, "r:s:w:f:p", long_options, &option_index);

      if(c==-1)
	break;

      switch(c) {
      case 'r':
	radius = (float)atof(optarg);
	break;
      case 's':
	mindist = (float)atof(optarg);
	stride[0] = stride[1] = mindist;
	break;
      case 'w':
	rw = optarg;
	break;
      case 'f':
	fn_shp = RB_ROADNETWORK_PATH + std::string(optarg);;
	break;
      case 'h':
	nthreads = atoi(optarg);
	break;
      case 'p':
	pflag = true;
	break;
      case 'n':
	pflag = false;
	break;
      case '?':
	break;
      default:
	printf("?? incorrect options, char code returned: 0%o ??\n",c);
      }
    }
  
  float marr[4]={0,0,0,0};
  std::vector<PointRoad> rpvec;

  printf("radius=%.4f , mindist=%.4f , rw=%s , nthreads=%d\n",radius,mindist,rw,nthreads);
  printf("shpfile=%s\n", fn_shp.c_str());

  printf("opening shp...\n");
  rpvec = openSHP(mstart, radius, mindist, marr, fn_shp);
  printArea(marr);
  // mstart[0] = 0.5; mstart[1] = 0.5;
  normalize_pt(mstart,marr);
  printCoord(mstart,"normalized start=");

  extra_pt[0] = krog_pt[0]; extra_pt[1] = krog_pt[1];
  mercator(extra_pt);
  normalize_pt(extra_pt,marr);
  printCoord(extra_pt,"normalized extra point (krog)=");

  ex2[0] = rocky_b[0]; ex2[1] = rocky_b[1];
  mercator(ex2);
  normalize_pt(ex2,marr);
  printCoord(ex2,"normalized 2nd extra point (evans)=");

  gtkGridData gd;
  printf("gridding...\n");
  if(nthreads > 1)
    {
      printf("nthreads = %d\n",nthreads);
      GridMT grid(stride,marr,rpvec,nthreads);
      grid.gridRoads();
      grid.calcAvailability();
      gd.grid = grid;
    }
  else
    {
      Grid grid(stride,marr,rpvec);
      grid.gridRoads();
      gd.grid = grid;
    }
  gd.startpt[0] = mstart[0]; gd.startpt[1] = mstart[1];

  if(pflag){
    printf("plotting...\n");
  GtkApplication *app = gtk_application_new("test.gridplot", G_APPLICATION_FLAGS_NONE);
  g_signal_connect (app, "activate", G_CALLBACK (activate), &gd);
  int status;
  status = g_application_run (G_APPLICATION (app), NULL, NULL);
  g_object_unref (app);
  return status;
  }
  return 0;
}
