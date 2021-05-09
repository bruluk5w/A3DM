#include "Isosurface.h"

#include "exercise/taulaMC.hpp"
#include <cstdint>


namespace
{
	const uint8_t edge_to_vtx_idx[12 * 2] = {
		0, 4,
		4, 5,
		1, 5,
		0, 1,
		2, 6,
		6, 7,
		3, 7,
		2, 3,
		4, 6,
		5, 7,
		0, 2,
		1, 3
	};
}

void extractIsoSurface(const Volume& vol, float t,  MyMesh& m) {
	m.clear();

	MyMesh::VertexHandle vh, vhandle[3];
	std::vector<MyMesh::VertexHandle>  face_vhandles;

	const float isovalue = vol.getIsovalue(t);
	const MyMesh::Point scale = { 1.0 / (double)vol.width, 1.0 / (double)vol.width, 1.0 / (double)vol.width };

	size_t y_stride = vol.width;
	size_t z_stride = vol.width * vol.width;
	uint16_t prev_z = 0;
	Volume::sample_t* data = vol.data.get();
	for (size_t z = 1; z < vol.width; ++z)
	{
		uint16_t prev_y = 0;
		for (size_t y = 1; y < vol.width; ++y)
		{
			Volume::sample_t value_table[8] = { 
				data[     z * z_stride +      y * y_stride], 0,
				data[     z * z_stride + prev_y * y_stride], 0,
				data[prev_z * z_stride +      y * y_stride], 0,
				data[prev_z * z_stride + prev_y * y_stride], 0,
			};

			uint8_t table_index = 
				uint8_t(value_table[0] < isovalue) | 
				uint8_t(value_table[2] < isovalue) << 2 | 
				uint8_t(value_table[4] < isovalue) << 4 | 
				uint8_t(value_table[6] < isovalue) << 6;

			uint16_t prev_x = 0;
			for (size_t x = 1; x < vol.width; ++x)
			{

				value_table[1] = data[     z * z_stride +      y * y_stride + x];
				value_table[3] = data[     z * z_stride + prev_y * y_stride + x];
				value_table[5] = data[prev_z * z_stride +      y * y_stride + x];
				value_table[7] = data[prev_z * z_stride + prev_y * y_stride + x];
				
				float vtx_x[8] = { prev_x, x , prev_x ,      x , prev_x ,      x , prev_x ,      x };
				float vtx_y[8] = {      y, y , prev_y , prev_y ,      y ,      y , prev_y , prev_y };
				float vtx_z[8] = {      z, z ,      z ,      z , prev_z , prev_z , prev_z , prev_z };
				table_index |= 
					uint8_t(value_table[1] < isovalue) << 1 |
					uint8_t(value_table[3] < isovalue) << 3 |
					uint8_t(value_table[5] < isovalue) << 5 |
					uint8_t(value_table[7] < isovalue) << 7;
				for (const std::array<uint8_t, 3>&tri : mc_table[table_index])
				{
					face_vhandles.clear();

#define MAKE_VERTEX(side) \
	const uint8_t idxFrom ## side = edge_to_vtx_idx[ tri[side] << 1    ]; \
	const uint8_t idxTo   ## side = edge_to_vtx_idx[(tri[side] << 1) | 1]; \
	const Volume::sample_t valueFrom ## side = value_table[idxFrom ## side]; \
	const Volume::sample_t valueTo   ## side = value_table[idxTo   ## side]; \
	const float t ## side = abs(valueTo ## side - valueFrom ## side) < 0.00001f ? 0.0f : (isovalue - valueFrom ## side) / (float)(valueTo ## side - valueFrom ## side); \
	MyMesh::Point pt ## side = MyMesh::Point( \
		vtx_x[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_x[idxTo ## side], \
		vtx_y[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_y[idxTo ## side], \
		vtx_z[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_z[idxTo ## side]) * scale; \
	vh = m.add_vertex( pt ## side  \
	); \
	vhandle[side] = vh; \
	face_vhandles.push_back(vhandle[side]);


					MAKE_VERTEX(0);
					// todo: calculate normal
					m.set_normal(vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(vh)));
					m.set_color(vh, (m.normal(vh) + OpenMesh::Vec3f(1, 1, 1)) * .5);
					MAKE_VERTEX(1);
					// todo: calculate normal
					m.set_normal(vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(vh)));
					m.set_color(vh, (m.normal(vh) + OpenMesh::Vec3f(1, 1, 1)) * .5);
					MAKE_VERTEX(2);
					// todo: calculate normal
					m.set_normal(vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(vh)));
					m.set_color(vh, (m.normal(vh) + OpenMesh::Vec3f(1, 1, 1)) * .5);
					
					MyMesh::FaceHandle face;
					face = m.add_face(face_vhandles);
				}

				value_table[0] = value_table[1];
				value_table[2] = value_table[3];
				value_table[4] = value_table[5];
				value_table[6] = value_table[7];

				table_index = table_index >> 1 & 0x55;

				prev_x = x;
			}

			prev_y = y;
		}

		prev_z = z;
	}

}
