#ifndef SCRIPTS_H
#define SCRIPTS_H

#include <nlohmann/json.hpp>
#include <string>
#include <sstream>
#include <iostream>
#include <bits/stdc++.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <locale>
#include <vector>
#include <utility>
#include <iterator>
#include "shapefil.h"
#include "csv.h"
#include "rbtypes.hpp"

// levenshtein distance
size_t levdist(const std::string &s1, const std::string &s2);
float levdist_norm(const std::string &s1, const std::string &s2);

// definitions from/for countyPop2DBF.cc

std::string dbfpath = (fnspace::path(RB_DATA_PATH) / "tl_2016_us_county/tl_2016_us_county.dbf").string();
std::string fips_path = (fnspace::path(RB_DATA_PATH) / "state_fips.csv").string();
std::string data_path = (fnspace::path(RB_DATA_PATH) / "county_pop/").string();

// indices for fields
struct FieldIndex {
  int stinit = -1; // State initials (e.g. "GA")
  int statefp = -1; // State FIPS (e.g. '13')
  int name = -1; // County Name (e.g. "Dekalb")
  int countyns = -1; // CountyNS code index
  int countyfp = -1; // County FIPS
  int clim[36] = {-1}; // Climate indices
  int pop[5] = {-1}; // Population indices (2010,-15,-20,-25,-30)
};

DBFHandle dbfhand;
FieldIndex findex; // indices for fields
int nrec; // number of records

DBFHandle openCountyDBF();
void find_commas(std::vector<std::string::size_type>& commas, std::string line);
void getStateFIPS(std::vector<std::pair<std::string,int>>& fipsv);
int match_county_params(int state_fips, int ccode, std::string cname);
int match_county_params(int state_fips, int county_fips);

#ifndef ONLY_DECLARATIONS
#define ONLY_DECLARATIONS
DBFHandle openCountyDBF()
{
  dbfhand = DBFOpen(dbfpath.c_str(), "rb+");
  return dbfhand;
}
#endif

#endif
