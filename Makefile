CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra -pedantic
TARGET = weighted_matcher
SRC = src/solver_driver.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET)
