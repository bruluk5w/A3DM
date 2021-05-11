#ifndef __Isosurface_h_
#define __Isosurface_h_

#include "scene.h"
#include "Volume.h"

void extractIsoSurface(const Volume& vol, float t, MyMesh& mesh);

#endif