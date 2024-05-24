#ifndef GEOM_H
#define GEOM_H

#include <vector>
#include <array>
#include <limits>
#include <set>
#include <algorithm>
#include "rbtypes.hpp"
using namespace rb;

const float eps = (float)(std::numeric_limits<float>().epsilon());
const std::numeric_limits<float> FLOAT;
const float MIN = FLOAT.min();
const float MAX = FLOAT.max();
const unsigned MAX_CORRECTION_ITERS = 1500;

template <class PointType=rb::Point<BasePoint>>
struct Side {
  PointType a;
  PointType b;
  bool hit = false; // indicates if a point has intersected this side
  Side() {}
  Side(PointType a0, PointType b0)
  {
    if(a0[1] > b0[1]) { b(a0); a(b0); }
    else { a(a0); b(b0); }
  }
  Side(std::initializer_list<PointType> plst)
  {
    PointType a0; PointType b0;
    std::copy(plst.begin(), plst.begin()+2, a0.data());
    std::copy(plst.begin()+2, plst.end(), b0.data());
    if(a0[1] > b0[1]) { b(a0); a(b0); }
    else { a(a0); b(b0); }    
  }
  bool operator()(PointType& p)
  {
    unsigned citers = 0;
    while(true){
      if(abs(p[1]-a[1]) <= MIN || abs(p[1]-b[1]) <= MIN)
      {
	p[1] = 1.0*(p[1] + eps*1.0);
      } else { break; }
    if(citers >= MAX_CORRECTION_ITERS)
      break;
    citers++;
    }
    if(p[1] > b[1] || p[1] < a[1] || p[0] > std::max(a[0], b[0])) return false;
    if(p[0] < std::min(a[0], b[0])) return true;
    auto blue = std::abs(a[0] - p[0]) > MIN ? (p[1] - a[1]) / (p[0] - a[0]) : MAX;
    auto red = std::abs(a[0] - b[0]) > MIN ? (b[1] - a[1]) / (b[0] - a[0]) : MAX;
    return blue >= red;
  }
};

template <class PointType=rb::Point<BasePoint>>
struct Polygon {
  std::vector<Side<PointRB>> sides;
  float area_rect[4]; // minx, maxx, miny, maxy
  Polygon(PointRoad vertices)
  {
    area_rect[0] = vertices.at(0)[0];
    area_rect[1] = vertices.at(0)[0];
    area_rect[2] = vertices.at(0)[1];
    area_rect[3] = vertices.at(0)[1];
    for(int vi=0; vi < (int)vertices.size()-1; vi++) {
    	sides.push_back(Side(PointRB(vertices.at(vi)[0], vertices.at(vi)[1]),
			     PointRB(vertices.at(vi+1)[0], vertices.at(vi+1)[1])));
	area_rect[0] = std::min(vertices.at(vi)[0], area_rect[0]);
	area_rect[2] = std::min(vertices.at(vi)[1], area_rect[2]);
	area_rect[1] = std::max(vertices.at(vi)[0], area_rect[1]);
	area_rect[3] = std::max(vertices.at(vi)[1], area_rect[3]);
    }
  }
  bool coord_within(PointType coord)
  {
    int cc = 0;
    for(auto& sd: sides)
      if(sd(coord)) { sd.hit = true; cc++; }
    return (cc % 2 != 0);
  }
};

#endif
