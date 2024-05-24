#ifndef UTILS_H
#define UTILS_H

#include <iostream>
#include <iomanip>
#include <fstream>
#include <math.h>
#include <stdio.h>
#include <array>
#include <algorithm>
#include <vector>
#include <cmath>
#include <cctype>
#include <unordered_map>
#include <locale>
#include <stdexcept>
#include <experimental/array> // to_array(), make_array() functions in c++2a (C++20)
#include "rbtypes.hpp"
#include <experimental/filesystem>
#include "geom.hpp"
#include <nlohmann/json.hpp>
using json = nlohmann::json;
using namespace rb;

#ifndef _WIN32
#include <sys/resource.h> // functions to modify stack size
// modify stack size
void mod_stack();
void mod_stack()
{
  // modify the stack size if needed
  struct rlimit rlim;
  int result;
  uintmax_t cur;
  result = getrlimit(RLIMIT_STACK, &rlim);
  cur = (uintmax_t)rlim.rlim_cur;
  const rlim_t stacksz = (uintmax_t)(3.2e10) + cur;
  printf("rlim result = %d ; rlim = %ju \n", result, cur);
  if (result == 0)
    {
      printf("successfully checked rlim...\n");
      if (stacksz < rlim.rlim_max)
	{ // if current stack size+new < max
	  printf("stacksz < rlim_max\n");
	  rlim.rlim_cur = stacksz;
	  printf("set rlim.rlim_cur = %d.\n",(int)stacksz);
	  result = setrlimit(RLIMIT_STACK, &rlim);
	  printf("result of setrlimit=%d\n",result);
	  printf("stack size changed.\n");
	  if (result != 0)
	    {
	      std::cout << "\n!ERROR CODE TRYING TO CHANGE STACK SIZE: " << result << std::endl;
	      throw std::runtime_error("\n!ERROR CODE TRYING TO CHANGE STACK SIZE: " + std::to_string(result));
	    }
	} else {
	printf("rlim is already max.\n");
      }
  }
}
#endif

/* load geojson, with nlohmann/json */
json loadGeoJSON(std::string filename)
{
  json gjson;
  std::ifstream ifj(filename);
  ifj >> gjson;
  return gjson;
}

void writeGeoJSON(json gjson, std::string filename)
{
  std::ofstream o(filename);
  o << std::setw(4) << gjson << std::endl;
}

json loadGeoJSONTemplate(std::string template_name)
{
  std::string gtemplates_dir = RB_ROADNETWORK_RESOURCES_PATH;
  gtemplates_dir += "/geojson/";
  return loadGeoJSON(gtemplates_dir + template_name + ".json");
}

json mapFeatures2GeoJSON(PointRB center, std::vector<PointRB> availablePoints)
{
  json r2p = loadGeoJSONTemplate("r2p_template");
  r2p["features"][0]["geometry"]["coordinates"] = BasePoint(center); // original start point
  for(PointRB& rpt: availablePoints)
    r2p["features"][1]["geometry"]["coordinates"].push_back(BasePoint(rpt.invmerc()));
  return r2p;
}

/* PNG io functions (lodepng)  */
void decodeOneStep(const char* filename, std::vector<unsigned char>& image, unsigned*w, unsigned*h) {
  unsigned width, height;
  //decode
  unsigned error = lodepng::decode(image, width, height, filename);
  *w = width; *h = height;
  //if there's an error, display it
  if(error) std::cout << "decoder error " << error << ": " << lodepng_error_text(error) << std::endl;
  //the pixels are now in the vector "image", 4 bytes per pixel, ordered RGBARGBA..., use it as texture, draw it, ...
}

void encodeOneStep(const char* filename, std::vector<unsigned char>& image, unsigned width, unsigned height) {
  //Encode the image
  unsigned error = lodepng::encode(filename, image, width, height);
  //if there's an error, display it
  if(error) std::cout << "encoder error " << error << ": "<< lodepng_error_text(error) << std::endl;
}


/* String manip functions */
// string to uppercase (capitalize)
inline std::string str_toupper(std::string s);
inline std::string str_toupper(std::string s)
{
  std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c){ return std::toupper(c); });
  return s;
}

