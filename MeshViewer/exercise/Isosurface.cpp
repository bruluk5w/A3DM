#include "Isosurface.h"

#include "exercise/taulaMC.hpp"
#include <cstdint>
#include <memory>
#include "utils.h"

namespace
{
	const uint8_t edge_to_vtx_idx[12 * 2] = {
		2, 6,
		3, 7,
		0, 4,
		1, 5,
		4, 6,
		5, 7,
		0, 2,
		1, 3,
		6, 7,
		4, 5,
		2, 3,
		0, 1,
	};
}
void initWithInvalidHandle(MyMesh::VertexHandle* h, int n) {
	for (int i = 0; i < n; ++i) {
		h[i] = MyMesh::VertexHandle();
	}
}

void extractIsoSurface(const Volume& vol, float t,  MyMesh& m) {
	m.clear();

	MyMesh::VertexHandle *vh;
	const uint16_t width = vol.width;
	const uint16_t sqWidth = width * width;
	MyMesh::VertexHandle* buffer_array[6] = {
		// vertices of edges along x axis of the last y step
		new MyMesh::VertexHandle[width],
		// vertices of edges along x axis of the current y step
		new MyMesh::VertexHandle[width],
		// vertices of edges along x axis of the last z step
		new MyMesh::VertexHandle[sqWidth],
		// vertices of edges along x axis of the current z step
		new MyMesh::VertexHandle[sqWidth],
		// vertices of edges along y axis of the last z step
		new MyMesh::VertexHandle[sqWidth],
		// vertices of edges along y axis of the current z step
		new MyMesh::VertexHandle[sqWidth],
	};

	initWithInvalidHandle(buffer_array[1], width);
	initWithInvalidHandle(buffer_array[2], sqWidth);
	initWithInvalidHandle(buffer_array[3], sqWidth);
	initWithInvalidHandle(buffer_array[4], sqWidth);
	initWithInvalidHandle(buffer_array[5], sqWidth);

	const float isovalue = vol.getIsovalue(t);
	const MyMesh::Point scale = { 1.0f / width, 1.0f / width, 1.0f / width };

	const size_t y_stride = width;
	const size_t z_stride = width * width;
	uint16_t prev_z = 0;
	Volume::sample_t* data = vol.data.get();
	for (uint16_t z = 1; z < width; ++z)
	{
		initWithInvalidHandle(buffer_array[0], width); // reset border
		uint16_t prev_y = 0;
		for (uint16_t y = 1; y < width; ++y)
		{
			Volume::sample_t value_table[8] = { 
				data[     z * z_stride +      y * y_stride], 0,
				data[     z * z_stride + prev_y * y_stride], 0,
				data[prev_z * z_stride +      y * y_stride], 0,
				data[prev_z * z_stride + prev_y * y_stride], 0,
			};

			uint8_t table_index = uint8_t(value_table[0] < isovalue) | uint8_t(value_table[2] < isovalue) << 2 | uint8_t(value_table[4] < isovalue) << 4 | uint8_t(value_table[6] < isovalue) << 6;
			uint16_t prev_x = 0;
			for (uint16_t x = 1; x < width; ++x)
			{

				value_table[1] = data[     z * z_stride +      y * y_stride + x];
				value_table[3] = data[     z * z_stride + prev_y * y_stride + x];
				value_table[5] = data[prev_z * z_stride +      y * y_stride + x];
				value_table[7] = data[prev_z * z_stride + prev_y * y_stride + x];
				
				float vtx_x[8] = { prev_x, x , prev_x ,      x , prev_x ,      x , prev_x ,      x };
				float vtx_y[8] = {      y, y , prev_y , prev_y ,      y ,      y , prev_y , prev_y };
				float vtx_z[8] = {      z, z ,      z ,      z , prev_z , prev_z , prev_z , prev_z };
				table_index |= uint8_t(value_table[1] < isovalue) << 1 | uint8_t(value_table[3] < isovalue) << 3 | uint8_t(value_table[5] < isovalue) << 5 | uint8_t(value_table[7] < isovalue) << 7;
				for (const std::array<uint8_t, 3>& tri : mc_table[table_index])
				{
#define MAKE_VERTEX(side) \
	const uint8_t edge_idx ## side = tri[side]; \
	const uint8_t buffer_idx ## side = edge_idx ## side >> 1; \
	const uint8_t offset ## side = edge_idx ## side & 0x01; \
	const uint8_t isVertical ## side = (edge_idx ## side & 0x08) >> 3; \
	const uint8_t is2DBuffer ## side = (uint8_t)((bool)(edge_idx ## side & 0x0c)); \
	const int pointIdx ## side = prev_x + (offset ## side & ~(isVertical ## side)) + is2DBuffer ## side * (prev_y + (offset ## side & isVertical ## side)) * vol.width; \
	vh = &buffer_array[buffer_idx ## side][pointIdx ## side]; \
	if (!vh->is_valid()) { \
		const uint8_t idxFrom ## side = edge_to_vtx_idx[ edge_idx ## side << 1    ]; \
		const uint8_t idxTo   ## side = edge_to_vtx_idx[(edge_idx ## side << 1) | 1]; \
		const Volume::sample_t valueFrom ## side = value_table[idxFrom ## side]; \
		const Volume::sample_t valueTo   ## side = value_table[idxTo   ## side]; \
		const float t ## side = abs(valueTo ## side - valueFrom ## side) < 0.00001f ? 0.0f : (isovalue - valueFrom ## side) / (float)(valueTo ## side - valueFrom ## side); \
		MyMesh::Point pt ## side = MyMesh::Point( \
			vtx_x[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_x[idxTo ## side], \
			vtx_y[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_y[idxTo ## side], \
			vtx_z[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_z[idxTo ## side]) * scale; \
		*vh = m.add_vertex(pt ## side); \
	} \
	MyMesh::VertexHandle vhandle ## side = *vh; \

#define REUSE_VERTEX_HANDLE(side) \
	if (!offset ## side && ~(edge_idx  ## side & 0x01)) { \
		 *vh = MyMesh::VertexHandle();\
	} \

					MAKE_VERTEX(0);
					m.set_normal(*vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(*vh)));
					m.set_color(*vh, (m.normal(*vh) + OpenMesh::Vec3f(1, 1, 1)) * .5f);
					REUSE_VERTEX_HANDLE(0);
					MAKE_VERTEX(1);
					m.set_normal(*vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(*vh)));
					m.set_color(*vh, (m.normal(*vh) + OpenMesh::Vec3f(1, 1, 1)) * .5f);
					REUSE_VERTEX_HANDLE(1);
					MAKE_VERTEX(2);
					m.set_normal(*vh, OpenMesh::vector_cast<OpenMesh::Vec3f>(m.point(*vh)));
					m.set_color(*vh, (m.normal(*vh) + OpenMesh::Vec3f(1, 1, 1)) * .5f);
					REUSE_VERTEX_HANDLE(2);

					MyMesh::FaceHandle face;
					face = m.add_face(vhandle0, vhandle1, vhandle2);
				}

				value_table[0] = value_table[1];
				value_table[2] = value_table[3];
				value_table[4] = value_table[5];
				value_table[6] = value_table[7];

				table_index = table_index >> 1 & 0x55;

				prev_x = x;
			}

			buffer_array[0][width - 1].invalidate(); // reset border
			std::swap(buffer_array[0], buffer_array[1]);

			prev_y = y;
		}

		for (int i = 0; i < width; ++i)
			buffer_array[2][width * i + width - 1].invalidate();  // reset border


		for (int i = sqWidth - width; i < sqWidth; ++i)
			buffer_array[4][i].invalidate();  // reset border

		std::swap(buffer_array[2], buffer_array[3]);
		std::swap(buffer_array[4], buffer_array[5]);


		prev_z = z;
	}


	for (int i = 0; i < countof(buffer_array); ++i)
	{
		delete[] buffer_array[i];
	}
}
