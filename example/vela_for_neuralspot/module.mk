local_app_name := vela
local_src := $(wildcard $(subdirectory)/src/*.c)
local_src += $(wildcard $(subdirectory)/src/*.cc)
local_src += $(wildcard $(subdirectory)/src/*.cpp)
local_src += $(wildcard $(subdirectory)/src/*.s)
# local_src := $(wildcard $(subdirectory)/src/ethos-u-core-driver/src/*.c)
# local_src += $(wildcard $(subdirectory)/src/ethos-u-core-driver/src/*.cc)
# local_src += $(wildcard $(subdirectory)/src/ethos-u-core-driver/src/*.cpp)
# local_src += $(wildcard $(subdirectory)/src/ethos-u-core-driver/src/*.s)
includes_api += $(subdirectory)/src/ethos-u-core-driver-nogithub/include
local_bin := $(BINDIR)/$(subdirectory)
lib_prebuilt += $(subdirectory)/src/ethos-u-core-driver-nogithub/build/libethosu_core_driver.a
bindirs   += $(local_bin)
# sources   += $(local_src)
examples  += $(local_bin)/$(local_app_name).axf
examples  += $(local_bin)/$(local_app_name).bin
# mains     += $(local_bin)/src/$(local_app_name).o
$(eval $(call make-axf, $(local_bin)/$(local_app_name), $(local_src)))
