#ifndef GRID_H
#define GRID_H

#include <fstream>
#include <math.h>
#include <stdio.h>
#include <iomanip>
#include <algorithm>
#include <functional>
#include <chrono>
#include <iostream>
#include <map>
#include <set>
#include "rbtypes.hpp"
#if defined(_THRUSTRB) && (_THRUSTRB==true||_THRUSTRB==1)
#include <thrust/execution_policy.h>
#include <thrust/host_vector.h>
#include <thrust/copy.h>
#include <thrust/scan.h>
#include <thrust/sequence.h>
#include <thrust/random.h>
#include <thrust/iterator/counting_iterator.h>
#include <thrust/functional.h>
#include <thrust/iterator/transform_iterator.h>
#include <thrust/transform_reduce.h>
#endif
#include "lodepng.h"
#include "utils.hpp"
#include "gridimg_utils.hpp"
#include <thread>
#include <mutex>
#include <condition_variable>
#include "threadpool.hpp"


/* 
   minimum griddistance for two gridrects to be considered adjacent 
*/
float MIN_GRID_DIST = 1.0;


struct GridRect {
  int nvisits=0; // number of times visited by pather
  float Lrwd[4]={0.0}; // grid pather reward accumulated (directional reward)
  int ix=-1; // Grid.grid index
  int iNx, iNy; // (gx, gy) grid coordinates
  PointRB iNxy; // (gx, gy) grid coordinates as PointRB
  int ny=-1; // number of vertical rects in grid (determines adjacency)
  float xr[2];
  float yr[2];
  float w, h;
  PointRB med; // center coordinate
  bool use=false; // contains a road?
  bool start=false; // contains start coord?
  bool avail=false; // is available within target road distance?
  bool cborder=false; // is part of a county border?
  std::string cname=""; // if part of county border, which county?
  bool clabel=false; // county label?
  bool cstart=false; // county contains start point?
  void calcmed()
  {
    med[0] = xr[0]+w/2.0;
    med[1] = yr[0]+h/2.0;
  }
  GridRect(int nry, float x[2], float y[2], int i): ix(i), ny(nry)
  {
    xr[0] = x[0]; xr[1] = x[1];
    yr[0] = y[0]; yr[1] = y[1];
    w = xr[1]-xr[0];
    h = yr[1]-yr[0];
    calcmed();
  }
  GridRect(int nry, float x0, float x1, float y0, float y1, int i): ix(i), ny(nry)
  {
    xr[0] = x0; xr[1] = x1;
    yr[0] = y0; yr[1] = y1;
    w = xr[1]-xr[0];
    h = yr[1]-yr[0];
    calcmed();
  }
  GridRect(int nry, float x0, float x1, float y0, float y1, int i, int inx, int iny):
    ny(nry), ix(i), iNx(inx), iNy(iny)
  {
    iNxy = PointRB(inx, iny);
    xr[0] = x0; xr[1] = x1;
    yr[0] = y0; yr[1] = y1;
    w = xr[1]-xr[0];
    h = yr[1]-yr[0];
    calcmed();
  }
  bool inRect(PointRB coord)
  {
    if(coord[0] < xr[0] || coord[0] > xr[1])
      return false;
    if(coord[1] < yr[0] || coord[1] > yr[1])
      return false;
    return true;
  }
  float gridDist(GridRect gr)
  {
    return lindist(iNxy, gr.iNxy);
  }
  bool isAdjacent(int grix, std::vector<GridRect>& gvec)
  {
    if(this->gridDist(gvec.at(grix)) <= MIN_GRID_DIST)
      return true;
    return false;
  }
  bool isAdjacent(GridRect& gr)
  {
    if(this->gridDist(gr) <= MIN_GRID_DIST)
      return true;
    return false;
  }
};

