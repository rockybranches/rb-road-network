#ifdef _WIN32
#include <pthread.h>
#endif
#include <stdio.h>
#include <getopt.h>
#include <fstream>
#include <iostream>
#include <ctime>
#include <string>
#include <functional>
#include <experimental/array>
#include "rbtypes.hpp"
using namespace rb;
#include "utils.hpp"
#include "grid.hpp"
#include "pre_gui.hpp"
#include "thrust_rb.hpp"

int main(int argc, char*argv[])
{
  utres = std::time(nullptr);
  std::string dbfn =
    RB_DATA_PATH + "logs/" + "debug-" + std::string(std::getenv("USER")) +
    "-" + std::to_string(utres) + ".log";
  std::ofstream debug_file(dbfn);
#if defined(_RB_DEBUG) && (_RB_DEBUG == true || _RB_DEBUG == 1)
  std::cout << "Debug Log File: " << dbfn << std::endl;
#endif
  freopen(dbfn.c_str(),"a+",stdout);
  std::cout << "Debug Log File: " << dbfn << std::endl;

  /* default params */
  std::string tons_str = "4.5";
  std::string filename = "poptable" + std::to_string(utres) + ".txt";
  std::cout << "Default nthreads: " << nthreads << std::endl;
  std::cout << "Default output filename: " << filename << std::endl;
  float zoom = 0.5;
  float radius = 20e3;
  PointRB stride(0.007, 0.007);
  
  int c;
  int cmd_coords = 0;

  while(1)
    {
      int option_index = 0;
      static struct option long_options[] = { {"radius", required_argument, 0, 'r'},
					      {"stride", required_argument, 0, 's'},
					      {"nthreads",required_argument, 0, 'h'},
					      {"init_point",required_argument, 0, 'i'},
					      {"tons-per-person",required_argument, 0, 't'},
					      {"output-file-path",required_argument, 0, 'f'},
					      {"lat",required_argument,0,'a'},
					      {"lon",required_argument,0,'b'},
					      {"zoom",required_argument,0,'z'}
      };

      c = getopt_long(argc, argv, "r:s:i:h:t:f:a:b:z:", long_options, &option_index);
      
      if(c==-1)
	break;

      switch(c) {
      case 'z':
	zoom = (float)std::atof(optarg);
	std::cout << "zoom set (cmd) = " << zoom << std::endl;
	break;
      case 'b':
	start_point[0] = (float)std::atof(optarg);
	cmd_coords = 1;
	break;
      case 'a':
	start_point[1] = (float)std::atof(optarg);
	cmd_coords = 1;
	break;
      case 'i':
	start_coord = global_coords(std::string(optarg));
	start_coord.name("start_"+start_coord.name());
	start_coord.toarr(start_xydeg);
	start_coord.merc().toarr(start_point.data());
	start_coord.print_coord();
	std::cout << "from cmd args: start_point = " << start_point[0]
	    << ", " << start_point[1] << std::endl;
	cmd_coords = 2;
	break;
      case 'r':
	radius = (float)atof(optarg);
	break;
      case 's':
	stride[0] = stride[1] = (float)atof(optarg);
	std::cout << "stride set (cmd) = " << stride[0] << std::endl;
	rb::assert_msg(stride[0]==(float)atof(optarg), "(PointRB Error!) Stride was not properly set!");
	break;
      case 'h':
	nthreads = atoi(optarg);
	break;
      case 't':
	tons_str = std::string(optarg);
	break;
      case 'f':
	filename = std::string(optarg);
	std::cout << "output filename set: " << filename;
      case '?':
	break;
      default:
	printf("?? incorrect options, char code returned: 0%o ??\n",c);
      }
    }

  if(cmd_coords==1){
    start_xydeg[0] = start_point[0];
    start_xydeg[1] = start_point[1];
    start_point = mercator(std::experimental::make_array(start_point[0], start_point[1]));
  } else if (cmd_coords==0)
    {
      start_coord = start_coord("start_elberton");
      start_coord.toarr(start_xydeg);
      start_coord.merc().toarr(start_point.data());
      std::cout << "Default start_coord: ";
      start_coord.print_coord();
      std::cout << "start_coord[0]=" << start_coord[0]
		<< " , start_coord[1]=" << start_coord[1] << std::endl;
      std::cout << "start_point = " << start_point[0]
		<< ", " << start_point[1] << std::endl;
    }
  use_GL = false;
  // check that radius is big enough (should be in meters)
  rb::assert_msg((radius >= 1e3), "Queried road distance was less than the minimum supported (>=1km).");
  PreGuiProcessor* processor = new PreGuiProcessor(radius, zoom, stride);
  bool road_params_changed = true;
  processor->done = false;
  auto pholder = NULL;
  auto* ppholder = &pholder;
  processor->process(&road_params_changed, &ppholder );
  std::time_t tf = std::time(nullptr);
  std::cout << "Done! Computation took " << std::setprecision(3) << std::difftime(tf, utres) << " seconds.\n";
  fclose(stdout);
#ifdef _WIN32
  pthread_exit(NULL);
#endif
  
  return 0;
}
