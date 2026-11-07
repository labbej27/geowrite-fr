# Assemble geoWrite autonome : noyau GEOS + souris 1351 + disque de travail.
V       := ../vendor
KERNAL  := $(V)/geos/build/bsw/kernal_combined.prg
CVT     := $(V)/geowrite/build/fr/geoWrite.cvt
OUT     := build

.PHONY: all clean
all: $(OUT)/geowrite.crt $(OUT)/documents.d64

$(KERNAL): FORCE
	python3 -I ../tools/mkfont.py $(V)/geos/kernal/bswfont/bswfont.s $(V)/geos/kernal/bswfont/bswfont_fr.inc >/dev/null
	python3 -I ../tools/mkfr.py
	python3 -I ../tools/mkicons.py
	# Ses regles ne suivent pas les .inc : tout recompiler.
	rm -rf $(V)/geos/build/bsw
	-$(MAKE) -C $(V)/geos VARIANT=bsw INPUT=mse1351 build/bsw/kernal_combined.prg
$(CVT): FORCE
	# Ses regles ne suivent pas les .inc : tout recompiler pour ne pas garder d'anciens textes.
	$(MAKE) -C $(V)/geowrite clean
	$(MAKE) -C $(V)/geowrite LOCALE=fr
	$(MAKE) -C $(V)/geowrite LOCALE=fr cvt
FORCE:

# Le noyau occupe les banques 1 a 6 de la cartouche (chaque banque : 8 Ko).
KERNEL_BANK := 1
DISK_BANK    = $(shell python3 -I -c "import os,sys;print(1+(os.path.getsize(sys.argv[1])-2+8191)//8192)" $(KERNAL))
KERNEL_PAGES = $(shell python3 -I -c "import os,sys;print((os.path.getsize(sys.argv[1])-2+255)//256)" $(KERNAL))

$(OUT)/crt.bin: crt.s crt.cfg $(KERNAL)
	@mkdir -p $(OUT)
	ca65 -D KERNEL_BANK=$(KERNEL_BANK) -D DISK_BANK=$(DISK_BANK) -D KERNEL_PAGES=$(KERNEL_PAGES) -o $(OUT)/crt.o crt.s
	ld65 -C crt.cfg -o $@ $(OUT)/crt.o

$(OUT)/geowrite.crt: $(OUT)/crt.bin $(CVT) $(OUT)/mps803.cvt ../tools/mkcrt.py
	python3 -I ../tools/mkcrt.py $(OUT)/crt.bin $(KERNAL) $@ $(CVT) $(OUT)/mps803.cvt

$(OUT)/mps803.cvt: mps803.s ../tools/mkprinter.py
	@mkdir -p $(OUT)
	ca65 -o $(OUT)/mps803.o mps803.s
	ld65 -t none -o $(OUT)/mps803.bin $(OUT)/mps803.o
	python3 -I ../tools/mkprinter.py $(OUT)/mps803.bin $@

# Disque vierge pour les documents ; ne sert jamais a ecraser celui de la SD.
$(OUT)/documents.d64:
	@mkdir -p $(OUT)
	c1541 -format "documents,gw" d64 $@ -silent on >/dev/null 2>&1
	python3 -I ../tools/geosdisk.py $@

clean:
	rm -rf $(OUT)
