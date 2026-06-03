# Shared by every target
CXXFLAGS_COMMON := -O0 -g $(shell root-config --cflags)
LDLIBS          := $(shell root-config --libs)

# Parallel stages need pthreads
CXXFLAGS_PAR    := $(CXXFLAGS_COMMON) -pthread

# Extra ROOT libraries beyond root-config --libs defaults
LDLIBS_MINUIT   := -lMinuit

all: RecoverBeamSpot GetParticleDistributions SGMC

RecoverBeamSpot: recoverBeamSpot.cpp
	$(CXX) $(CXXFLAGS_COMMON) $< $(LDLIBS) $(LDLIBS_MINUIT) -o $@

GetParticleDistributions: getParticleDistributions.cpp
	$(CXX) $(CXXFLAGS_PAR) $< $(LDLIBS) -o $@

SGMC: sgmc.cpp
	$(CXX) $(CXXFLAGS_PAR) $< $(LDLIBS) -o $@

clean:
	rm -f RecoverBeamSpot GetParticleDistributions SGMC