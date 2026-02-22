#ifndef PLACES_H
#define PLACES_H

#include <array>
#include "rbtypes.hpp"
#include <locale>
#include "utils.hpp"
#include "grid.hpp"
#include "geom.hpp"

struct PlacePop {
  int id;
  std::string name;
  std::vector<int> years{2010, 2015, 2020, 2025, 2030};
  std::vector<int> pops;
  void print_pops()
  {
    for(int pi=0; pi < (int)pops.size(); pi++)
      {
	std::cout << "Year: " << years.at(pi) << " Pop: " << pops.at(pi) << std::endl;
      }
  }
};

struct County {
  bool avail = false; // is the county available?
  bool start = false; // county contains start point?
  int cuid; // unique ID (GNIS code for the county)
  int grix; // GridRect index (corresponds to Grid().grid)
  int grX, grY; // GridRect nx, ny
  std::string name; // county name
  std::string stinit; // state initials (2-letter abbrev, e.g. "GA")
  float loc[2]; // mercator loc (E, N)
  float label_loc[2]; // coordinate (X,Y) to specify the county label location
  PointRoad bound; // mercator bound
  Polygon<PointRB> *shape; // county shape defined by bound
  PlacePop pop; // population values for years: (2010, 15, 20, 25, 30)
  float area[4];
  County(int cid, std::string nm, std::string stin, PointRB l, PointRoad bd, AreaRB mArr) : cuid(cid), name(nm), stinit(stin)
  {
    /*
      input Location (l[2]) should be in mercator, not normalized
      input Bound (bd) should be also in mercator, not normalized
    */
    bound = bd;
    loc[0] = l[0]; loc[1] = l[1]; // store location (mercator)
    shape = new Polygon<PointRB>(bd); // mercator polygon
    area[0] = shape->area_rect[0]; area[1] = shape->area_rect[1]; // get mercator area from polygon
    area[2] = shape->area_rect[2]; area[3] = shape->area_rect[3];
    calc_label_loc(); // calculate label location
  }
  void calc_label_loc()
  {
    /*
      From the polygon bounding box, get the label position
    */
    label_loc[0] = loc[0];
    label_loc[1] = loc[1];
  }
  void calc_county_availability_singlePt(PointRB pt)
  {
    if(shape->coord_within(pt))
      this->avail = true;
  }
  void calc_county_availability(Grid& gd)
  {
    /*
      determine if the county is available via the grid
    */
    if(shape->coord_within(gd.grid.at(gd.start_ix).med))
      this->start = true;
    // check if grid rect is part of the county border
    for(GridRect& gr : gd.grid){
      for(auto side: this->shape->sides){
	if(gr.inRect(side.a) || gr.inRect(side.b)){
	  gr.cborder = true;
	  for(GridRect& gtmp: gd.grid)
	    {
	      if(gtmp.isAdjacent(gr))
		{
		  gtmp.cborder = true;
		  break;
		}
	    }
	}
      }
    }
    if(!this->avail)
      { // county availability check
	for(GridRect& gr: gd.grid)
	  {
	    if(gr.avail)
	      {
		if(shape->coord_within(gr.med))
		  {
		    std::cout << this->name << " County (Avail) : " << 
		      "GridRect(" << gr.med[0] << "," << gr.med[1] << ") within bounds." << std::endl;
		    this->avail = true;
		    break;
		  }
	      }
	  }
      }
    if(this->avail)
      {
	int gri = gd.findClosestGridRect(label_loc);
	GridRect gr = gd.grid.at(gri);
	this->grY = gr.iNy;
	this->grX = gr.iNx;
	gd.grid.at(gri).clabel = true;
	gd.grid.at(gri).cname = this->name + ", " + this->stinit;
	this->grix = gri;
	if(this->start)
	  gd.grid.at(gri).cstart = true;
      }
  }
  void print_county()
  {
    printf("\nCOUNTYNS: %d\n",cuid);
    printf("AVAIL: %d\n",this->avail);
    printf("NR_BOUNDS: %d\n", (int)bound.size());
    printf("NAME: %s\n",name.c_str());
    printf("LOC: %.2f, %.2f\n",loc[0],loc[1]);
    printf("LabelLoc: %.2f, %.2f\n",label_loc[0],label_loc[1]);
    printf("GridIndex: %d , (iNx: %d, iNy: %d)\n", this->grix, this->grX, this->grY);
    pop.print_pops();
  }
};

