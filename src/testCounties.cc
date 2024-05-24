#include <gtk/gtk.h>
#include "utils.hpp"
#include "grid.hpp"
#include "places.hpp"
#include "plot.hpp"
#include "gui.hpp"
#include <stdio.h>
#include <getopt.h>
#include <fstream>
#include <iostream>
#include <ctime>
#include <string>

int main(int argc, char*argv[])
{

  std::time_t utres = std::time(nullptr);
  std::string dbfn = RB_DATA_PATH + "/" + "debug-" + std::to_string(utres) + ".log";
  std::ofstream debug_file(dbfn);
  freopen(dbfn.c_str(),"w+",stdout);

  mod_stack();
  
  bool pflag = true;

  // set default start point
  float rocky_b[2] = {-82.1472484, 33.5562623}; // evans home
  float decatur_pt[2] = {-84.275, 33.781}; // decatur apt
  float elberton_pt[2] = {-82.874, 34.0998}; // center of Elberton GA
  start_point[0] = decatur_pt[0]; start_point[1] = decatur_pt[1];
  mercator(start_point);
  
  int c;
  int digit_optind = 0;

  while(1)
    {
      int this_option_optind = optind ? optind : 1;
      int option_index = 0;
      static struct option long_options[] = { {"radius", required_argument, 0, 'r'},
					      {"stride", required_argument, 0, 's'},
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
	stride[0] = stride[1] = (float)atof(optarg);
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

  printf("started testCounties...\n");
  
  loadCountySHP(start_point, radius, zoom, stride[0],RB_DATA_PATH + "/tl_2016_us_county/" + "tl_2016_us_county.shp");
  counties.at(0).print_county();
  counties.at(1).print_county();
  return 0;
}
