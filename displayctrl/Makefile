CXX = g++
CXXFLAGS = -c -Wall -std=c++11 -pthread
LD = g++
LDFLAGS = -pthread

-include Makefile.local

ifeq ($(DEBUG), 1)
	CXXFLAGS += -g -O0
else
	CXXFLAGS += -O3 -DNDEBUG
endif

ALL_SRC = $(wildcard src/*.cpp)
ALL_OBJ = $(ALL_SRC:src/%.cpp=build/%.o)
BIN = build/displayctrl

.PHONY: all clean

all: $(BIN)

$(BIN): $(ALL_OBJ)
	$(LD) -o $@ $^ $(LDFLAGS)

build/%.o: src/%.cpp | build
	$(CXX) $(CXXFLAGS) -o $@ $<

build:
	mkdir $@

clean:
	rm -rf build/