#include "shapefil.h"

static std::vector<County> counties;
std::string dbfpath = (fs::path(rb::RB_DATA_PATH) / "tl_2016_us_county_wgs84/tl_2016_us_county.dbf").string();

void openCountyDBF(DBFHandle* dbfp);
void openCountyDBF(DBFHandle* dbfp)
{
  (*dbfp) = DBFOpen(dbfpath.c_str(), "rb");
}

void loadCountySHP(float start_pt[2], float radius,
		   float zoom, float mindist,
		   std::string fn);
void loadCountySHP(float start_pt[2], float radius,
		   float zoom, float mindist, std::string fn)
{  
  std::vector<County>().swap(counties); // empty counties vector
  if(zoom < 0.5)
    radius /= (zoom + 0.5);
  float D = radius * 2;  // enables the search radius to fill the AoI polygon
  printf("loading counties within square L=%.1f m\n",radius);
  SHPHandle shphand = SHPOpen(fn.c_str(), "rb");
  int shpN, shptype;
  double minBound[4];
  double maxBound[4];
  SHPGetInfo(shphand,&shpN,&shptype,minBound,maxBound);
  printf("(counties) shpN=%d , shptype=%d , minBound=%.3f %.3f %.3f %.3f , maxBound=%.3f %.3f %.3f %.3f\n",
	 shpN, shptype, minBound[0], minBound[1], minBound[2], minBound[3],
	 maxBound[0], maxBound[1], maxBound[2], maxBound[3]);
  PointRB cent;
  PointRB mxy;
  float xy1[2] = {0, 0};
  BasePoint pta;
  float radius2d[2] = {radius, radius};
  DBFHandle dbfhand;
  openCountyDBF(&dbfhand);
  int cname_ix = DBFGetFieldIndex(dbfhand, "NAME");
  DBFClose(dbfhand);
  openCountyDBF(&dbfhand);
  int lsad_ix = DBFGetFieldIndex(dbfhand, "COUNTYNS");
  DBFClose(dbfhand);
  openCountyDBF(&dbfhand);
  int lat_ix = DBFGetFieldIndex(dbfhand, "INTPTLAT");
  DBFClose(dbfhand);
  openCountyDBF(&dbfhand);
  int lon_ix = DBFGetFieldIndex(dbfhand, "INTPTLON");
  DBFClose(dbfhand);
  openCountyDBF(&dbfhand);
  int stinit_ix = DBFGetFieldIndex(dbfhand, "STINIT");
  DBFClose(dbfhand);
  printf("CNAMEIX=%d ; NSIX=%d ; LATIX=%d ; LONIX=%d ; STINITIX=%d\n",
	 cname_ix, lsad_ix, lat_ix, lon_ix, stinit_ix);
  std::string psr[5] = {"10", "15", "20", "25", "30"};
  int popixs[5];
  PointRoad current_county;
  for(int pj=0; pj < 5; pj++)
    {
      openCountyDBF(&dbfhand);
      popixs[pj] = DBFGetFieldIndex(dbfhand, ("POP" + psr[pj]).c_str());
      DBFClose(dbfhand);
    }  
  for(int si=0; si < shpN; si++)
    {
      openCountyDBF(&dbfhand);
      std::string county_name = std::string(DBFReadStringAttribute(dbfhand, si, cname_ix));
      DBFClose(dbfhand);

      dbfhand = DBFOpen(dbfpath.c_str(), "rb");
      std::string lsad = std::string(DBFReadStringAttribute(dbfhand, si, lsad_ix));
      DBFClose(dbfhand);

      dbfhand = DBFOpen(dbfpath.c_str(), "rb");
      std::string intptLAT = std::string(DBFReadStringAttribute(dbfhand, si, lat_ix));
      DBFClose(dbfhand);

      dbfhand = DBFOpen(dbfpath.c_str(), "rb");
      std::string intptLON = std::string(DBFReadStringAttribute(dbfhand, si, lon_ix));
      DBFClose(dbfhand);

      dbfhand = DBFOpen(dbfpath.c_str(), "rb");
      std::string stinit = std::string(DBFReadStringAttribute(dbfhand, si, stinit_ix));
      DBFClose(dbfhand);
      
      SHPObject* shpread = SHPReadObject(shphand, si);
      PointRoad().swap(current_county);
      for(int vi=0; vi < shpread->nVertices; vi++)
	{
	  mxy = p2sinusoid(mxy, (float)shpread->padfX[vi], (float)shpread->padfY[vi]);
	  if(withinArea(mxy[0], mxy[1], start_pt, radius2d))
	    {
	      pta = { mxy[0], mxy[1] };
	      current_county.push_back(pta);
	    }
	}
      if(current_county.size() >= (unsigned)(shpread->nVertices / 2.0))
	{
	  // fillRoadGaps(current_county, mindist*radius*3.0);
	  cent = p2sinusoid(cent, (float)std::stof(intptLON,nullptr), (float)std::stof(intptLAT,nullptr));
	  County ccounty(std::stoi(lsad,nullptr), std::string(county_name), str_toupper(std::string(stinit)),
			 cent, current_county, marr);
	  for(int pk=0; pk < 5; pk++)
	    {
	      openCountyDBF(&dbfhand);
	      ccounty.pop.pops.push_back(DBFReadIntegerAttribute(dbfhand, si, popixs[pk]));
	      DBFClose(dbfhand);
	    }
	  counties.push_back(ccounty);
	  // counties.back().print_county();
	}
      SHPDestroyObject(shpread);
    }
  SHPClose(shphand);
  std::cout << "counties.size=" << (int)counties.size() << std::endl;
}


