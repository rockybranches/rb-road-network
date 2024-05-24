#ifndef GRIDIMG_UTILS_H
#define GRIDIMG_UTILS_H
#include <map>
#include <experimental/filesystem>
#include "rbtypes.hpp"
#include "utils.hpp"
#include "lodepng.h"

/*
  GridImage Utils
*/

namespace gim {
  
  /* Type Definitions for GridImage namespace */
  typedef unsigned char ccomp;
  typedef std::vector<ccomp> gimg;
  typedef std::vector<ccomp>::iterator gimgiter;
  typedef std::map<std::string,std::string> gnmap;

  gimg readPNG(std::string fn, unsigned*wp, unsigned*hp)
  {
    gimg im; //the raw pixels
    decodeOneStep(fn.c_str(), im, wp, hp);
    return im;
  }
  
  void exportPNG(std::string fn, gimg image, unsigned w, unsigned h)
  {	
    unsigned error = lodepng::encode(fn, image, w, h);
    if(error)
      std::cout << "lodepng error " << error << std::endl;
    std::cout << "exported to PNG: " << fn << std::endl;
  }
  
  struct Glyph {
    std::string name = "empty";
    unsigned w, h;
    AreaRB area;
    gimg g;
    Glyph() {}
    Glyph(std::string fn):
      name(fn){ trimName(); }
    Glyph(std::string fn, gimg fimg):
      name(fn), g(fimg) { trimName(); }
    Glyph(std::string fn, gimg fimg, unsigned wi, unsigned hi):
      name(fn), w(wi), h(hi), g(fimg)
    { trimName(); }
    void initArea()
    { // TODO
    }
    void trimName()
    {
      std::size_t ix = name.find(".png");
      if(ix != std::string::npos)
	name.erase(ix,4);
    }
  };

  typedef std::vector<Glyph> gword;
  
  struct GlyphMap
  {
    // holds all glyphs
    std::vector<Glyph> glyphs;

    // map of symbols to glyph names (filenames)
    gnmap tnames{{"", "empty"},
		 {" ", "space"},
		 {".","period"},{",","comma"},
		 {"-","hyphen"},
		 {"(","parenleft"},{")","parenright"},
		 {"0","zero"},{"1","one"},
		 {"2","two"},{"3","three"},
		 {"4","four"},{"5","five"},
		 {"6","six"},{"7","seven"},
		 {"8","eight"},{"9","nine"}};
    
    GlyphMap(gword gw): glyphs(gw) {}
    GlyphMap() { loadGlyphs(); }

    void operator()(gword gw) { glyphs = gw; }
    
    void loadGlyphs()
    {
      std::string fontpath = RB_ROADNETWORK_RESOURCES_PATH + "font/josefin-sans-font/pngs/quarter_size/";
      std::string custom_fontpath = RB_ROADNETWORK_RESOURCES_PATH + "font/josefin-sans-font/custom/";
      std::vector<std::string> font_paths{fontpath, custom_fontpath};
      for(const auto & fontdir : font_paths){
	for(const auto & entry : filesystem::directory_iterator(fontdir))
	  {
	    if(entry.path().extension() == ".png")
	      {
		std::string fnpath = entry.path();
		std::string fontfn = entry.path().filename();
		Glyph gtmp(fontfn);
		gtmp.g = readPNG(fnpath, &(gtmp.w), &(gtmp.h));
		glyphs.push_back(gtmp);
	      }
	  }
      }
      glyphs.push_back(Glyph("empty.png"));
    }
    
    Glyph getGlyph(std::string gname)
    {
      std::string tname = this->translate(gname); // attempt to translate
      auto git = std::find_if(glyphs.begin(), glyphs.end(),[tname](Glyph g){ return (g.name) == tname; });
      if(git == glyphs.end())
	{
	  std::cout << "WARNING: tried to get a glyph that doesnt exist! (gname=" << gname
		    << ")[tname=" << tname << "]" << std::endl;
	  insert_breakpoint();
	}
      return (*git);
    }
    
    std::vector<Glyph> getWordGlyphs(std::string gstr)
    {
      gword gout;
      std::string s;
      for(auto& tn : gstr)
	{
	  s = tn;
	  if(s != "")
	    gout.push_back(getGlyph(s));
	}
      return gout;
    }
    
    std::string translate(std::string skey)
    { // attempt to get corresponding name from tnames
      try { return tnames.at(skey); }
      catch(const std::exception& excep) {
	return skey;
      }
    }
    
  }; // end of GlyphMap

