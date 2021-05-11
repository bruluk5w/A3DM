TEMPLATE = app
QT += opengl
QT += widgets
CONFIG += release
CONFIG += warn_on
QMAKE_CXX = g++-7
QMAKE_CC = gcc-7
QMAKE_CXXFLAGS += -std=c++11 -D__USE_XOPEN

# Inputs:
INCLUDEPATH += .
INCLUDEPATH += /assig/sgi/include

HEADERS += ./*.h
SOURCES += ./*.cxx
HEADERS += ./exercise/*.h
HEADERS += ./exercise/*.hpp
SOURCES += ./exercise/*.cpp

LIBS += -lGLU
LIBS += -L/assig/sgi/lib -Wl,-rpath,/assig/sgi/lib/ -lOpenMeshCore -lOpenMeshTools

# Outputs:
TARGET = MeshViewer
MOC_DIR = build
OBJECTS_DIR = build
RCC_DIR = build

TARGET = MeshViewer