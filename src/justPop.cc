#ifdef _WIN32
#include <pthread.h>
#endif
#include <stdio.h>
#include <getopt.h>
#include <fstream>
#include <iostream>
#include <ctime>
#include <string>
#include <functional>
#include <experimental/array>
#include <experimental/filesystem>
/* experimental filesystem namespace */
namespace fs = std::experimental::filesystem;
#include "spdlog/spdlog.h"
#include "spdlog/sinks/basic_file_sink.h"
#include "spdlog/sinks/stdout_color_sinks.h"
#include "rbtypes.hpp"
using namespace rb;
#include "utils.hpp"
#include "grid.hpp"
#include "pre_gui.hpp"

void compute_population_table(float, std::string);
void compute_population_table(float tons_person, std::string filename)
{
  // create population table
  std::ostringstream text;
  text << "\\begin{tabular}{r|*{6}{l}}\n"
       << "County & State & 2010 & 2015 & 2020 & 2025 & 2030 \\\\ \n"
       << "\\hline\n";
  int totals[5] = {0};
  sort(counties.begin(), counties.end(), // sort counties alphabetically
       [](County c0, County c1)
       { return (c0.name.compare(c1.name) < 0); });
  for (County &cty : counties)
  {
    auto ctest0 = std::find_if_not(cty.pop.pops.begin(), cty.pop.pops.end(),
                                   [](int ptest)
                                   { return ptest == 0; });
    if (cty.avail && ctest0 != cty.pop.pops.end())
    {
      text << cty.name << " & " << cty.stinit;
      int tj = 0;
      for (int &cpc : cty.pop.pops)
      {
        text << " & " << std::to_string(cpc);
        totals[tj] += cpc;
        tj++;
      }
      text << "\\\\ \n";
    }
  }
  text << "\\\\ \n"
       << "\\hline\\hline\n"
       << "    Totals = & ";
  for (int i = 0; i < 5; i++)
  {
    text << " & " << totals[i];
  }
  text << "\\newline\n"
       << "\\end{tabular} \\\\ \n"
       << "\\begin{tabular}{l|l}\n\\hline\\hline\n\\newline\n"
       << " Population increase (2015 to 2030) & "
       << std::fixed << (totals[4] - totals[1]) << " \\\\ \n"
       << " Percent population increase & "
       << std::fixed << std::setprecision(1) << 100.0 * ((float)(totals[4] - totals[1]) / (float)totals[1]) << " \\\\ \n";

  std::cout << "(justPop.cc::compute_population_table) tons/person -> float: " << std::fixed << std::setprecision(3) << tons_person << "\n"
            << std::endl;

  text << " Tons needed by market (2015) & " << std::fixed << std::setprecision(3) << tons_person * totals[1] << "  (" << tons_person << " tons/person) \\\\ \n";
  text << " Tons needed by market (2030) & " << std::fixed << std::setprecision(3) << tons_person * totals[4] << "  (" << tons_person << " tons/person) \\\\ \n";
  text << " Increase in tons needed (2015 to 2030) & " << std::fixed << std::setprecision(3) << tons_person * (totals[4] - totals[1]) << " \\\\ \n";
  text << "\\end{tabular}\n";
  // save text to file
  std::ofstream ofs;
  ofs.open(filename);
  if (ofs.is_open())
  {
    std::cout << "opened poptable text file: " << filename << std::endl;
    ofs << text.str();
    std::cout << "wrote poptable text to file: " << filename << std::endl;
    ofs.close();
  }
}

void convert_tpp_str2float(std::string, float *);
void convert_tpp_str2float(std::string tons_str, float *tons_person)
{
  char *pos = nullptr;
  *tons_person = std::strtof(tons_str.c_str(), &pos);
  std::cout << "(convert_tpp_str2float) output: " << std::fixed << *tons_person << std::endl;
}

std::string setup_logging(int);
std::string setup_logging(int utres)
{
  std::string dbfn = RB_DATA_PATH + "/" + "debug-" + std::to_string(utres) + ".log";
  try 
    {
      // setup a logger with separate sinks (debugging -> file, warning -> console)
      auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
      console_sink->set_level(spdlog::level::warn);
      console_sink->set_pattern("[rb_roads] [%^%l%$] %v");
      
      auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(dbfn, true);
      file_sink->set_level(spdlog::level::trace);

      stdplog::sinks_init_list sinks_list{console_sink, file_sink};
      auto stdplog::logger::logger("rb_log", sinks_list); // instantiate the new logger
      logger.set_level(spdlog::level::debug);
      
      spdlog::flush_on(spdlog::level::info);  // flush every time an info-or-higher log event occurs
      spdlog::set_default_logger(logger);  // replace the default logger
    }
  catch (const spdlog::spdlog_ex &ex)
    {
      std::cout << "Log init failed: " << ex.what() << std::endl;
    }
  spdlog::get("rb_log")->info("Logger setup with filepath: " + dbfn);
  return dbfn;
}

