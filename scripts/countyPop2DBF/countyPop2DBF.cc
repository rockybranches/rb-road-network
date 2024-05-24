#include "scripts.hpp"


// countyPop2DBF.cc

/* Script for updating county population info: 
 (local CSVs) $RB_DATA/county_pop/(*.CSV)
 => .DBF (local data file)
 $RB_DATA/tl_2016_us_county_wgs84/tl_2016_us_county.dbf
*/

std::string psr[5] = {"POP10", "POP15", "POP20", "POP25", "POP30"};

void getStateFIPS(std::vector<std::pair<std::string,int>>& fipsv)
{
  std::cout << "getStateFIPS()...\n";
  io::CSVReader<3> fipsfile(fips_path);
  fipsfile.read_header(io::ignore_extra_column, "State Name", "State Abbrev", "State FIPS");
  std::string abbrev, stname; int fips;
  while(fipsfile.read_row(stname, abbrev, fips))
    {
      std::transform(abbrev.begin(), abbrev.end(), abbrev.begin(), [](unsigned char c){ return std::tolower(c);});
      fipsv.push_back(std::pair(abbrev,fips));
    }
  int ct = 1;
  for(auto& spair : fipsv) {
    std::cout << ct << " " << spair.first << ", " << spair.second << std::endl;
    ct++;
  }
}

void find_commas(std::vector<std::string::size_type>& commas, std::string line)
{
  std::string::size_type pos = line.find(",",0);
  while(pos != std::string::npos) { commas.push_back(pos); pos = line.find(",",pos+1); }
}

int match_county_params(int state_fips, int ccode, std::string cname)
{
  std::string::size_type sz;
  for(int ri=0; ri < nrec; ri++)
    {
      dbfhand = openCountyDBF(); // get state FIPS for a record
      int csfips = std::stoi(std::string(DBFReadStringAttribute(dbfhand, ri, findex.statefp)),&sz);
      DBFClose(dbfhand);
      dbfhand = openCountyDBF(); // get the county NS code for a record
      int ccode_r = std::stoi(std::string(DBFReadStringAttribute(dbfhand, ri, findex.countyns)));
      DBFClose(dbfhand);
      if(csfips==state_fips && ccode_r==ccode)
	{
	  std::cout << "    + Found (County, State) : " << cname << ", " << state_fips << std::endl;
	  return ri;
	}
    }
  return -1;
}

typedef std::vector<std::vector<std::string>> strvec;

int main(int argc, char*argv[])
{
  std::locale::global(std::locale("en_US.utf8"));
  std::vector<std::pair<std::string,int>> fipsv;
  getStateFIPS(fipsv);
  std::cout << "done getting state fips from CSV" << std::endl;

  /*
    Create new fields
  */
  int tmp_findex = 0;
  for(int pj=0; pj < 5; pj++)
    {
      dbfhand = openCountyDBF(); // Add the county population fields
      tmp_findex = DBFGetFieldIndex(dbfhand, psr[pj].c_str());
      DBFClose(dbfhand);
      if(tmp_findex==-1) // only add field if it hasn't already been created
	{
	  dbfhand = openCountyDBF();
	  DBFAddField(dbfhand, psr[pj].c_str(), FTInteger, 10, 0);
	  DBFClose(dbfhand);
	}
    }
  dbfhand = openCountyDBF();
  tmp_findex = DBFGetFieldIndex(dbfhand, "STINIT");
  DBFClose(dbfhand);  // add the state initials field
  if(tmp_findex==-1)
    {
      dbfhand = openCountyDBF();
      DBFAddField(dbfhand, "STINIT", FTString, 2, 0);
      DBFClose(dbfhand);
    }
  std::cout << "done creating new fields" << std::endl;

  /*
    Get field indices
  */
  dbfhand = openCountyDBF(); // get the state initials index
  findex.stinit = DBFGetFieldIndex(dbfhand, "STINIT");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get the state FIPS index
  findex.statefp = DBFGetFieldIndex(dbfhand, "STATEFP");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get the county name index
  findex.name = DBFGetFieldIndex(dbfhand, "NAME");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get the countyns index
  findex.countyns = DBFGetFieldIndex(dbfhand, "COUNTYNS");
  DBFClose(dbfhand);
  for(int pj=0; pj < 5; pj++)
    {
      dbfhand = openCountyDBF(); // get the county population indices
      findex.pop[pj] = DBFGetFieldIndex(dbfhand, psr[pj].c_str());
      DBFClose(dbfhand);
    }
  dbfhand = openCountyDBF(); // get number of records
  nrec = DBFGetRecordCount(dbfhand);
  DBFClose(dbfhand);
  std::cout << "done getting field indices\n";

  /*
    Iterate through (state, FIPS) pairs,
    write the population data from the corresponding CSV file.
  */
  for(auto stpair: fipsv)
    {
      std::cout << "==> State: " << stpair.first << ", FIPS: " << stpair.second << std::endl;
      try
	{
	  std::cout << "  - Reading population data from CSV...\n";
	  io::CSVReader<7> csvfile(data_path + "/" + stpair.first + ".csv");
	  csvfile.read_header(io::ignore_extra_column, "County NS Code", "County", "2010", "2015", "2020", "2025", "2030");
	  int nrows = 0;
	  std::string cname;
	  int ccode;
	  float pop10, pop15, pop20, pop25, pop30;
	  while(csvfile.read_row(ccode, cname, pop10, pop15, pop20, pop25, pop30))
	    {
	      int dix = match_county_params(stpair.second, ccode, cname);
	      if(dix!=-1)
		{
		  dbfhand = openCountyDBF(); // write STINIT -> DBF
		  DBFWriteStringAttribute(dbfhand, dix, findex.stinit, stpair.first.c_str());
		  DBFClose(dbfhand);
		  std::cout << "      STINIT : " << stpair.first << std::endl;
		  std::vector<float> popvec{pop10, pop15, pop20, pop25, pop30};
		  std::cout << "      [ Pop : ";
		  for(int pi=0; pi < 5; pi++)
		    {
		      dbfhand = openCountyDBF();
		      DBFWriteIntegerAttribute(dbfhand, dix, findex.pop[pi], (int)popvec[pi]);
		      DBFClose(dbfhand);
		      std::cout << (int)popvec[pi] << " ";
		    }
		  std::cout << " ] " << std::endl;
		}
	      nrows++;
	    }
	  std::cout << "  + Done writing (nrows=" << nrows << ") to DBF.\n";
	} catch (std::exception& excep) { std::cout << "(!) Exception! " << excep.what() << std::endl; exit(EXIT_FAILURE); }
    }
  return 0;
}
