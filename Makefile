CXX = g++
CXXFLAGS = -O3 -Wall
# Update this line to include the 'src/' folder
SRC = src/workload.cpp
# This ensures the output goes into the 'bin/' folder
TARGET = bin/workload

all: $(TARGET)

$(TARGET): $(SRC)
	mkdir -p bin
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -rf bin