struct Road {
  int ix=-1; // corresponds to index of rpvec (non-normalized mercator-projected vector of roads)
  std::vector<int> ixs; // indices of GridRects (vector Grid.grid)
  Road(){}
  Road(std::vector<GridRect>& grid, PointRoad rd, int index): ix(index)
  {
    for(auto& pt: rd)
      {
	for(auto& gr: grid)
	  {
	    if(gr.inRect(pt.data())){
	      ixs.push_back(gr.ix);
	      gr.use = true;
	    }
	  }
      }
  }
#if defined(_THRUSTRB) && (_THRUSTRB==1||_THRUSTRB==true)
  typedef typename thrust::host_vector<GridRect> HostGridVect;
  Road(HostGridVect& grid, HostPointRoad rd, int index): ix(index)
  {
    for(auto& pt: rd)
      {
	for(auto& gr: grid)
	  {
	    if(gr.inRect(pt.data())){
	      ixs.push_back(gr.ix);
	      gr.use = true;
	    }
	  }
      }
  }
#endif
  bool inRoad(int gix)
  { // true if the GridRect corresponding to gix is in the Road, else false
    for(int& ix: ixs)
      {
	if(ix==gix)
	  return true;
      }
    return false;
  }
};
  
struct Block {
  int bix=-1; // block index
  float xy[2]; // center of block
  float rad; // radi of block
  std::vector<int> ixs; // GridRect indices within block
  int nr_use=0; // number of used GRs
  Block(int bi, float pblock, float r, std::vector<GridRect> grid): bix(bi)
  {
    int nr_blocks = (int)(pblock*(float)grid.size());
    int gix = (int)(((float)bi/nr_blocks)*(float)grid.size());
    rad = r*0.5*pblock;
    xy[0] = grid.at(gix).med[0];
    xy[1] = grid.at(gix).med[1];
    float r2d[2] = {rad, rad};
    for(GridRect& gr: grid)
      {
	if(withinArea(gr.med[0], gr.med[1], xy, r2d))
	  {
	    ixs.push_back(gr.ix);
	    if(gr.use)
	      nr_use+=1;
	  }
      }
    std::sort(ixs.begin(), ixs.end());
  }
};

typedef std::vector<GridRect> GridVector;
typedef std::vector<Road> RoadsVector;

class Grid {
public:
  float gradius;
  int start_ix;
  float strd[2];
  AreaRB area;
  PointRB mstart;
  int nx, ny;
  std::vector<Road> roads;
  std::vector<GridRect> grid;
  std::vector<PointRoad> mvec;
  std::vector<Block> blocks;
  float roadArea()
  {
    float ra=0.0;
    for(GridRect& gr: grid)
      {
	if(gr.use)
	  ra += gr.w*gr.h;
      }
    return ra;
  }
  float availArea()
  {
    float aa=0.0;
    for(GridRect& gr: grid)
      {
	if(gr.avail)
	  aa += gr.w*gr.h;
      }
    return aa;
  }
  Grid(){}
  Grid(PointRB s, AreaRB a, RoadStore rpvec)
  {
    mstart = start_point;
    mvec = rpvec;
    area = a;
    std::cout << "(Grid constructor, grid.hpp:212) | area= [ " <<
      area[0] << "," << area[1] << "," << area[2] << "," << area[3] << " ]" << std::endl;
    gradius = ((area[3])-(area[2]));
    if(s[0] >= 1 && s[1] >= 1)
      {
	strd[0]=s[0]; strd[1]=s[1];
      }
    else
      {
    	strd[0] = ((area[1])-(area[0]))*s[0];
    	strd[1] = ((area[3])-(area[2]))*s[1];
      }
    defineGrid();
  }
  void defineGrid()
  {
    int gi=0;
    nx = (int)((area[1]-area[0])/strd[0]);
    ny = (int)((area[3]-area[2])/strd[1]);
    for(int yi=0; yi < ny; yi++){
      for(int xi=0; xi < nx; xi++){
	float x0 = (area[0])+strd[0]*xi;
	float x1 = (area[0])+strd[0]*(xi+1);
	float y0 = (area[2])+strd[1]*yi;
	float y1 = (area[2])+strd[1]*(yi+1);
	int tmpyi = (ny-yi);
	if(tmpyi >= ny)
	  tmpyi = ny - 1;
	gi = nx*tmpyi + xi;
	grid.push_back(GridRect(ny,x0,x1,y0,y1,gi,xi,yi));
	if(grid.back().inRect(mstart))
	  {
	    grid.back().start = true;
	    start_ix = gi;
	    grid.back().avail = true;
	  }
      }
    }
    for(unsigned ii=0; ii < grid.size(); ii++){
      if(grid.at(ii).isAdjacent(start_ix, grid)){
	grid.at(ii).avail = true;
	break;
      }
    }
    std::cout << "nx=" << nx << " ny=" << ny << std::endl;
  }
  virtual void gridRoads()
  {
    auto start = std::chrono::high_resolution_clock::now();    
    for(int ri=0; ri < (int)mvec.size(); ri++)
      {
	roads.push_back(Road(grid, mvec.at(ri), ri));
	for(int& rx: roads.back().ixs)
	  {
	    grid.at(rx).use = true;
	  }
      }
    auto finish = std::chrono::high_resolution_clock::now();
    std::chrono::duration<float> elapsed = finish - start;
    std::cout << "(gridRoads()) time elapsed: " << elapsed.count() << std::endl;
  }
  int findClosestGridRect(pt_f pt)
  {
    std::pair<int, float> dp{-1,-1.0};
    for(const GridRect& gr : this->grid){
      float dnew = lindist(gr.med, pt);
      if(dnew < dp.second || dp.first==-1){
	dp = std::make_pair<int,float>((int)gr.ix, (float)dnew);
      }
    }
    return dp.first;
  }
  virtual void calcAvailability();
};

