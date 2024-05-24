#include <stdio.h>
#include <iostream>
#include <fstream>
#include <ctime>
#include <string>
#include <functional>
#include <experimental/array>
#include "rbtypes.hpp"
using namespace rb;
#include "utils.hpp"
#include "gridimg_utils.hpp"
#include "grid.hpp"

using namespace std;
using namespace gim;

int main(int argc, char*argv[])
{
  utres = std::time(nullptr);
  std::string dbfn =
    RB_DATA_PATH + "logs/" + "debug-" + std::string(std::getenv("USER")) +
    "-" + std::to_string(utres) + ".log";
  std::ofstream debug_file(dbfn);
#if defined(_RB_DEBUG) && (_RB_DEBUG == true || _RB_DEBUG == 1)
  std::cout << "Debug Log File: " << dbfn << std::endl;
#endif
  freopen(dbfn.c_str(),"a+",stdout);
  std::cout << "Debug Log File: " << dbfn << std::endl;

  cout << "== Test GlyphMap ==\n" << endl;

  GlyphMap gmp;
  cout << "Declared reference of GlyphMap.\n\n";

  cout << "\nTesting: GlyphMap.loadGlyphs()...\n";
  gmp.loadGlyphs();
  cout << "...GlyphMap.loadGlyphs() test completed.\n";
  
  cout << "\nTesting: GlyphMap.getWordGlyphs()...\n";
  string gstr = "Hi, hello. This is a test (test, getWordGlyphs).";
  std::cout << "string requested: '" << gstr << "'" << endl;
  gword gw = gmp.getWordGlyphs(gstr);
  for(Glyph& gg : gw)
    std::cout << "Glyph Name = " << gg.name << endl;
  cout << "...GlyphMap.getWordGlyphs() test completed.\n\n";
  
  cout << "\n-- Test GlyphMap Complete. --\n" << endl;
}