// string to lowercase
inline std::string str_tolower(std::string s);
inline std::string str_tolower(std::string s)
{
  std::transform(s.begin(), s.end(), s.begin(), [](unsigned char c){ return std::tolower(c); });
  return s;
}

// replace whitespace in string
inline std::string str_replacews(std::string s, const std::string& rep);
inline std::string str_replacews(std::string s, const std::string& rep)
{
  // std::replace_if(s.begin(), s.end(), std::isspace, rep);
  std::transform(s.begin(), s.end(), s.begin(), [rep](unsigned char c){ return std::isspace(c)?rep.at(0):c; });
  return s;
}


// split string by delimiter
inline strvec str_split(const std::string& i_str, const std::string& i_delim);
inline strvec str_split(const std::string& i_str, const std::string& i_delim)
{
  strvec result;
  size_t found = i_str.find(i_delim);
  size_t startIndex = 0;
  while(found != std::string::npos)
    {
      std::string temp(i_str.begin()+startIndex, i_str.begin()+found);
      result.push_back(temp);
      startIndex = found + i_delim.size();
      found = i_str.find(i_delim, startIndex);
    }
  if(startIndex != i_str.size())
    result.push_back(std::string(i_str.begin()+startIndex, i_str.end()));
  return result;
}

inline std::string strvec_join(strvec stv, std::string delim);
inline std::string strvec_join(strvec stv, std::string delim)
{
  std::string strout = stv.at(0);
  if(stv.size() == 1)
    return strout;
  for(unsigned i=1; i < stv.size(); i++)
    strout += " " + stv.at(i);
  return strout;
}

// trim from start (in place)
static inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int ch) {
        return !std::isspace(ch);
    }));
}

// trim from end (in place)
static inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

// trim from both ends (in place)
static inline void trim(std::string &s) {
    ltrim(s);
    rtrim(s);
}

// trim from start (copying)
static inline std::string ltrim_copy(std::string s) {
    ltrim(s);
    return s;
}

// trim from end (copying)
static inline std::string rtrim_copy(std::string s) {
    rtrim(s);
    return s;
}

// trim from both ends (copying)
static inline std::string trim_copy(std::string s) {
    trim(s);
    return s;
}

inline int medianInt(std::vector<int> vin);
inline int medianInt(std::vector<int> vin)
{
  std::sort(vin.begin(), vin.end());
  if(vin.size()%2==0)
    {
      return (vin[vin.size()/2 - 1] + vin[vin.size()/2])/2;
    }
  else
    {
      return vin[vin.size() / 2];
    }
}

inline int madInt(std::vector<int> vin, int* medInit);
inline int madInt(std::vector<int> vin, int* medInit)
{
  int med;
  if(medInit!=NULL)
    {
      med = *medInit;
    }
  else
    {
      med = medianInt(vin);
    }
  std::vector<int> tmp;
  for(int& nn: vin)
    {
      tmp.push_back(std::abs(nn-med));
    }
  return medianInt(tmp);
}

template <class Pt>
inline void printCoord(Pt coord, std::string extra)
{
  printf("%s : (%.4f, %.4f)\n",extra.c_str(),coord[0],coord[1]);
}


/*
  Geospatial Transforms
      Citation: "Map Projections-- A Working Manual." US Geological Survey. PROFESSIONAL PAPER 1395.
*/

inline float dec2rad(float); // decimal degrees -> radians

// geospatial constants
float R = 6378137; // meters (equatorial radius)
float lam0 = dec2rad(-84.0); // (degrees west -> radians) reference longitude (central meridian for Eastern Standard Time)
float f = 1.0/294.98; // Clarke 1866 ellipsoid flattening constant f=1-(b/a)
float a = 6378206.4; // Clarke 1866 (equatorial)
float b = 6356583.8; // Clarke 1866 (polar)
float e2 = 0.00676866; // Clarke 1866

inline float dec2rad(float deg)
{
  return M_PI*deg/180.0;
}

