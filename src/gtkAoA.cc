#include <gtk/gtk.h>
#include <stdio.h>
#include <getopt.h>
#include <fstream>
#include <iostream>
#include <ctime>
#include <string>
#include "rbtypes.hpp"
#include "utils.hpp"
#include "grid.hpp"
#include "plot.hpp"
#include "gui.hpp"

int main(int argc, char*argv[])
{

  std::time_t utres = std::time(nullptr);
  std::string dbfn = RB_DATA_PATH + "/" + "debug-" + std::to_string(utres) + ".log";
  std::ofstream debug_file(dbfn);
  std::streambuf *coutbuf = std::cout.rdbuf();
  std::cout.rdbuf(debug_file.rdbuf());
  freopen(dbfn.c_str(),"a+",stdout);
  std::cout << "Debug Log File: " << dbfn << std::endl;

  start_coord = start_coord("start_elberton");
  std::cout << "Default start_coord: ";
  start_coord.print_coord();

  std::cout << "start_coord[0]=" << start_coord[0]
	    << " , start_coord[1]=" << start_coord[1] << std::endl;

  std::cout << "Default nthreads: " << nthreads << std::endl;
  
  bool pflag = true;
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
					      {"nplot",no_argument,0,'n'},
					      {"init_point",required_argument, 0, 'i'}
      };

      c = getopt_long(argc, argv, "pr:s:i:h:", long_options, &option_index);

      if(c==-1)
	break;

      switch(c) {
      case 'i':
	start_coord = global_coords(std::string(optarg));
	start_coord.name("start_"+start_coord.name());
	start_coord.print_coord();
        start_point = start_coord.merc();
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

  std::cout << "start_point = " << start_point[0]
	    << ", " << start_point[1] << std::endl;
  
  gdata = new gtkGridData();
  gdata->startpt[0] = start_point[0];
  gdata->startpt[0] = start_point[1];
  gtk_gui_start(600,600);
  delete gdata;
  
  return 0;
}
