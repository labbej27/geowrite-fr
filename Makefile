NAME   := demo
C64_IP ?= 192.168.1.128
PRG    := build/$(NAME).prg
SRC    := $(wildcard src/*.c) $(wildcard src/*.s)

.PHONY: all run deploy clean stock restore mousetest geowrite geowrite-run

all: $(PRG)

$(PRG): $(SRC)
	@mkdir -p build
	cl65 -t c64 -O -o $@ -m build/$(NAME).map --obj-path build $(SRC)
	@ls -l $@

run: $(PRG)
	x64sc -autostart $(PRG)

deploy: $(PRG)
	curl -fsS -m 15 -X POST --data-binary @$(PRG) \
	  -H 'Content-Type: application/octet-stream' \
	  http://$(C64_IP)/v1/runners:run_prg

stock:
	python3 -I tools/c64cfg.py stock

restore:
	python3 -I tools/c64cfg.py restore

mousetest:
	@mkdir -p build/mouse
	cl65 -t c64 -O -o build/mouse.prg --obj-path build/mouse tests/mouse/mouse.c
	curl -fsS -m 15 -X POST --data-binary @build/mouse.prg \
	  -H 'Content-Type: application/octet-stream' \
	  http://$(C64_IP)/v1/runners:run_prg

# Sources de mist64 + modifications du projet (patches/), au premier build.
vendor/geos/Makefile vendor/geowrite/Makefile:
	sh tools/setup-vendor.sh

geowrite: vendor/geos/Makefile vendor/geowrite/Makefile
	$(MAKE) -C geowrite

# Installe et lance la cartouche ; le disque de documents de la SD est conserve.
geowrite-run: geowrite
	sh tools/sd-install.sh

clean:
	rm -rf build