/*
  Calculate M (true distance along central meridian from the Equator to specified latitude Phi.)
*/
inline float calcTrueDistanceFromEquator(float phi)
{
  float phi_rad = (std::abs(phi) > 2.0*M_PI) ? dec2rad(phi) : phi; // convert to radians if necessary
  float phi_deg = (std::abs(phi) < 2.0*M_PI) ? (180.0 * phi / M_PI) : phi; // phi in degrees
  float A = ( 1.0 - e2/4.0 - 3.0*e2*e2/64.0 - 5.0*e2*e2*e2/256.0 ) * phi_rad;
  float B = ( 3.0*e2/8.0 + 3.0*e2*e2/32.0 + 45.0*e2*e2*e2/1024.0 ) * std::sin(2.0*phi_rad);
  float C = ( 15.0*e2*e2/256.0 + 45.0*e2*e2*e2/1024.0 ) * std::sin(4.0*phi_rad);
  float D = ( 35.0*e2*e2*e2/3072.0 ) * std::sin(6.0*phi_rad);
  return a * ( A - B + C - D );
}

/*
  Sinusoidal Projection (mercator equal-area)
  https://en.wikipedia.org/wiki/Sinusoidal_projection
      Citation: "Map Projections-- A Working Manual." US Geological Survey. PROFESSIONAL PAPER 1395. (Pages 248-249).
*/
inline BasePoint sinusoidal(BasePoint coord)
{ // ellipsoidal form of the sinusoidal pseudocylindrical projection
  float lam_rad = dec2rad(coord[0]);
  float lam_deg = coord[0];
  float phi_rad = dec2rad(coord[1]);
  float phi_deg = coord[1];
  coord[0] = a * (lam_deg - 180.0*lam0/M_PI) * (M_PI/180.0) * std::cos(phi_rad) / std::sqrt(1.0 - e2 * pow(std::sin(phi_rad),2));
  coord[1] = calcTrueDistanceFromEquator(phi_deg);
  return coord;
}

inline PointRB& sinusoidal(PointRB& coord)
{ // ellipsoidal form of the sinusoidal pseudocylindrical projection
  float lam_rad = dec2rad(coord[0]);
  float lam_deg = coord[0];
  float phi_rad = dec2rad(coord[1]);
  float phi_deg = coord[1];
  coord[0] = a * (lam_deg - 180.0*lam0/M_PI) * (M_PI/180.0) * std::cos(phi_rad) / std::sqrt(1.0 - e2 * pow(std::sin(phi_rad),2));
  coord[1] = calcTrueDistanceFromEquator(phi_deg);
  return coord;
}

inline PointRB& p2sinusoid(PointRB& pout, float l, float p)
{
  pout[0] = l;
  pout[1] = p;
  pout = sinusoidal(pout);
  try { pout.merced = true; } catch(const std::exception& excep) {
    std::cout << "warning: failed to set pout.merced = true in utils.hpp::p2sinusoid()\n";
    std::cout << "  PointRB& pout = (" << pout.x() << ", " << pout.y() << ")" << std::endl;
  }
  return pout;
}

/*
  Inverse Sinusoidal Projection
*/
inline void invsinusoidal(float x, float y, float coord[2])
{
  float mu_rad = y / (a*(1.0-e2/4.0-3.0*e2*e2/64.0-5.0*e2*e2*e2/256.0));
  float mu_deg = 180.0*mu_rad/M_PI;
  float e1 = (1.0-std::sqrt(1.0-e2))/(1.0+std::sqrt(1.0-e2));
  float A = ( 3.0*e1/2.0 - 27.0*pow(e1,3)/32.0 ) * std::sin(2.0*mu_rad);
  float B = ( 21.0*e1*e1/16.0 - 55.0*pow(e1,4)/32.0 ) * std::sin(4.0*mu_rad);
  float C = ( 151.0*pow(e1,3)/96.0 ) * std::sin(6.0*mu_rad);
  float D = ( 1097.0*pow(e1,4)/512.0 ) * std::sin(8.0*mu_rad);
  float phi_deg = mu_deg + (A + B + C + D) * 180.0 / M_PI;
  float phi_rad = dec2rad(phi_deg);
  coord[0] = (180.0 * lam0 / M_PI) + 180.0*( x*std::sqrt(1.0 - e2 * pow(std::sin(phi_rad),2)) / (a*std::cos(phi_rad)) ) / M_PI;
  coord[1] = phi_deg;
}

/*
  Mercator Projection
*/
inline BasePoint mercator(BasePoint coord)
{
  float lam = dec2rad(coord[0]);
  float phi = dec2rad(coord[1]);
  coord[0] = R * (lam - lam0);
  coord[1] = R * log(tan(M_PI/4.0 + phi/2.0));
  return coord;
}