class GridPather {
public:
  int last_direction; // last direction chosen
  int directions[4]; // direction (E, W, N, S)
  float target_distance, path_distance=0.0;
  float max_step_size=1000.0; // maximum possible step size in a path
  PointRB loc; // current location of pather
  int start_index, current_index;
  std::vector<int> path; // path indices
  Grid* grid;
  mutable std::mutex trace_m;
  std::condition_variable tcond;
  GridPather(Grid* gd, float td, int start): target_distance(td), start_index(start)
  {
    srand(time(0));
    grid = gd;
    max_step_size = grid->strd[0] * td; // set maximum possible step size (relative to stride length)
    loc[0] = grid->grid.at(start).med[0];
    loc[1] = grid->grid.at(start).med[1];
    current_index = start;
    path.push_back(start);
    directions[0] = -grid->ny;
    directions[1] = grid->ny;
    directions[2] = -1;
    directions[3] = 1;
  }
  int chooseDirection()
  {
    int new_dir = rand() % 4;
    if(start_index==current_index)
      {
	last_direction = new_dir;
	return directions[new_dir];
      }
    GridRect* gr_start = &(grid->grid.at(start_index));
    GridRect* gr_cur = &(grid->grid.at(current_index));
    GridRect* gr_new;
    float L[4] = {0, 0, 0, 0};
    for(unsigned li=0; li < 4; li++)
      L[li] = 0.95*gr_cur->Lrwd[li]; // degradation of reward
    for(int di=0; di < 4; di++)
      {
	gr_new = &(grid->grid.at(current_index+directions[di]));
	if(current_index+directions[di] < (int)grid->grid.size() && (*gr_new).use)
	  {
	    L[di] += 3.0*(1.0+lindist(gr_new->med, gr_start->med));
	    L[di] -= 2.75*(1.0+lindist(gr_cur->med,gr_start->med));
	    L[di] += 3.0*target_distance / (1.0+gr_new->nvisits);
	    L[di] += 1.5*(float)(rand() % (int)(3.0*target_distance+1));
	  }
	else
	  {
	    L[di] = -5.0*target_distance;
	  }
      }
    for(unsigned li=0; li < 4; li++){ // update GridRect directional reward
      grid->grid.at(gr_cur->ix).Lrwd[li] += L[li];
      grid->grid.at(gr_cur->ix).Lrwd[li] /= 2.0;
    }
    int dx = 0;
    while(dx < 4)
      {
	if(L[dx] > L[new_dir])
	  new_dir = dx;
	dx++;
      }
    if(((1 + rand()) % 100) > 60){
      while(new_dir==last_direction)
	{
	  new_dir = rand() % 4;
	}
    }
    last_direction=new_dir;
    return directions[new_dir];
  }
  bool stepPath(int ix)
  {
    bool takestep = false;
    if(ix < (int)grid->grid.size())
      {
	if(grid->grid.at(ix).use && grid->grid.at(ix).isAdjacent(grid->grid.at(current_index)))
	  {
	    float stepdist = lindist(grid->grid.at(ix).med, loc);
	    float startdist = lindist(grid->grid.at(ix).med, grid->grid.at(start_index).med);
	    if(stepdist <= max_step_size && // limit the distance of a single step
	       path_distance+stepdist <= target_distance &&
	       startdist+stepdist <= target_distance)
	      {
		if(std::find(path.begin(), path.end(), ix)==path.end())
		  { // only step if gridrect[ix] not already in path
		    grid->grid.at(ix).nvisits += 1;
		    path_distance += stepdist;
		    loc[0] = grid->grid.at(ix).med[0];
		    loc[1] = grid->grid.at(ix).med[1];
		    current_index = ix;
		    path.push_back(ix);
		    takestep = true;
		  }
	      }
	  }
      }
    return takestep;
  }  
  void tracePath(int nfallowed=10)
  {
    try
      {
	int nfalses = 0;
	current_index = start_index;
	if(path.empty())
	  path.push_back(start_index);
	path_distance = 0.0;
	loc[0] = grid->grid.at(current_index).med[0];
	loc[1] = grid->grid.at(current_index).med[1];
	while(nfalses < nfallowed)
	  {
	    int newIndex = current_index + chooseDirection();
	    nfalses += (int)(!stepPath(newIndex));
	  }
      }
    catch(int excep_code)
      {
	std::cout << "Exception occurred with code: " << excep_code << std::endl;
      }
  }
  
