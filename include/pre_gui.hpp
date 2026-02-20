#ifndef PRE_GUI_H
#define PRE_GUI_H

#include <stdio.h>
#include <iomanip>
#include <sstream>
#include <iostream>
#include <exception>
#include <functional>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>

#include "threadpool.hpp"
#include "rbtypes.hpp"
#include "utils.hpp"
#include "places.hpp"
#include "grid.hpp"

#include "spdlog/spdlog.h"

#ifndef _TESTRB
#include "plot.hpp"
#define GTK_GRIDDATA_P(gdat) reinterpret_cast<gtkGridData*>(gdat)
#endif

#if defined(_THRUSTRB) && (_THRUSTRB==true||_THRUSTRB==1)
#include "thrust_rb.hpp"
#endif

class PreGuiProcessor {
public:
  float radius = 20e3;
  float zoom = 0.5;
  PointRB stride;
  PreGuiProcessor();
  PreGuiProcessor(float rd, float z, PointRB s);
  PreGuiProcessor(float rd, float z, PointRB s, std::string imfn);
  void process(bool*,auto**);
  void loadRoads(bool*,auto**);
  bool done = false;
  std::vector<PointRB> availablePoints;
  json r2pJSON;
private:
  States* states;
  GridMT* gridc;
  int ncalc = 0;
  float areap = 1, areac = 1, availerr=100;
  void gridCalc();
  ThreadPool threadpool;
  std::vector<std::thread> threads;
  mutable std::mutex main_m;
  std::condition_variable dcond_m;
  std::string image_fn;
};

PreGuiProcessor::PreGuiProcessor()
{
  states = new States();
}

PreGuiProcessor::PreGuiProcessor(float rd, float z, PointRB s, std::string imfn): radius(rd), zoom(z), stride(s), image_fn(imfn)
{
  spdlog::debug("constructing PreGuiprocessor with a new States instance...");
  states = new States();
}

void PreGuiProcessor::loadRoads(bool*road_params_changed, auto** gdat)
{
  std::cout << "PreGuiprocessor::loadRoads()..." << std::endl;
  if(*road_params_changed)
    {
      std::vector<std::string> stnames = states->get_names();
      std::vector<Polygon<>> stbounds = states->get_bounds();
      // load roads
      ar_f larr;
      marr.toarr(larr);
      rpvec = openSHP(start_point, radius, zoom, stride[0], larr,
		      stnames, stbounds, shapefn);
      std::cout << "--> Larr= [ " << larr[0] << "," << larr[1] << ","
		<< larr[2] << "," << larr[3] << " ]" << std::endl;
      marr = AreaRB(larr);
#ifndef _TESTRB
      if(gdat)
	{
	  (*gdat) = GTK_GRIDDATA_P(*gdat);
	  (*gdat)->mvec = normalize_pts(rpvec, marr);
	}
#endif
      // load counties
      std::string county_data_path = (fs::path(RB_DATA_PATH) / "tl_2016_us_county/tl_2016_us_county.shp").string();
      std::cout << "county_data_path (pre_gui): " << county_data_path << std::endl;
      loadCountySHP(start_point.data(), radius, zoom, stride[0], county_data_path);
#ifndef _TESTRB
      if(gdat)
	(*gdat)->counties = counties;
#endif
    }
  std::cout << "--> marr= [ " << marr[0] << "," << marr[1] << "," << marr[2] << "," << marr[3] << " ]" << std::endl;
  std::cout << "rpvec.size = " << rpvec.size() << std::endl;
  std::cout << "done with loadRoads." << std::endl;
  (*road_params_changed) = false;
}

void PreGuiProcessor::gridCalc()
{
  try
    {	
      std::unique_lock lk(main_m);
      srand(time(0));
      (*gridc).calcAvailability();
      this->areac = (*gridc).availArea();
      lk.unlock();
      dcond_m.notify_one();
      std::this_thread::yield();
      if(ncalc > 0)
	{
	  lk.lock();
	  availerr = stride[0]*std::abs(areac - areap);
	  areap = areac;
	  std::cout << "Availability error = " << availerr << std::endl;
	  lk.unlock();
	}
      dcond_m.notify_all();
      std::this_thread::yield();
      lk.lock();
      ncalc++;
      lk.unlock();
      dcond_m.notify_all();
      std::this_thread::yield();
    }
  catch (const std::exception& excep)
    {
      std::cout << "(thread " << std::this_thread::get_id() << ")"
		<< " Error in Grid.calcAvailability() : "
		<< excep.what() << std::endl;
    }
}

void PreGuiProcessor::process(bool*road_params_changed, auto** gdat)
{
  std::cout << "PreGuiprocessor::process..." << std::endl;
#ifndef _TESTRB
  if(gdat)
    (*gdat) = GTK_GRIDDATA_P(*gdat);
#endif  
  // load the roads vector for area
  loadRoads(road_params_changed, gdat);
  // grid computations
  ar_f larr = {0};
  marr(larr);
#if !defined(_THRUSTRB) || (_THRUSTRB==0)
  GridMT gridl = GridMT(stride,larr,rpvec,nthreads);
#elif defined(_THRUSTRB) && (_THRUSTRB==1)
  GridThrust gridl(stride, larr, rpvec, nthreads);
#endif
  gridl.gridRoads();
  gridl.calcAvailability();
  for(GridRect& gr: gridl.grid){
    if(gr.avail)
      availablePoints.push_back(gr.med);
  }
  PointRB startpt(start_xydeg[0], start_xydeg[1]);
  r2pJSON = mapFeatures2GeoJSON(startpt, availablePoints);
  std::cout << "done with grid computations" << std::endl;
#ifndef _TESTRB
  if(gdat)
    {
      (*gdat)->mvec = gridl.mvec;
      (*gdat)->gvec = gridl.grid;
    }
#endif
  std::cout << "calculating county availability..." << std::endl;
  // calculate county availability
  for(County& county: counties){
    county.calc_county_availability(gridl);
    if(county.avail)
      county.print_county();
  }
  std::cout << "done with county computations." << std::endl;
  std::cout << "creating gridimg..." << std::endl;
  // compute, export grid image
  GridImage gridimg(gridl, zoom);
  std::string user_str = std::string(std::getenv("USER"));
  if(user_str == "www-data")
    user_str = "rocapp";
  gridimg.exportPNG(image_fn);
#ifndef _TESTRB
  if(gdat)
    (*gdat)->counties = counties;
    std::cout << "done with county computations" << std::endl;
#endif
  done = true;
  std::cout << "done with processor.process()\n" << std::endl;
}

#endif