inline PointRB& mercator(PointRB& coord)
{
  float lam = dec2rad(coord[0]);
  float phi = dec2rad(coord[1]);
  coord[0] = R * (lam - lam0);
  coord[1] = R * log(tan(M_PI/4.0 + phi/2.0));
  return coord;
}

inline PointRB& p2merc(PointRB& pout, float l, float p)
{
  pout[0] = l;
  pout[1] = p;
  pout = mercator(pout);
  try { pout.merced = true; } catch(const std::exception& excep) {
    std::cout << "warning: failed to set pout.merced = true in utils.hpp::p2merc()\n";
    std::cout << "  PointRB& pout = (" << pout.x() << ", " << pout.y() << ")" << std::endl;
  }
  return pout;
}

/*
  Inverse Mercator Projection
*/
inline void invmercator(float x, float y, float coord[2])
{
  coord[0] = (180.0/M_PI) * x / R;
  coord[1] = (180.0/M_PI) * (2.0*atan(std::exp(y/R))-M_PI/2.0);
}

template<class AreaType>
inline AreaType calcRangePointRoads(AreaType area, RoadStore rpvec);
template<class AreaType>
inline AreaType calcRangePointRoads(AreaType area, RoadStore rpvec)
{
  area[0] = rpvec[0][0][0];
  area[1] = rpvec[0][0][0];
  area[2] = rpvec[0][0][1];
  area[3] = rpvec[0][0][1];
  for(PointRoad& pr: rpvec)
    {
      for(PointRB& pt: pr)
	{
	  area[0] = std::min(pt[0], area[0]);
	  area[1] = std::max(pt[0], area[1]);
	  area[2] = std::min(pt[1], area[2]);
	  area[3] = std::max(pt[1], area[3]);
	}
    }
  return area;
}

inline PointRB normalize_pt(PointRB pt, AreaRB area)
{
  float tmp[2];
  tmp[0] = pt[0]; tmp[1] = pt[1];
  pt[0] = (tmp[0]-area[0])/(area[1]-area[0]);
  pt[1] = (tmp[1]-area[2])/(area[3]-area[2]);
  pt[1] = 1.0 - pt[1]; // invert for projection to screen (0,0 is upper left)
  return pt;
}

template <class AreaType>
inline RoadStore normalize_pts(RoadStore rpvec, AreaType area);
template <class AreaType>
inline RoadStore normalize_pts(RoadStore rpvec, AreaType area)
{
  std::vector<PointRoad> rpout;
  float pt[2];
  PointRB pa;
  for(int rx=0; rx < (int)rpvec.size(); rx++)
    {
      PointRoad prv = rpvec.at(rx);
      PointRoad prc;
      for(int ry=0; ry < (int)prv.size(); ry++)
	{
	  pt[0] = prv.at(ry)[0];
	  pt[1] = prv.at(ry)[1];
	  normalize_pt(pt, area);
	  pa[0] = pt[0]; pa[1] = pt[1];
	  prc.push_back(pa);
	}
      rpout.push_back(prc);
    }
  return rpout;
}

inline float normal_azimuth(float phi0, float phi1, float L);
inline float normal_azimuth(float phi0, float phi1, float L)
{
  phi0 = dec2rad(phi0);
  phi1 = dec2rad(phi1);
  L = dec2rad(L);
  float e2 = (f*(2.0-f));
  float Lam = pow(1.0 - f,2) * (tan(phi1)/tan(phi0)) + (  e2*sqrt( (1.0 + ((1.0-e2)*tan(phi1)*tan(phi1))) /
								   (1.0 + ((1.0-e2)*tan(phi0)*tan(phi0))) ) );
  float alpha = atan(sin(L) / ((Lam-cos(L))*sin(phi0)));
  return alpha;
}

struct VincentyInverseResult {
  float s = 0, a1 = 0, a2 = 0; //(s): ellipsoidal distance; (a1,a2): azimuths for each coordinate
};

