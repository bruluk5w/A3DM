#include <QFileDialog>
#include "Volume.h"

#include <QMessageBox>
#include <QTextStream>

namespace {
    const int invalid = -1;
}

Volume::Volume(const char* filename) :
    width(invalid),
    numSamples(invalid),
    low(std::numeric_limits<float>::max()),
    high(std::numeric_limits<float>::lowest()),
    data(nullptr),
    valid(false)
{
    struct Closer {
        Closer(const char* filename) : file(filename) { }
        ~Closer() { file.close(); }
        QFile file;
    } file (filename);

    if (!file.file.open(QIODevice::ReadOnly)) {
        QMessageBox::information(0, "error", file.file.errorString());
        return;
    }

    QTextStream in(&file.file);
    if (in.atEnd()) {
        QMessageBox::information(0, "error", "File to does not state volume dimensions.");
        return;
    }

    bool ok = false;
    int intWidth = in.readLine().toInt(&ok);
    if (!ok) {
        width = invalid;
        QMessageBox::information(0, "error", "Could not read volume dimensions.");
        return;
    }

    numSamples = intWidth * intWidth * intWidth;

    const size_t maxDataSize = 4294967296; // max 4 GB
    if (intWidth <= 0 || numSamples * sizeof(float) > maxDataSize || intWidth > std::numeric_limits<uint16_t>::max() >> 2) {
        numSamples = invalid;
        QMessageBox::information(0, "error", "Invalid or too large volume dimensions.");
        return;
    }

    width = (uint16_t)intWidth;
    
    data = std::unique_ptr<float[]>(new float[numSamples]);
    int i = 0;
    while (i < numSamples && !in.atEnd())
    {
        float sample = in.readLine().toFloat(&ok);
        if (!ok) {
            width = numSamples = invalid;
            data = nullptr;
            QMessageBox::information(0, "error", "Invalid sample.");
            return;
        }

        data[i] = sample;
        if (sample < low) low = sample;
        if (sample > high) high = sample;

        ++i;
    }

    if (i != numSamples) {
        width = numSamples = invalid;
        low = std::numeric_limits<float>::max();
        high = std::numeric_limits<float>::lowest();
        data = nullptr;
        QMessageBox::information(0, "error", "Could not read enough data from file for stated dimensions.");
        return;
    }

    if (!in.atEnd()) {
        QMessageBox::information(0, "warning", "All samples read but file not fully read.");
    }

    valid = true;
}

float Volume::getIsovalue(float t) const
{
    if (!valid) {
        QMessageBox::information(0, "error", "Invalid volume model has no isovalue.");
        return 0;
    }

    return low + (high - low) * t;
}
