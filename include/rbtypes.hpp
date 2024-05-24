/*

  Type definitions common to all RB modules

  09/13/2019 : Robert Ahlroth Capps


  Conventions/Notes:
  - Coordinates are stored as (X,Y)/(East,North)/(Long,Lat) despite the fact that "lat/long" sounds better verbally.
  - Areas are defined as (Xmin, Xmax, Ymin, Ymax)... i.e. Xmin = min(X), which is the numerical minimum, not always
  the southernmost/"bottom" point spatially.

*/

#ifndef RBTYPES_H
#define RBTYPES_H
#include <csignal> // insert breakpoint -- std::raise(SIGINT) -- signal interrupt
#include <iostream>
#include <fstream>
#include <math.h>
#include <stdio.h>
#include <algorithm>
#include <vector>
#include <cmath>
#include <cctype>
#include <unordered_map>
#include <initializer_list>
#include <locale>
#include <experimental/filesystem>

/* experimental filesystem namespace */
namespace fs = std::experimental::filesystem;

#include <experimental/array> // to_array(), make_array() functions in c++2a (C++20)
#include "lodepng.h"
void insert_breakpoint();
#if defined(_RB_DEBUG) && (_RB_DEBUG == true || _RB_DEBUG == 1)
void insert_breakpoint()
{
  std::cout << "--- Encountered breakpoint: Raise SIGINT --- " << std::endl;
  std::raise(SIGINT);
}
#else
void insert_breakpoint() {}
#endif

#ifdef _USEGL
#include <GL/glew.h>
#include <GL/glu.h>
#endif

#include <assert.h>
#undef assert
#define assert(condition, message)\
  (!(condition)) ?\
  (std::cerr << "Assertion failed: (" << #condition << "), "\
  << "function " << __FUNCTION__\
  << ", file " << __FILE__\
  << ", line " << __LINE__ << "."\
   << std::endl << message << std::endl, abort(), 0) : 1




/* RB Point Macros */
#define PtTemplate template<class PointType=BasePoint>
#define PtType Point<PointType>

/* Points in RB rely on an internal std::array<float,2>. */
typedef std::array<float,2> BasePoint;
typedef std::array<float,4> BaseArea;

/*
  Forward declarations of templates, classes, funcs (involving rb::Point, rb::Area, etc)
*/
PtTemplate class Point;
struct Area;
// PtTemplate inline PtType mercator(PtType coord);
inline BasePoint mercator(BasePoint coord);
inline BasePoint sinusoidal(BasePoint coord);
PtTemplate inline PtType p2merc(PtType& cout, float l, float p);
PtTemplate inline PtType p2sinusoid(PtType& pout, float l, float p);
PtTemplate inline void printCoord(PtType coord, std::string extra="");
PtTemplate inline PtType normalize_pt(PtType pt, Area area);
PtTemplate inline float lindist(PtType c0, PtType c1);
inline void invmercator(float x, float y, float coord[2]);
inline void invsinusoidal(float x, float y, float coord[2]);

namespace rb {  
  /*
    assert with message
  */    
  void assert_msg(bool condition, std::string message);
  void assert_msg(bool condition, std::string message)
  {
    assert(condition, message);
  }

  /* numerical constant value for pi, macro def */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif
  
  /* aliases to convert from float* correctly */
  using pt_f = float[2];
  using ar_f = float[4];