inline VincentyInverseResult* vincenty(VincentyInverseResult* vp, float lam, float phi, float lam1, float phi1);
inline VincentyInverseResult* vincenty(VincentyInverseResult* vp, float lam0, float phi0, float lam1, float phi1)
{
  phi0=dec2rad(phi0);
  phi1=dec2rad(phi1);
  lam0=dec2rad(lam0);
  lam1=dec2rad(lam1);
  
  float B0 = atan((1-f)*tan(phi0));
  float B1 = atan((1-f)*tan(phi1));
  float L = lam1 - lam0;
  float lam = L;
  float lamOld = lam;
  float s, alpha1, alpha2;
  int iters = 0;
  while (true)
    {
      float sinsig = sqrt( pow(cos(B1)*sin(lam),2) +
			    pow(cos(B0)*sin(B1)-sin(B0)*cos(B1)*cos(lam),2) );
      float cossig = sin(B0)*sin(B1)+cos(B0)*cos(B1)*cos(lam);
      float sig = atan(sinsig/cossig);
      float sinalpha = (cos(B0)*cos(B1)*sin(lam))/sin(sig);
      float cos2alpha = 1.0 - pow(sinalpha,2);
      float cos2sigm = cossig - (2.*sin(B0)*sin(B1))/cos2alpha;
      float C = (f/16.0) * cos2alpha * (4. + f * (4.-3.*cos2alpha));
      lamOld = lam;
      lam = L+(1.-C)*f*sinalpha*(sig+C*sinsig*(cos2sigm+C*cossig*(-1.+2.*cos2sigm*cos2sigm)));
      if (std::abs(lam-lamOld) <= 1e-12 or (iters >= 200))
	{
	  float u2 = cos2alpha*(a*a - b*b)/(b*b);
	  float A = 1.+(u2/16384.0)*(4096.+u2*(-768.+u2*(320.-175.*u2)));
	  float B = (u2/1024.)*(256.+u2*(-128.+u2*(74.-47.*u2)));
	  float dsig = B*sinsig*(cos2sigm+0.25*B*(cossig*(-1.+2.*cos2sigm*cos2sigm))-(B/6.)*cos2sigm*(-3.+4.*sinsig*sinsig)*(-3.+4.*cos2sigm*cos2sigm));
	  s = b*A*(sig-dsig);
	  alpha1 = atan((cos(B1)*sin(lam))/(cos(B0)*sin(B1)-sin(B0)*cos(B1)*cos(lam))); // azimuth (1)
	  alpha2 = atan(cos(B0)*sin(lam)/(-sin(B0)*cos(B1)+cos(B0)*sin(B1)*cos(lam))); // azimuth (2)
	  break;
	}
      else
	{
	  iters += 1;
	}
    }
  vp->s = s; vp->a1 = alpha1; vp->a2 = alpha2;
  return vp;
}

inline float vdist(float c0[2], float c1[2]);
inline float vdist(float c0[2], float c1[2])
{
  VincentyInverseResult vr;
  return vincenty(&vr, c0[0], c0[1], c1[0], c1[1])->s;
}

inline PointRB triangulate(PointRoad coords, float D);
inline PointRB triangulate(PointRoad coords, float D)
{
  for(PointRB& prb : coords)
    {
      if(prb.merced)
	prb = prb.invmerc();
    }
  float az = normal_azimuth(coords[0][1], coords[1][1], coords[1][0]);
  float x = coords[0][0] + D*sin(az);
  float y = coords[0][1] + D*cos(az);
  PointRB coord2(x - D*sin(az), y - D*cos(az));
  return coord2;
}

inline float lindist(PointRB c0, PointRB c1)
{
  return sqrt(pow(c1[0]-c0[0],2)+pow(c1[1]-c0[1],2));
}

inline void fillRoadGaps(PointRoad& road, float dst);
inline void fillRoadGaps(PointRoad& road, float dst)
{
  unsigned i = 1;
  while(true)
    {
      PointRoad lastCoords{road.at(i), road.at(i-1)};
      float ldd = lindist(lastCoords[0], lastCoords[1]);
      if(ldd > dst)
	road.insert(road.end()-1, triangulate(lastCoords, ldd / 2.0));
      i++;
      if(i >= road.size())
	break;
    }
}