  virtual std::vector<int> tracePaths(int npaths=10000)
  {
    auto start = std::chrono::high_resolution_clock::now();
    int ndone=0,ntry=0,nconst=0;
    std::vector<int> availperimeter;
    while(ndone < npaths && ntry < npaths*100 && nconst < (int)(50*npaths))
      {
	tracePath();
	int apsz = (int)availperimeter.size();
	if(path.size() > 0)
	  {
	    for(int& pth: path)
	      availperimeter.push_back(pth);
	    std::vector<int>().swap(path); // clear path
	    ndone++;
	  }
	if(apsz==(int)availperimeter.size())
	  nconst++;
	ntry++;
      }
    auto finish = std::chrono::high_resolution_clock::now();
    std::chrono::duration<float> elapsed = finish - start;
    std::cout << "(GridPather) time elapsed: " << elapsed.count() << std::endl;
    return availperimeter;
  }  
};


void Grid::calcAvailability()
{
  GridPather gpath(this, gradius, start_ix);
  int npaths = (int)(roads.size()*nx);
  std::vector<int> available = gpath.tracePaths(npaths);
  for(int& ia: available)
    {
      for(GridRect& gr: grid)
	{
	  if(gr.ix == ia)
	    gr.avail = true;
	}
    }
}


/*
  GridPatherMT class def
*/