  /* Area type definition -- RB */
  typedef struct Area {
    BaseArea a = {0}; // (Xmin, Xmax, Ymin, Ymax) * keep in mind, this is the numerical min()/max() *
    Area() {}
    Area(float xmin, float xmax, float ymin, float ymax)
    { a[0] = xmin; a[1] = xmax; a[2] = ymin; a[3] = ymax; }
    // construct Area from initializer list ( e.g. {0.1, 0.9} )
    Area(std::initializer_list<float> Al)
    { std::copy(Al.begin(), Al.end(), a.data()); }
    // constructor (float*) -> To: Area
    Area(ar_f af) { std::copy(af, af+4, a.data()); }
  
    // (Area = Area) (overloaded assignment operator)
    Area& operator = (const Area & A)
    { for(int ai=0; ai < 4; ai++) this->a[ai] = A[ai]; return (*this); }
  
    // float* -> Area (assignment operator)
    Area& operator = (const float* &Af)
    { for(int ai=0; ai < 4; ai++) this->a[ai] = Af[ai]; return (*this); }
    Area& operator = (const ar_f &Af)
    { for(int ai=0; ai < 4; ai++) this->a[ai] = Af[ai]; return (*this); }

    // cast operator overloads
    operator float*() // cast to float pointer
    {
      return this->a.data();
    }

    // access operator overloads (get, set)
    float operator[] (int ai) const { return a[ai]; }
    float& operator[] (int ai) { return a[ai]; }

    // in-place call pointer-to-array operator overload : ( e.g. Area marr; ar_f Af; marr(Af); )
    void operator() (ar_f Af)
    { for(int ai=0; ai < 4; ai++) Af[ai] = this->a[ai]; }

    // helper funcs
    auto begin() { return a.begin(); }
    auto end() { return a.end(); }
    float* data() { return a.data(); }   // to access underlying point array
    void toarr(ar_f aout) { for(int ai=0; ai < 4; ai++) aout[ai] = a[ai]; }
    bool withinArea(float x, float y)
    {
      if(x < a[0])
	return false;
      if(x > a[1])
	return false;
      if(y < a[2])
	return false;
      if(y > a[3])
	return false;
      return true;
    }
  } Area;
  typedef rb::Area AreaRB;

  /* 
     Point type definition -- RB
  */
  PtTemplate
  class Point {
  public:
    BasePoint parr = {-12,-12};
    bool normed = false; // flag to indicate if point is normalized
    bool merced = false; // flag to indicate if point has been converted to mercator
    /*
      Constructors:
    */
    Point() { parr[0] = -12; parr[1] = -12; }
    // construct point from two floats
    Point(float c0, float c1) { parr[0] = c0; parr[1] = c1; }
    // construct point from arbitrary PointType
    Point(PointType c) { parr[0] = c[0]; parr[1] = c[1]; }
    // construct point from initializer list ( e.g. {0.1, 0.9} )
    Point(std::initializer_list<float> Pl)
    { std::copy(Pl.begin(), Pl.end(), parr.data()); }
    // (float*) -> To: Point
    Point(float* pp) { parr[0] = *pp; parr[1] = *(pp+1); }
    /*
      Type conversion functions: Point -> To: (???)
    */
    // Point -> To: BasePoint
    operator BasePoint() { return parr; }
    /*
      Other overloaded operators:
    */
    // (Point = Point) (overloaded assignment operator)
    Point& operator = (const Point & P) { parr[0] = P[0]; parr[1] = P[1]; return (*this); }
    // (Point << float*) assignment
    Point& operator = (const float* & Pf) { parr[0] = Pf[0]; parr[1] = Pf[1]; return (*this); }
    // point_instance(PointType c) : stores coord from another point instance
    Point& operator() (PointType c) { parr[0] = c[0]; parr[1] = c[1]; return (*this); }
    // access operator overloads (get, set)
    float operator[] (int pi) const { return parr[pi]; }
    float& operator[] (int pi) { return parr[pi]; }
    /*
      Helper funcs:
    */
  
    // getters, setters
    float x() const { return parr[0]; }
    float y() const { return parr[1]; }
    float x(float xf) { parr[0] = xf; return parr[0]; }
    float y(float yf) { parr[1] = yf; return parr[1]; }

    // check if point is mercator
    bool isMerc(){
      this->merced = ( abs(this->x()) > 180.0 || abs(this->y()) > 180.0 );
      return this->merced;
    }
    
    // print relevant debug info
    void print_point(std::string other_info="")
    {
      this->isMerc();
      std::cout << "Point(" << this->x() << ", " << this->y()
		<< "); msg: " << other_info
		<< " ; merced=" << merced << ", normed=" << normed
		<< std::endl;
    }
  
