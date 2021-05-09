#pragma once

#include <memory>

struct Volume
{
	using sample_t = float;

	Volume(const char* filename);
	float getIsovalue(float t) const;

	int width;
	int numSamples;

	sample_t low;
	sample_t high;
	std::unique_ptr<sample_t[]> data;

	bool valid;
};