class GridPatherMT : public GridPather {
public:
  int nthreads = 2;
  int nthreads_done = 0;
  std::vector<int> availperimeter;
  int ndone = 0;
  int ntried = 0;
  int max_ntried_thread = 1000;
  int npaths = 1000;
  std::function<void(int,int)> pathFunc = std::bind(&GridPatherMT::traceThreaded,this,
						    std::placeholders::_1,
						    std::placeholders::_2);
  std::vector<std::thread::id> threads_tried;
  GridPatherMT(Grid* gd, float td, int start, int nthreads): GridPather(gd, td, start), nthreads(nthreads)
  {
    if((int)threads.size() < nthreads)
      initThreads();
  }
  std::vector<int> tracePaths(int nths=1000)
  { // multithreaded override of tracePaths
    auto start = std::chrono::high_resolution_clock::now();
    npaths = nths;
    max_ntried_thread = (int)(npaths*nthreads);
    auto push_thread = [this](bool new_thread=false) {
      if(new_thread)
	threads.emplace_back(std::thread(&ThreadPool::loop_func, &this->threadpool));
      threadpool.push(std::bind(pathFunc,(int)(0.4*npaths/(float)nthreads),(int)(npaths/(float)(nthreads))));
    };
    for(int ti=0; ti < nthreads; ti++)
      push_thread(false);
    threadpool.done();
    std::unique_lock lock(main_m);
    for(int th=0; th < nthreads; th++)
	threads.at(th).join();
    lock.unlock();
    pcond.notify_all();
    lock.lock();
    pcond.wait(lock, 
    	       [this](){
    		 // bool all_tried = (ntried>=(max_ntried_thread*(nthreads-1)));
    		 return (ndone>=npaths) || (nthreads_done >= nthreads);
    	       });
    pcond.notify_all();
    auto finish = std::chrono::high_resolution_clock::now();
    std::chrono::duration<float> elapsed = finish - start;
    std::cout << "(GridPatherMT) time elapsed: " << elapsed.count() << std::endl;
    std::vector<std::thread>().swap(threads);
    return availperimeter;
  }
private:
  ThreadPool threadpool;
  std::vector<std::thread> threads;
  mutable std::mutex paths_m, main_m;
  std::condition_variable pcond;
  void initOneThread()
  {
    threads.emplace_back(std::thread(&ThreadPool::loop_func, &this->threadpool));
  }
  void initThreads()
  {
    for(int i=0; i < nthreads; i++)
      threads.emplace_back(std::thread(&ThreadPool::loop_func, &this->threadpool));
  }
  void traceThreaded(int nfallowed, int local_npaths)
  {
    if(ndone >= npaths)
      return;
    int local_ndone = 0;
    int local_ntried = 0;
    std::unique_lock lock0(paths_m);
    std::cout << "(thread" << std::this_thread::get_id() << ") "
	      << " started tracing..." << std::endl;
    lock0.unlock();
    while(true)
      {
	lock0.lock();
	tracePath(nfallowed);
	local_ntried++;
	lock0.unlock();
	lock0.lock();
	if(!path.empty())
	  {
	    for(int& pth: path)
	      availperimeter.push_back(pth);
	    std::vector<int>().swap(path); // clear path
	    local_ndone++;
	  }
	lock0.unlock();
	if(local_ndone >= local_npaths ||
	   ( (local_ntried > max_ntried_thread) )
	   )
	  {
	    std::lock_guard lg(paths_m);
	    std::cout << std::this_thread::get_id()
		      << " ...finished local_ndone or hit max number of trials.\n";
	    break;
	  }
      }
    if(ndone >= npaths) // haha! this was a fun one to fix... :P
      return;
    lock0.lock();
    ndone += local_ndone;
    ntried += local_ntried;
    threads_tried.push_back(std::this_thread::get_id());
    std::cout << "(thread" << std::this_thread::get_id() << ") "
	      << " ...finished tracing (local_ndone=" << local_ndone << ")" << std::endl;
    std::cout << " ...ndone = " << ndone << " of [ " << npaths << " (ntodo) ]" << std::endl;
    std::cout << " ...ntried = " << ntried << " of " << max_ntried_thread*(nthreads-1) << std::endl;
    nthreads_done += 1;
    lock0.unlock();
    pcond.notify_all();
    return;
  }
};


/*
  GridMT Class Def
*/