template <class Pt=PointRB, class Pt2=PointRB>
inline void minRoad2Coord(Pt& cmin, Pt2 coord, PointRoad pr)
{
  /*
    Calculate cmin[2] to be the point in pr that is the minimum distance from coord[2].
  */
  float dist = -1;
  float tdist;
  for(PointRB pt: pr)
    {
      tdist = lindist(coord, pt);
      if(dist==-1||tdist<dist)
	{
	  dist = tdist;
	  cmin[0] = pt[0];
	  cmin[1] = pt[1];
	}
    }
}

void printArea(float ar[4]);
void printArea(float ar[4])
{
    printf("area=%.4f %.4f %.4f %.4f\n",ar[0],ar[1],ar[2],ar[3]);
}

inline void find_closest_pt(float o[2], float c[2], std::vector<PointRoad> rpvec);
inline void find_closest_pt(float o[2], float c[2], std::vector<PointRoad> rpvec)
{
  float dst = -1;
  for(int i=0; i < (int)rpvec.size(); i++)
    {
      for(int j=0; j < (int)rpvec.at(i).size(); j++)
	{
	  float td = lindist(PointRB(c), PointRB(rpvec.at(i).at(j).data()));
	  if(dst == -1|| td < dst)
	    {
	      dst = td;
	      o[0] = rpvec.at(i).at(j)[0];
	      o[1] = rpvec.at(i).at(j)[1];
	    } 
	}
    }
}

inline bool withinArea(float x, float y, float spt[2], float rd[2]);
inline bool withinArea(float x, float y, float bds[4]);

inline bool withinArea(float x, float y, float bds[4])
{
  if(x < bds[0])
    return false;
  if(x > bds[1])
    return false;
  if(y < bds[2])
    return false;
  if(y > bds[3])
    return false;
  return true;
}

inline bool withinArea(float x, float y, float spt[2], float rd[2])
{
  float bds[4];
  bds[0] = spt[0] - rd[0];
  bds[1] = spt[0] + rd[0];
  bds[2] = spt[1] - rd[1];
  bds[3] = spt[1] + rd[1];
  if(x < bds[0])
    return false;
  if(x > bds[1])
    return false;
  if(y < bds[2])
    return false;
  if(y > bds[3])
    return false;
  return true;
}

fspath append_fn(fspath, fspath);
fspath append_fn(fspath p, fspath fn="")
{ /* Append shapefile filename to path that points to a directory
     [ Default = roads shapefile filename ]
  */
  if(fn == "")
    fn = fspath(shapefn).filename();
  p /= fn;
  return p;
}

/*
  Load roads shp files
*/

#include "shapefil.h"
#include "csv.h"
std::vector<PointRoad> openSHP(PointRB& spt, float R, float zoom,
			       float mindist, float bounds[4],
			       std::vector<std::string> stnames,
			       std::vector<Polygon<>> stbounds,
			       std::string="DQ_area_roads.shp");
	      