class State {
public:
  std::string name;
  std::string abbrev;
  PointRoad bound; // mercator bound
  Polygon<PointRB> *shape; // shape defined by bound
  rb::Area area;
  State(std::string nm, std::string ab, PointRoad bd): name(nm), abbrev(ab), bound(bd)
  {
    shape = new Polygon<PointRB>(bound); // mercator polygon
    area[0] = shape->area_rect[0]; area[1] = shape->area_rect[1]; // get mercator area from polygon
    area[2] = shape->area_rect[2]; area[3] = shape->area_rect[3];
  }
};

class States {
public:
  std::vector<State> states;
  int stname_ix;
  int stabbrev_ix;
  States()
  {
    std::cout << "Opening handler for States dbf..." << std::endl;
    DBFHandle dbfhand;
    openStateDBF(&dbfhand);
    stname_ix = DBFGetFieldIndex(dbfhand, "NAME");
    DBFClose(dbfhand);
    openStateDBF(&dbfhand);
    stabbrev_ix = DBFGetFieldIndex(dbfhand, "STUSPS");
    DBFClose(dbfhand);
    int shpN, shptype;
    double minBound[4], maxBound[4];
    SHPHandle shphand = SHPOpen(RB_STATES_PATH.c_str(), "rb");
    SHPGetInfo(shphand,&shpN,&shptype,minBound,maxBound);
    PointRB mxy;
    for(int si=0; si < shpN; si++)
      {
	openStateDBF(&dbfhand);
	std::string st_name = std::string(DBFReadStringAttribute(dbfhand, si, stname_ix));
	std::cout << "Opening state DBF for " << st_name << std::endl;
	DBFClose(dbfhand);
	openStateDBF(&dbfhand);
	std::string st_abbrev = std::string(DBFReadStringAttribute(dbfhand, si, stabbrev_ix));
	DBFClose(dbfhand);
	SHPObject* shpread = SHPReadObject(shphand, si);
	PointRoad current_state;
	for(int vi=0; vi < shpread->nVertices; vi++)
	  {
	    mxy = p2sinusoid(mxy, (float)shpread->padfX[vi], (float)shpread->padfY[vi]);
	    current_state.push_back(mxy);
	  }
	State st(st_name, st_abbrev, current_state);
	states.push_back(st);
	SHPDestroyObject(shpread);
	PointRoad().swap(current_state);
      }
    SHPClose(shphand);
  }
  void openStateDBF(DBFHandle* dbfp)
  {
    std::cout << "Loading state boundaries: " << rb::RB_STATES_DBF << std::endl;
    (*dbfp) = DBFOpen(rb::RB_STATES_DBF.c_str(), "rb");
  }
  std::vector<Polygon<>> get_bounds()
  {
    std::vector<Polygon<>> stpolygons;
    for(State& stt: states)
      stpolygons.push_back(*(stt.shape));
    return stpolygons;
  }
  std::vector<std::string> get_names()
  {
    std::vector<std::string> names;
    for(State& stt: states)
      names.push_back(stt.name);
    return names;
  }
};

#endif
