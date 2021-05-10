#include "Isosurface.h"

#include "exercise/taulaMC.hpp"
#include <cstdint>
#include <memory>


namespace
{
	const uint8_t edge_to_vtx_idx[12 * 2] = {
		2, 6, // 4
		3, 7, // 6
		0, 4, // 0
		1, 5, // 2
		4, 6, // 8
		5, 7, // 9
		0, 2, // 10
		1, 3, // 11
		6, 7, // 5
		4, 5, // 1
		2, 3, // 7
		0, 1, // 3
	};

	//// first index is index of buffer, second parameter describes which of (x, y) to use to index the buffer (false->x;true->x,y), last number if the index shift to apply (todo: replace index shift in this table by proper naming of the edges to allow using the bits of the names)
	//const std::tuple<uint8_t, bool, uint8_t> edge_to_buffer_idx[12] = {
	//	{1, 0, 0}, // 0
	//	{2, 1, 0}, // 1
	//	{1, 0, 1}, // 2
	//	{3, 1, 0}, // 3
	//	{0, 0, 0}, // 4
	//	{2, 1, }, // 5
	//	{0, 0, 1}, // 6
	//	{, }, // 7
	//	{, }, // 8
	//	{, }, // 9
	//	{, }, // 10
	//	{, }, // 11
	//};
	//const uint8_t buffer_idx = edge_idx >> 1;
	//const uint8_t offset = edge_idx & 1;
	//const bool isVertical = edge_idx & 0x08;
	//const bool is2DBuffer = edge_idx & 0x0c;
	// int bufferIdx = x + offset & ~(isVertical) + (y + offset & (isVertical)) * vol.width
	// although loops start at one, indices here start at 0 (offsets are applied in the formula)
}
void initWithInvalidHandle(MyMesh::VertexHandle* h, int n) {
	for (int i = 0; i < n; ++i) {
		h[i] = MyMesh::VertexHandle();
	}
}

void extractIsoSurface(const Volume& vol, float t,  MyMesh& m) {
	m.clear();

	MyMesh::VertexHandle vh, vhandle[3];

	std::unique_ptr<MyMesh::VertexHandle[]> buffer_array[6] = {
		// vertices of edges along x axis of the last y step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width]),
		// vertices of edges along x axis of the current y step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width]),
		// vertices of edges along x axis of the last z step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width * vol.width]),
		// vertices of edges along x axis of the current z step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width * vol.width]),
		// vertices of edges along y axis of the last z step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width * vol.width]),
		// vertices of edges along y axis of the current z step
		std::unique_ptr<MyMesh::VertexHandle[]> (new MyMesh::VertexHandle[vol.width * vol.width])
	};

	initWithInvalidHandle(buffer_array[0].get(), vol.width);
	initWithInvalidHandle(buffer_array[1].get(), vol.width);
	initWithInvalidHandle(buffer_array[2].get(), vol.width * vol.width);
	initWithInvalidHandle(buffer_array[3].get(), vol.width * vol.width);
	initWithInvalidHandle(buffer_array[4].get(), vol.width * vol.width);
	initWithInvalidHandle(buffer_array[5].get(), vol.width * vol.width);

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

			uint8_t table_index = uint8_t(value_table[0] < isovalue) | uint8_t(value_table[2] < isovalue) << 2 | uint8_t(value_table[4] < isovalue) << 4 | uint8_t(value_table[6] < isovalue) << 6;

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
				table_index |= uint8_t(value_table[1] < isovalue) << 1 | uint8_t(value_table[3] < isovalue) << 3 | uint8_t(value_table[5] < isovalue) << 5 | uint8_t(value_table[7] < isovalue) << 7;
				for (const std::array<uint8_t, 3>&tri : mc_table[table_index])
				{
					face_vhandles.clear();

#define MAKE_VERTEX(side) \
	const uint8_t edge_idx ## side = tri[side]; \
	if (edge_idx ## side && false) { \
	} \
	else { \
		const uint8_t idxFrom ## side = edge_to_vtx_idx[ edge_idx ## side << 1    ]; \
		const uint8_t idxTo   ## side = edge_to_vtx_idx[(edge_idx ## side << 1) | 1]; \
		const Volume::sample_t valueFrom ## side = value_table[idxFrom ## side]; \
		const Volume::sample_t valueTo   ## side = value_table[idxTo   ## side]; \
		const float t ## side = abs(valueTo ## side - valueFrom ## side) < 0.00001f ? 0.0f : (isovalue - valueFrom ## side) / (float)(valueTo ## side - valueFrom ## side); \
		MyMesh::Point pt ## side = MyMesh::Point( \
			vtx_x[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_x[idxTo ## side], \
			vtx_y[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_y[idxTo ## side], \
			vtx_z[idxFrom ## side] * (1 - t ## side) + t ## side * vtx_z[idxTo ## side]) * scale; \
		vh = m.add_vertex( pt ## side  \
		); \
	} \
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