class GridMT : public Grid {
public:
  int nthreads = 2;
  int nthreads_done = 0;
  bool gdone = false;
  GridMT(PointRB s, AreaRB a, RoadStore v, int nt) :
    Grid(s, a, v), nthreads(nt) {}
  void gridRoads()
  { // multithreaded override of gridRoads
    auto start = std::chrono::high_resolution_clock::now();
    if(nthreads > (int)mvec.size())
      nthreads = 1;
    if((int)threads.size() < nthreads)
      initThreads();
    std::function<void(int)> appFunc = std::bind(&GridMT::appendRoad,this,std::placeholders::_1);
    for(int ti=0; ti < nthreads; ti++)
      {
	std::unique_lock lock(main_m);
	threadpool.push(std::bind(appFunc,ti));
	lock.unlock();
	dcond_m.notify_all();
      }
    std::unique_lock lock(main_m);
    threadpool.done();
    lock.unlock();
    lock.lock();
    for(int th=0; th < nthreads; th++)
	threads.at(th).join();
    dcond_m.notify_all();
    dcond_m.wait(lock, [this](){
	return ((int)roads.size()>=((int)mvec.size()-1)) || gdone;
      });
    std::cout << "done waiting on threads.\n";
    dcond_m.notify_all();
    std::vector<std::thread>().swap(threads); // empty threads vector    
    auto finish = std::chrono::high_resolution_clock::now();
    std::chrono::duration<float> elapsed = finish - start;
    std::cout << "(GridMT) time elapsed: " << elapsed.count() << std::endl;
  }
  void calcAvailability()
  {
    std::cout << "initializing grid pather(MT)" << std::endl;
    std::cout << "nthreads = " << nthreads << std::endl;
    GridPatherMT gpath(this, gradius, start_ix, nthreads);
    int npaths = (int)(nx*ny/(float)2.5);
    std::cout << "tracing " << npaths << " paths..." << std::endl;
    std::vector<int> available = gpath.tracePaths(npaths);
    std::set<int> unique_paths;
    unsigned usz = available.size();
    for(unsigned pi=0; pi < usz; pi++)
      unique_paths.insert(available.at(pi));
    available.assign(unique_paths.begin(), unique_paths.end());
    std::cout << available.size() << "unique paths traced." << std::endl;
    try {
      for(int& ia: available)
	{
	  for(GridRect& gr: grid)
	    {
	      if( gr.ix == ia && // Check: grid med should be within the map area.
		  lindist(grid.at(ia).med, grid.at(start_ix).med) <= (gradius) )
		{
		  gr.avail = true;
		  break;
		}
	    }
	}
    } catch(const std::exception& excep) {
      std::cout << "(excep line 558) Error in Grid.calcAvailability() : " << excep.what() << std::endl;
    }
    try {
      for(GridRect& gr: grid)
	{
	  if((!gr.avail) && gr.use)
	    {
	      int ngid = gr.ix;
	      int navail = 0;
	      for(int di=0; di < 4; di++)
		{
		  ngid = gr.ix + gpath.directions[di];
		  if( ngid < (int)grid.size() && ngid > 0 )
		    {
		      if(grid.at(ngid).use && grid.at(ngid).avail)
			navail++;
		    }
		  else
		    {
		      break;
		    }
		}
	      if(navail>=2)
		gr.avail = true;
	    }
	}
    } catch(const std::exception& excep) {
      std::cout << "(excep line 584) Error in Grid.calcAvailability() : " << excep.what() << std::endl;
    }
  }
  
private:
  ThreadPool threadpool;
  std::vector<std::thread> threads;
  mutable std::mutex main_m, roads_m, grid_m;
  std::condition_variable dcond_m;
  void initThreads()
  {
    printf("GridMT: init %d threads...\n",nthreads);
    for(int i=0; i < nthreads; i++)
      threads.emplace_back(std::thread(&ThreadPool::loop_func, &this->threadpool));
  }
  void setGridUse(int rx, bool flag)
  {
    if(rx < (int)grid.size())
      grid.at(rx).use = flag;
  }
  void appendRoad(int ri)
  {
    std::unique_lock lk(roads_m);
    if((int)roads.size()>=(int)mvec.size())
      return;
    std::cout << "appendRoad (threadID=" << std::this_thread::get_id() << ")" << std::endl;
    int rj0 = (int)((float)mvec.size()*(float)((float)ri/((float)nthreads)));
    int rj1 = (int)((float)mvec.size()*(float)((float)(ri+1)/((float)nthreads)))-1;
    std::cout << "(init) rj0=" << rj0 << ", rj1=" << rj1 << std::endl;
    if(rj1 <= 0)
      return;
    else if(rj0 >= rj1){
      int rjt = rj0;
      rj0 = rj1;
      rj1 = rjt;
    }
    else if(rj0 == rj1)
      rj0 = rj1 - 1;
    std::cout << "(fin) rj0=" << rj0 << ", rj1=" << rj1 << std::endl;
    int rj=rj0;
    lk.unlock();
    dcond_m.notify_one();
    while(rj <= rj1) // mark spot *
      {
	Road rd(grid, mvec.at(rj), rj);
	lk.lock();
	roads.push_back(rd);
	rj++;
	lk.unlock();
	dcond_m.notify_one();
      }
    dcond_m.notify_all();
    lk.lock();
    nthreads_done++;
    std::cout << "(thread=" << std::this_thread::get_id() << ")" << " ntdone=" << nthreads_done
	      << " | Nroads=" << (int)roads.size() << " of " << (int)mvec.size() << " (mvec.size)"
	      << std::endl;
    if(nthreads==nthreads_done)
      gdone = true;
    lk.unlock();
    dcond_m.notify_all();
    return;
  }
};