    // to access underlying point array
    float* data() { return parr.data(); }
  
    // load a float array 
    void toarr(pt_f pout) { for(int pi=0; pi < 2; pi++) pout[pi] = parr[pi]; }
  
    // mercator projection
    Point& merc()
    {
      this->isMerc();
      if(!merced)
	{
	  merced = true;
	  this->parr = sinusoidal(this->parr); // sinusoid instead of mercator projection
	  return (*this);
	}
      this->print_point("Warning: called merc() on previously projected point.");
      return (*this);
    }
    Point& invmerc()
    {
      this->isMerc();
      if(merced)
	{
	  float newA[2];
	  invsinusoidal(parr[0], parr[1], newA); // inverse sinusoidal instead of mercator!
	  (*this) = newA;
	  merced = false;
	  return (*this);
	}
      this->print_point("Warning: called invmerc() on non-mercator point.");
      return (*this);
    }
    // normalize to given area
    Point& norm(Area aer)
    {
      if(!normed)
	{ normed = true; this->parr = normalize_pt(this, aer); return (*this); }
      else {
	this->print_point("called norm() on previously normalized.");
	return (*this);
      }
    }
  };

  // PointRB alias for default Point template class
  typedef Point<BasePoint> PointRB;

  /*
    Coord type definition for RB
  */
  template <class PointType=PointRB>
  class Coord {
    PointRB pt = {0.0, 0.0}; // (X,Y)/(East,North)/(Long,Lat)
    std::string nm = "Unspecified"; // name of location
  public:
    Coord(){}
    Coord(PointType p)
    {
      pt[0] = p[0];
      pt[1] = p[1];
    }
    Coord(std::string n, PointType p): nm(n)
    {
      pt[0] = p[0];
      pt[1] = p[1];
    }
    Coord(PointType p, std::string n): nm(n)
    {
      pt[0] = p[0];
      pt[1] = p[1];
    }

    Coord<PointType>& operator () (Point<PointType> Pt) { pt(Pt); return (*this); }
    Coord<PointType>& operator () (std::string n) { this->name(n); return (*this); }
    Coord<PointType>& operator = (const Coord & C) { pt[0] = C[0]; pt[1] = C[1]; nm = C.name(); return (*this); }
    float operator[] (int ci) const { return pt[ci]; }
    float & operator[] (int ci) { return pt[ci]; }
    float* data() { return pt.data(); }
    void toarr(pt_f& pout) { for(int pi=0; pi < 2; pi++) { pout[pi] = pt.parr[pi]; } }
    float x() const { return pt[0]; }
    float y() const { return pt[1]; }
    float x(float xf) { pt[0] = xf; return pt[0]; }
    float y(float yf) { pt[1] = yf; return pt[1]; }
    std::string name() const { return nm; }
    std::string name(std::string n) { nm = n; return nm; }
    PointRB& merc() { this->pt = this->pt.merc(); return this->pt; }
    PointRB& norm(Area aer) { this->pt = this->pt.norm(aer); return this->pt; }
    void print_coord() {
      std::cout << this->name() << " | ";
      this->pt.print_point(); }
  };

  /* typedefs */
  typedef std::vector<Point<>> PointRoad; // vector of Coords, usually ordered by spatial adjacency
  typedef std::vector<PointRoad> RoadStore; // vector of PointRoads
  typedef std::unordered_map<std::string,Coord<>> CoordMap; // map object of ("Location Name", Coordinate)
  namespace fnspace = std::experimental::filesystem;
  namespace filesystem = fnspace;
  typedef fnspace::path fspath; // path type
  typedef std::vector<std::string> strvec; // string vector
  typedef std::vector<fspath> fpvec; // path vector
  
  // forward declaration of template function
  template <class Pt, class Pt2> inline void minRoad2Coord(Pt& cmin, Pt2 coord, PointRoad pr);