  struct Color {
    ccomp c[4];
    gimg cv;
    ccomp operator[] (int pi) const { return c[pi]; }
    ccomp& operator[] (int pi) { return c[pi]; }
    ccomp r(bool pre=false) {
      if(pre)
	return (c[0]/255.0) * (this->a()/255.0);
      return c[0];
    }
    void r(unsigned rnew) { c[0] = rnew; }
    ccomp g(bool pre=false)  {
      if(pre)
	return (c[1]/255.0) * (this->a()/255.0);
      return c[1];
    }
    void g(unsigned gnew) { c[1] = gnew; }
    ccomp b(bool pre=false)  {
      if(pre)
	return (c[2]/255.0) * (this->a()/255.0);
      return c[2];
    }
    void b(unsigned bnew) { c[2] = bnew; }
    ccomp a() { return c[3]; }
    void a(unsigned anew) { c[3] = anew; }
    ccomp cp(int i) {
      switch (i) {
      case 0:
	return r(true);
      case 1:
	return g(true);
      case 2:
	return b(true);
      case 3:
	return a();
      }
    }
    Color(ccomp rgb[3], ccomp alpha=255)
    {
      for(unsigned i=0; i < 3; i++)
	c[i] = rgb[i];
      c[3] = alpha;
      cv = gimg(c, c+4);
    }
    Color(int rr, int gg, int bb, int aa=255)
    {
      c[0] = rr;
      c[1] = gg;
      c[2] = bb;
      c[3] = aa;
      cv = gimg(c, c+4);
    }
    gimg setPixel(gimg& imc)
    {
      float A[4], B[4], D[4];
      for(unsigned k=0; k < 4; k++)
	{
	  A[k] = (float)this->c[k] / 255.0;
	  B[k] = (float)imc.at(k) / 255.0;
	}
      float aA = (float)A[3];
      float aB = (float)B[3];
      D[3] = (float)aA + (float)aB*(1.0 - (float)aA);
      for(unsigned m=0; m < 3; m++){
	  A[m] = (float)aA * A[m];
	  B[m] = (float)aB * B[m];
      }
      for(unsigned i=0; i < 3; i++)
	D[i] = (float)A[i] + (float)B[i]*(1.0-(float)aA);
      for(unsigned j=0; j < 4; j++)
	imc.at(j) = (float)(255.0 * (float)D[j]);
      gimg imo(imc);
      return imo;
    }
  };

  struct GridImageLayers {
    gimg imc; // color vector : combined layers
    std::vector<Color> layers;
    unsigned N() const { return (unsigned)this->layers.size(); }
    std::vector<Color>::iterator getFGIter() { return this->layers.begin(); }
    std::vector<Color>::iterator getBGIter() { return this->layers.end()-1; }
    gimg setupPixelLayers()
    {
      gimg imc = layers.back().cv;
      int i=0;
      i = (int)(this->N()) - 1;
      while(true){
	imc = this->layers.at(i).setPixel(imc);
	i = i - 1;
	if(i < 0)
	  break;
      }
      return imc;
    }
    int Nvisits = 0;
    bool isStart=false, isRoad=false, isAvail=false, patherHere=false, isBorder=false;
    const Color cBG = Color(150, 150, 150, 255);
    const Color cRoad = Color(80, 80, 80, 255);
    const Color cAvail = Color(50, 250, 60, 195);
    const Color cStart = Color(200, 0, 40, 255);
    const Color cPather = Color(255, 0, 255, 175);
    const Color cBorder = Color(0, 0, 0, 255);
    GridImageLayers(int nvisits, bool start, bool use, bool avail, bool pather=false, bool cbord=false):
      Nvisits(nvisits), isStart(start), isRoad(use), isAvail(avail), patherHere(pather), isBorder(cbord)
    {
      if(patherHere)
	this->layers.push_back(cPather);
      if(isStart){
	// std::cout << "...(GridImageLayers) --> current gridrect contains start point!\n";
	this->layers.push_back(cStart);
      }
      if(isBorder){
	// std::cout << "...(GridImageLayers) --> current gridrect is part of county border!\n";
	this->layers.push_back(cBorder);
      }
      if(isAvail){
	// std::cout << "...(GridImageLayers) --> current gridrect is available!\n";
	this->layers.push_back(cAvail);
      }
      if(isRoad){
	// std::cout << "...(GridImageLayers) --> current gridrect contains roads!\n";
	this->layers.push_back(cRoad);
      }
      this->layers.push_back(cBG);
    }
  };
  
}

#endif