std::vector<PointRoad> openSHP(PointRB& spt, float R, float zoom,
			       float mindist, float bounds[4],
			       std::vector<std::string> stnames,
			       std::vector<Polygon<>> stbounds,
			       std::string fn)
{
  std::vector<PointRoad>().swap(rpvec);   // empty roads vector
  bounds[0] = spt[0]-R;
  bounds[1] = spt[0]+R;
  bounds[2] = spt[1]-R;
  bounds[3] = spt[1]+R;
  R *= 1.025; // load a little extra to make sure bounds are filled
  if(zoom < 0.5)
    R /= (zoom+0.5);
  PointRB mxy;
  PointRB mxy1;
  float dst = mindist*R / 2.0;
  if(dst < MIN_STRIDE)
    dst = MIN_STRIDE;
  std::cout << "(OpenSHP) Stride distance in meters: " << dst << " m." << std::endl;
  PointRB pta;
  float R2d[2] = {R, R};
  int shpN, shptype;
  double minBound[4];
  double maxBound[4];
  PointRoad current_road;
  SHPHandle shphand;
  SHPObject* shpread;
  fspath shapepath;
  std::vector<fspath> geompaths;
  auto get_stbound =
    [stnames,stbounds](std::string stn)
    {
      auto it = std::find_if(stnames.begin(),
			     stnames.end(),
			     [stn](std::string sn)
			     {
			       std::string sl = str_tolower(sn);
			       std::string sl1 =str_tolower(stn);
			       return (sl==sl1); });
      if(it != stnames.end())
	return (int)std::distance(stnames.begin(),it);
      else
	return (int)-1;
    };
  std::cout << "loading roads within R : L=" << R << " meters" << std::endl;
  fs::path gis_extra_path = fs::path(rb::RB_DATA_PATH) / "gis_osm_roads_extra/";
  for(const auto & entry : filesystem::directory_iterator(gis_extra_path))
    {
      shapepath = append_fn(entry.path(),"");
      shphand = SHPOpen(shapepath.c_str(), "rb");
      SHPGetInfo(shphand,&shpN,&shptype,minBound,maxBound);
      strvec snvec = str_split(entry.path().stem().string(),"_geom");
      std::string snm = snvec.at(0);
      snvec = str_split(snm,"-");
      for(auto& snv: snvec){
	std::string ss(1,snv.at(0));
	snv.at(0) = str_toupper(ss).at(0);
      }
      snm = strvec_join(snvec, " ");
      int ixx = get_stbound(snm);
      if(ixx > 0 && ixx < (int)stbounds.size())
	{
	  Polygon<> stb = stbounds.at(ixx);
	  if(stb.coord_within(spt)){
	    shapefn = shapepath;
	  } else {
	    geompaths.push_back(shapepath);
	  }
	}
    }
  std::cout << "(openSHP) primary roads shapefile path: " << shapefn << std::endl;
  io::CSVReader<2, io::trim_chars<' '>, io::double_quote_escape<',','\"'>>
    csvfile(fs::path(RB_DATA_PATH) / "state_borders.csv");
  csvfile.read_header(io::ignore_extra_column, "State", "Bordering States");
  std::string statename, borders;
  strvec bvec;
  double best_dist = -1;
  fpvec shpfiles_toload{shapefn};
  while(csvfile.read_row(statename, borders))
    {
      std::string sname = str_replacews(str_tolower(statename),"-");
      if(std::string(shapefn).find(sname) != std::string::npos)
	{
	  bvec = str_split(borders,", ");
	  for(std::string& bstr : bvec){
	    bstr = str_replacews(str_tolower(bstr),"-");
	    for(const auto& gstr : geompaths){
	      if(std::string(gstr).find(bstr)!=std::string::npos){
		shpfiles_toload.push_back(gstr);
		std::cout << "(openSHP) border state roads shpfile : "
			  << shpfiles_toload.back() << std::endl;
	      }
	    }
	  }
	  break;
	}
    }
  for(const auto& shpfn : shpfiles_toload)
    {
      std::cout << "(openSHP) loading roads shpfile: " << shpfn << std::endl;
      shphand = SHPOpen(shpfn.c_str(), "rb");
      SHPGetInfo(shphand,&shpN,&shptype,minBound,maxBound);
      for(int si=0; si < shpN; si++)
	{
	  shpread = SHPReadObject(shphand, si);
	  PointRoad().swap(current_road);
	  for(int vi=0; vi < shpread->nVertices; vi++)
	    {
	      mxy = p2sinusoid(mxy, (float)shpread->padfX[vi], (float)shpread->padfY[vi]);
	      if(withinArea(mxy[0], mxy[1], spt.data(), R2d))
		{
		  pta = { mxy[0], mxy[1] };
		  current_road.push_back(pta);
		  PointRoad lastCoords{current_road.back(), *(current_road.end()-2)};
		  float ldd = lindist(lastCoords[0], lastCoords[1]);
		  if(ldd > dst)
		    current_road.insert(current_road.end()-1, triangulate(lastCoords, ldd / 2.0));
		  float d2spt = lindist(current_road.back(), spt) * 0.5;
		  if((d2spt <= dst) && ((best_dist==-1)||(d2spt < best_dist)))
		    {
		      spt[0] = current_road.back()[0];
		      spt[1] = current_road.back()[1];
		    }
		}
	    }
	  SHPDestroyObject(shpread);
	  if((int)current_road.size() >= 1 ){
	    rpvec.push_back(current_road);
	  }
	}
      SHPClose(shphand);
    }
  std::cout << "rpvec.size=" << (int)rpvec.size() << std::endl;
  rb::assert_msg(((int)rpvec.size() > 0), "No data was available for the requested area.");
  if (rpvec.empty())
    std::cout << "(no roads found within the requested area.)" << std::endl;
  return rpvec;
}

#endif