  /*   
  CoordFactory

  A class in which the default initial coordinates are stored in a private CoordMap, organized by (name, loc).

  - Specific coordinates can be accessed like so:

  `Coord specific_coordinate = CoordFactory()("specific-location-name");`

  - To get a vector of coordinates:
    
  `PointRoad specific_coords = CoordFactory()({"loc0", "loc1", "loc2"});`
  */
  class CoordFactory {
  private:
    CoordMap store = {
		      {"rami", Coord<PointRB>("rami",Point({-84.317,34.7425}))},
		      {"knox", Coord<PointRB>("knox",Point({-84.508419,34.220352}))},
		      {"decatur", Coord<PointRB>("decatur",Point({-84.275,33.781}))},
		      {"rb", Coord<PointRB>("rb",Point({-82.1472484,33.5562623}))},
		      {"elberton", Coord<PointRB>("elberton",Point({-82.874,34.0998}))},
		      {"edgefield", Coord<PointRB>("edgefield",Point({-81.974218,33.853262}))},
		      {"midlands", Coord<PointRB>("midlands",Point({-81.974218,33.853262}))},
		      {"grandview", Coord<PointRB>("grandview",Point({-81.01,36.945}))},
		      {"lamb", Coord<PointRB>("lamb",Point({-102.35,34.07}))},
		      {"wildcat", Coord<PointRB>("wildcat",Point({-84.570644,34.570084}))}
    };
  public:
    CoordFactory(){}
    Coord<PointRB> operator() (std::string name, PointRB loc)
    {
      store.emplace(name, Coord<PointRB>(name, loc));
      return store[name];
    }
    Coord<PointRB> operator() (std::string name)
    {
      return store[name];
    }
    std::vector<Coord<PointRB>>
    operator() (std::initializer_list<std::string> names)
    {
      std::vector<Coord<PointRB>> nout;
      for(auto& nm: names)
	nout.push_back(store[nm]);
      return nout;
    }
  };


  /*
    ========== global objects... ==========
  */

  bool use_GL = false; // OpenGL backend flag

  float MIN_STRIDE = 210.0; // minimum possible stride length in meters
  
  int nthreads = 8;
  
  Area marr{-10};
  
  std::time_t utres; // timestamp (set in justPop.cc)

  CoordFactory global_coords;
  Coord<PointRB> start_coord = global_coords("elberton");
  PointRB start_point;
  pt_f start_xydeg;
  RoadStore rpvec;
  // RoadStore rpvec: global object that contains the mercator-projected PointRoad objects for the current map area.

  
  /*
    ========== global paths ==========
  */
  
  // constant paths
  const std::string RB_DATA_PATH = fs::path(std::string(std::getenv("RB_DATA"))).string();
  const std::string RB_STATES_PATH = (fs::path(RB_DATA_PATH) /
				      "us_state_borders_wgs84/us_state_borders_wgs84.shp").string();
  const std::string RB_STATES_DBF = (fs::path(RB_DATA_PATH) /
				     "us_state_borders_wgs84/us_state_borders_wgs84.dbf").string();
  const std::string RB_ROADNETWORK_PATH = std::string(fs::path(std::string(std::getenv("RB_SRC"))).string());
  const std::string RB_ROADNETWORK_RESOURCES_PATH = std::string((fs::path(RB_ROADNETWORK_PATH) / "resources/").string());
  
  // global paths that can be modified
  fspath shapefn = fs::path(RB_DATA_PATH) / "gis_osm_roads/gis_osm_roads_free_1.shp";
  fspath fnout = fs::path(RB_ROADNETWORK_PATH) / "AreaOfAvail.png";

  
} // end namespace rb
using namespace rb;

#if defined(_THRUSTRB) && (_THRUSTRB==1||_THRUSTRB==true)
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
typedef typename thrust::host_vector<PointRB> HostPointRoad;
typedef typename thrust::host_vector<HostPointRoad> HostRoadStore;
#endif
#endif
