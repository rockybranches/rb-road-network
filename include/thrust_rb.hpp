#ifndef THRUST_RB_HPP
#define THRUST_RB_HPP
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
#include "rbtypes.hpp"
#include "utils.hpp"
#include "grid.hpp"

typedef typename thrust::host_vector<Road> HostRoadVect;
typedef typename thrust::host_vector<GridRect> HostGridVect;

class GridThrust : public GridMT {
public:
  int nGPUthreads = (int)1e5;
  GridThrust(PointRB s, AreaRB a, RoadStore v, int nt, int gnt) :
    GridMT(s, a, v, nt), nGPUthreads(gnt) {}
  GridThrust(PointRB s, AreaRB a, RoadStore v, int nt) :
    GridMT(s, a, v, nt) {}
  void gridRoads();
  struct gridRoads_thrust : public thrust::unary_function<int,Road>
  {
    /*
      This Thrust functor initializes the Grid.roads vector [ Roads(grid, mvec.at(ri), ri) ],
      then applies the operation (set GridRect.use = true) [ grid.at(road_index) = true ]
      for GridRects in the vector Grid.grid that contain a road.
     */
    HostGridVect grid_local;
    HostRoadStore mvec_local;
    __host__ gridRoads_thrust(GridVector gd, RoadStore mv):
      grid_local(gd), mvec_local(mv) {}
    __host__ Road operator()(int mvix)
    {
      return Road(grid_local, mvec_local[mvix], mvix);
    }
  };
};

void GridThrust::gridRoads()
{ // GPU-based override of gridRoads. (Uses Thrust, the CUDA OOP library)
  std::cout << "(GridThrust)::gridRoads() started..." << std::endl;
  auto start = std::chrono::high_resolution_clock::now();
  roads = RoadsVector(mvec.size());
  gridRoads_thrust gr_init(grid, mvec);
  thrust::tabulate(thrust::host, roads.begin(), roads.end(), gr_init); // init roads vector
  grid.assign(gr_init.grid_local.begin(), gr_init.grid_local.end());
  auto finish = std::chrono::high_resolution_clock::now();
  std::chrono::duration<float> elapsed = finish - start;
  std::cout << "(GridThrust) time elapsed: " << elapsed.count() << std::endl;
}


#endif
