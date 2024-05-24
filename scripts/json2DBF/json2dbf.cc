#include "scripts.hpp"

using json = nlohmann::json;

const std::string climate_path = std::string(getenv("RB_DATA")) + "/climate_data/";

void lowercase(std::string& strin)
{
  std::transform(strin.begin(), strin.end(), strin.begin(), [](unsigned char c){ return std::tolower(c);});
}

void uppercase(std::string& strin)
{
  std::transform(strin.begin(), strin.end(), strin.begin(), [](unsigned char c){ return std::toupper(c);});
}

int match_county_params(int state_fips, int county_fips)
{
  std::string::size_type sz;
  for(int ri=0; ri < nrec; ri++)
    {
      dbfhand = openCountyDBF(); // get state FIPS for a record
      int csfips = std::stoi(std::string(DBFReadStringAttribute(dbfhand, ri, findex.statefp)),&sz);
      DBFClose(dbfhand);
      dbfhand = openCountyDBF(); // get the county FIPS code for a record
      int ccode_r = std::stoi(std::string(DBFReadStringAttribute(dbfhand, ri, findex.countyfp)));
      DBFClose(dbfhand);
      if(csfips==state_fips && ccode_r==county_fips)
	{
	  return ri;
	}
    }
  return -1;
}

int main(int argc, char *argv[])
{

  std::string cfstrings[3] = {"PRCP", "TMIN", "TMAX"};
  std::string months[12] = {"01JAN", "02FEB", "03MAR", "04APR",
			    "05MAY", "06JUN", "07JUL", "08AUG",
			    "09SEP", "10OCT", "11NOV", "12DEC"};
  std::vector<std::string> fieldnames;
  
  // add the climate fields
  for(int cfi=0; cfi < 3; cfi++)
    {
      for(int cmi=0; cmi < 12; cmi++)
	{
	  std::string field_name = cfstrings[cfi]+months[cmi];
	  fieldnames.push_back(field_name);
	  dbfhand = openCountyDBF();
	  int tmp_findex = DBFGetFieldIndex(dbfhand, field_name.c_str());
	  DBFClose(dbfhand);
	  if(tmp_findex==-1)
	    {
	      dbfhand = openCountyDBF();
	      findex.clim[cfi*12+cmi] = DBFAddField(dbfhand, field_name.c_str(), FTDouble, 8, 3);
	      DBFClose(dbfhand);
	    } else { findex.clim[cfi*12+cmi] = tmp_findex; }
	}
    }
  std::cout << "finished creating any new fields\n";

  /*
    Get field indices
  */
  dbfhand = openCountyDBF(); // get the state initials index
  findex.stinit = DBFGetFieldIndex(dbfhand, "STINIT");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get the state FIPS index
  findex.statefp = DBFGetFieldIndex(dbfhand, "STATEFP");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get the county fips index
  findex.countyfp = DBFGetFieldIndex(dbfhand, "COUNTYFP");
  DBFClose(dbfhand);
  dbfhand = openCountyDBF(); // get number of records
  nrec = DBFGetRecordCount(dbfhand);
  DBFClose(dbfhand);
  
  std::ifstream sjsf(climate_path + "climate.json");
  json sjson = json::parse(sjsf);
  std::string state_fips, county_fips;
  for(auto it=sjson.begin(); it != sjson.end(); ++it)
    {
      try
	{
	  const std::string &pcountycode = it.key();
	  state_fips.assign(pcountycode.begin(), pcountycode.begin()+2);
	  county_fips.assign(pcountycode.begin()+2, pcountycode.begin()+5);
	  json &val = it.value();
	  int record_index = match_county_params(std::stoi(state_fips), std::stoi(county_fips));
	  for(auto it1=val.begin(); it1!=val.end(); ++it1) // CLIMATE ELEMENTS (TMIN, TMAX, PRCP...)
	    {
	      const std::string &climstr = it1.key();
	      json &climvals = it1.value();
	      for(auto it2=climvals.begin(); it2 != climvals.end(); ++it2)
		{
		  auto fnit = std::find(fieldnames.begin(), fieldnames.end(), climstr+it2.key());
		  if(fnit != fieldnames.end())
		    { // get the climate element index
		      int climix = findex.clim[std::distance(fieldnames.begin(), fnit)];
		      dbfhand = openCountyDBF();
		      DBFWriteDoubleAttribute(dbfhand, record_index, climix, (float)it2.value());
		      DBFClose(dbfhand);
		    }
		}
	    }
	}
      catch (json::exception& e)
	{
	  std::cout << "msg : " << e.what() << "\n" << "exception id : " << e.id << std::endl;
	  exit(EXIT_FAILURE);
	}
    }
  sjsf.close();
  
  // export the combined list to DBF
  
  return 0;
}
