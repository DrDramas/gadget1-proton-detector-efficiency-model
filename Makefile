SRCDIR := src
BINDIR := bin

CXXFLAGS_COMMON := -O2 $(shell root-config --cflags)
LDLIBS          := $(shell root-config --libs)
CXXFLAGS_PAR    := $(CXXFLAGS_COMMON) -pthread

.PHONY: all clean
all: $(BINDIR)/RecoverBeamSpot $(BINDIR)/GetParticleDistributions $(BINDIR)/SGMC

$(BINDIR):
	mkdir -p $(BINDIR)

$(BINDIR)/RecoverBeamSpot: $(SRCDIR)/recoverBeamSpot.cpp | $(BINDIR)
	$(CXX) $(CXXFLAGS_COMMON) $< $(LDLIBS) -lMinuit -o $@

$(BINDIR)/GetParticleDistributions: $(SRCDIR)/getParticleDistributions.cpp | $(BINDIR)
	$(CXX) $(CXXFLAGS_PAR) $< $(LDLIBS) -o $@

$(BINDIR)/SGMC: $(SRCDIR)/sgmc.cpp | $(BINDIR)
	$(CXX) $(CXXFLAGS_PAR) $< $(LDLIBS) -o $@

clean:
	rm -rf $(BINDIR)