/*
  GridImage Class Def
*/

using namespace gim;

class GridImage {
  GlyphMap glyphs;
public:
  gimg image;
  unsigned h = 660;
  unsigned w = 660;
  float zoom = 0.5;
  GridImage(){}
  GridImage(Grid gridl,
	    float z=0.5,
	    unsigned wi=660,
	    unsigned hi=660):
    zoom(z), w(wi), h(hi)
  {
    zoom = zoom + 0.5;
    glyphs.loadGlyphs();
    std::vector<GridRect> grid = gridl.grid;
    unsigned gw = (unsigned)grid.at(0).ny;
    unsigned gh = gw;
    float wratio = gw / (float)(w);
    float hratio = gh / (float)(h);
    image.resize(w * h * 4);
    std::fill(image.begin(), image.end(), (unsigned)255);
    PointRB start_imloc;
    for(GridRect& gr : grid){
      if(gr.start){
	start_imloc = PointRB(gr.iNx/wratio, gr.iNy/hratio);
	break;
      }
    }
    std::vector<gword> gclabs;
    PointRoad goffs; // (xoff, yoff)
    std::vector<std::string> gstrs;
    for(unsigned r=0; r < h; r++){ // plot Grid
      for(unsigned c=0; c < w; c++)
	{
	  unsigned cg = c * wratio;
	  unsigned rg = r * hratio;
	  GridRect gr = grid.at((int)(rg*gw+cg));
	  GridImageLayers gil(gr.nvisits, gr.start, gr.use, gr.avail, false, gr.cborder);
	  gimg imc = gil.setupPixelLayers();
	  for(unsigned i=0; i < 4; i++)
	    image.at(4*(r*w+c)+i) = imc.at(i);
	  if(gr.clabel &&(std::find(gstrs.begin(), gstrs.end(), gr.cname)==gstrs.end()))
	    {
	      gstrs.push_back(gr.cname);
	      std::cout << "--> getting glyphs... (" << gr.cname << ")" << std::endl;
	      std::stringstream gstr;
	      if(gr.cstart){
		gstr << gr.cname
		     << " (" << std::fixed << std::setprecision(1) << start_xydeg[0] << "E,"
		     << std::fixed << std::setprecision(1) << start_xydeg[1] << "N)";
	      } else { gstr << gr.cname; }
	      gword cnvec = glyphs.getWordGlyphs(gstr.str());
	      gclabs.push_back(cnvec);
	      /* 
		 Auto-adjust text position
	      */
	      PointRB offxy = PointRB(c, r);
	      float gword_w=0,gword_h=(float)(cnvec.at(0).h);
	      for(auto& ggw : cnvec)
		{
		  gword_w += (float)ggw.w;
		}
	      while(true)
		{
		  AreaRB garea = AreaRB(offxy.x(), offxy.x()+gword_w,
					offxy.y(), offxy.y()+gword_h);
		  bool wia = withinArea(start_imloc.x(), start_imloc.y(), garea);
		  float cx = offxy.x();
		  float cy = offxy.y();
		  if(wia)
		    offxy.x(cx - 1);
		  if(offxy.x() + gword_w >= w && abs(offxy.x()+gword_w-w)<=gword_w/2.0)
		    {
		      offxy.x(cx - 1);
		    }
		  if(offxy.y() + gword_h >= h)
		    {
		      offxy.y(cy - 1);
		    }
		  wia = withinArea(start_imloc.x(), start_imloc.y(), garea);
		  if((offxy.x() + gword_w <= w || abs(offxy.x()+gword_w-w)>gword_w/2.0)
		     && offxy.y() + gword_h <= h && !(wia))
		    break;
		}
	      goffs.push_back(offxy);
	    }
	}
    }
    { /* Invert image */
      gimg gtmp(image);
      for(unsigned r=0; r < h; r++){
    	for(unsigned c=0; c < w; c++){
	  unsigned tmpix = h-r;
	  if(tmpix >= h)
	    tmpix = h-1;
    	  for(unsigned i=0; i < 4; i++)
    	    image.at(4*(r*w+c)+i) = gtmp.at(4*((tmpix)*w+c)+i);
    	}
      }
    }
    /* County names (set raster text) */
    for(unsigned j=0; j < (unsigned)gclabs.size(); j++){
      gword cnvec = gclabs.at(j);
      PointRB global_off = goffs.at(j);
      PointRB local_off(0, 0);
      for(auto cg : cnvec)
	{
	  for(unsigned r=0; r < cg.h; r++){
	    unsigned imr = global_off.y() + local_off.y() + r;
	    for(unsigned c=0; c < cg.w; c++){
	      unsigned imc = global_off.x() + local_off.x() + c;
	      Color ctmp(255, 255, 255, 200);
	      gimg gtmp;
	      for(unsigned j=0; j < 3; j++)
		ctmp.c[j] = cg.g.at(4*(r*cg.w+c)+j);
	      if(imr < h && imc > 0 && imc < w && 4*(imr*w+imc)+3 < image.size()){
		Color ctmp1(image.at(4*(imr*w+imc)),
			    image.at(4*(imr*w+imc)+1),
			    image.at(4*(imr*w+imc)+2),
			    image.at(4*(imr*w+imc)+3));
		gtmp = ctmp.setPixel(ctmp1.cv);
	      }
	      for(unsigned i=0; i < 4; i++)
		{
		  if((4*(imr*w+imc)+i < image.size()) &&
		     (4*(imr*w+imc)+i >= 0) &&
		     (imr > 0 && imr < h && imc > 0 && imc < w))
		    {
		      image.at(4*(imr*w+imc)+i) = gtmp.at(i);
		    }
		}
	    }
	  }
	  local_off[0] = local_off.x() + cg.w;
	}
    }
    std::cout << "...done creating GridImage.\n";
  }
  void exportPNG(std::string fn)
  {	
    unsigned error = lodepng::encode(fn, image, w, h);
    if(error)
      std::cout << "lodepng error " << error << std::endl;
    std::cout << "exported GridImage to PNG: " << fn << std::endl;
  }
};

#endif
