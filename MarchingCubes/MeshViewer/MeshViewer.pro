TEMPLATE = app
QT += opengl
QT += widgets
CONFIG += debug
CONFIG += warn_on
QMAKE_CXXFLAGS += -std=c++14 -D__USE_XOPEN

# Inputs:
INCLUDEPATH += .

# HEADERS += ./*.h
HEADERS = $$files(./*.h)
# SOURCES += ./*.cxx
SOURCES = $$files(./*.cxx)

LIBS += -lGLU
LIBS += -L/usr/local/lib -lOpenMeshCore -lOpenMeshTools

# Outputs:
TARGET = MeshViewer
MOC_DIR = build
OBJECTS_DIR = build
RCC_DIR = build

TARGET = MeshViewer
