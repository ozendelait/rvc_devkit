#ifndef UTILS_H
#define UTILS_H

#include <iostream>
#include <fstream>
#include <vector>
#include <stdint.h>
#include <png++/png.hpp>
#include <stdio.h>
#include <math.h>

bool imageFormat(std::string file_name,png::color_type col,size_t depth,int32_t width,int32_t height) {
  std::ifstream file_stream;
  file_stream.open(file_name.c_str(),std::ios::binary);
  png::reader<std::istream> reader(file_stream);
  reader.read_info();
  if (reader.get_color_type()!=col)  return false;
  if (reader.get_bit_depth()!=depth) return false;
  if (reader.get_width()!=width)     return false;
  if (reader.get_height()!=height)   return false;
  return true;
}

double statMean(std::vector< std::vector<double> > &errors,int32_t idx) {
  double err_mean = 0;
  for (int32_t i=0; i<errors.size(); i++)
    err_mean += errors[i][idx];
  return err_mean/(double)errors.size();
}

double statWeightedMean(std::vector< std::vector<double> > &errors,int32_t idx,int32_t idx_num) {
  double err = 0;
  double num = 0;
  for (int32_t i=0; i<errors.size(); i++) {
    err += errors[i][idx];
    num += errors[i][idx_num];
  }
  return err/std::max(num,1.0);
}

double statMin(std::vector< std::vector<double> > &errors,int32_t idx) {
  double err_min = 100000;
  for (int32_t i=0; i<errors.size(); i++)
    if (errors[i][idx]<err_min) err_min = errors[i][idx];
  return err_min;
}

double statMax(std::vector< std::vector<double> > &errors,int32_t idx) {
  double err_max = 0;
  for (int32_t i=0; i<errors.size(); i++)
    if (errors[i][idx]>err_max) err_max = errors[i][idx];
  return err_max;
}

#endif // UTILS_H