int main(int argc, char *argv[])
{
  /*
    Setup timestamp, logging.
  */
  utres = std::time(nullptr);
  std::string dbfn = setup_logging(utres); // setup logging, return the log filepath
  /*
    Default params
  */
  std::string tons_str = "4.50";
  float tons_person;
  std::string filename = "poptable" + std::to_string(utres) + ".txt";
  std::string imfn = RB_DATA_PATH + "grid_images/gimg-" + std::to_string(utres) + ".png";
  std::cout << "Default nthreads: " << nthreads << std::endl;
  std::cout << "Default output filename: " << filename << std::endl;
  float zoom = 0.485;
  std::cout << "Default zoom: " << zoom << std::endl;
  float radius = 75e3;
  std::cout << "Default radius: " << radius << std::endl;
  PointRB stride(0.009, 0.009);

  int c;
  int cmd_coords = 0;

  while (1)
  {
    int option_index = 0;
    static struct option long_options[] = {{"radius", required_argument, 0, 'r'},
                                           {"stride", required_argument, 0, 's'},
                                           {"nthreads", required_argument, 0, 'h'},
                                           {"init_point", required_argument, 0, 'i'},
                                           {"tons-per-person", required_argument, 0, 't'},
                                           {"output-file-path", required_argument, 0, 'f'},
                                           {"lat", required_argument, 0, 'a'},
                                           {"lon", required_argument, 0, 'b'},
                                           {"zoom", required_argument, 0, 'z'}};

    c = getopt_long(argc, argv, "r:s:i:h:t:f:a:b:z:", long_options, &option_index);

    if (c == -1)
      break;

    std::cout << "input arg : [ -" << (char)(c) << " ]: " << optarg << std::endl;

    switch (c)
    {
    case 'z':
      zoom = (float)std::atof(optarg);
      std::cout << "zoom set (cmd) = " << zoom << std::endl;
      break;
    case 'b':
      start_point[0] = (float)std::atof(optarg);
      std::cout << "setting start lon... " << start_point[0] << std::endl;
      cmd_coords = 1;
      break;
    case 'a':
      start_point[1] = (float)std::atof(optarg);
      std::cout << "setting start lat... " << start_point[1] << std::endl;
      cmd_coords = 1;
      break;
    case 'i':
      std::cout << "setting start coord..." << std::endl;
      start_coord = global_coords(std::string(optarg));
      start_coord.name("start_" + start_coord.name());
      start_coord.toarr(start_xydeg);
      start_coord.merc().toarr(start_point.data());
      start_coord.print_coord();
      std::cout << "from cmd args: start_point = " << start_point[0]
                << ", " << start_point[1] << std::endl;
      cmd_coords = 2;
      break;
    case 'r':
      std::cout << "setting radius..." << std::endl;
      radius = (float)atof(optarg);
      break;
    case 's':
      std::cout << "setting stride..." << std::endl;
      stride[0] = stride[1] = (float)atof(optarg);
      std::cout << "stride set (cmd) = " << stride[0] << std::endl;
      rb::assert_msg(stride[0] == (float)atof(optarg), "(PointRB Error!) Stride was not properly set!");
      break;
    case 'h':
      std::cout << "setting nr threads..." << std::endl;
      nthreads = atoi(optarg);
      break;
    case 't':
      std::cout << "setting tons per person..." << std::endl;
      tons_str = std::string(optarg);
      std::cout << "...tons per person (str):" << tons_str << std::endl;
      convert_tpp_str2float(tons_str, &tons_person);
      std::cout << "...tons per person (float):" << std::fixed << std::setprecision(3) << tons_person << std::endl;
      break;
    case 'f':
      filename = std::string(optarg);
      std::cout << "output filename set: " << filename << std::endl;
    case '?':
      break;
    default:
      std::cout << "?? incorrect options, char code returned: " << c << std::endl;
      break;
    }
  }

  if (cmd_coords == 1)
  {
    std::cout << "cmd_coords=1: setting start_point, start_xydeg = mercator(start)..." << std::endl;
    start_xydeg[0] = start_point[0];
    start_xydeg[1] = start_point[1];
    start_point = sinusoidal(std::experimental::make_array(start_point[0], start_point[1]));
    std::cout << "startpoint (projected) = " << start_point[0] << ", " << start_point[1] << std::endl;
    pt_f tmp_start_pt;
    invsinusoidal(start_point[0], start_point[1], tmp_start_pt);
    std::cout << "startpoint (inverse) = " << tmp_start_pt[0] << ", " << tmp_start_pt[1] << std::endl;
  }
  else if (cmd_coords == 0)
  {
    start_coord = start_coord("start_elberton");
    start_coord.toarr(start_xydeg);
    start_coord.merc().toarr(start_point.data());
    std::cout << "Default start_coord: ";
    start_coord.print_coord();
    std::cout << "start_coord[0]=" << start_coord[0]
              << " , start_coord[1]=" << start_coord[1] << std::endl;
    std::cout << "start_point = " << start_point[0]
              << ", " << start_point[1] << std::endl;
  }
  std::cout << "setting up environment..." << std::endl;
  use_GL = false;
  // check that radius is big enough (should be in meters)
  rb::assert_msg((radius >= 1e3), "Queried road distance was less than the minimum supported (>=1km).");
  imfn = str_split(filename, ".txt").at(0) + ".png";
  std::cout << "image_fn = " << imfn << std::endl;
  PreGuiProcessor *processor = new PreGuiProcessor(radius, zoom, stride, imfn);
  bool road_params_changed = true;
  processor->done = false;
  auto pholder = NULL;
  auto *ppholder = &pholder;
  processor->process(&road_params_changed, &ppholder);
  writeGeoJSON(processor->r2pJSON, str_split(filename, ".txt").at(0) + ".json");
  compute_population_table(tons_person, filename);
  std::time_t tf = std::time(nullptr);
  std::cout << "Done! Computation took " << std::setprecision(3) << std::difftime(tf, utres) << " seconds.\n";
  fclose(stdout);
  std::cout << "\npopulation table (result):\n";
  std::ifstream pfs(filename);
  if (pfs.is_open())
  {
    char pcc = pfs.get();
    while (pfs.good())
    {
      std::cout << pcc;
      pcc = pfs.get();
    }
    pfs.close();
  }
#ifdef _WIN32
  pthread_exit(NULL);
#endif

  return 0;
}
