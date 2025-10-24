$(shell envSetupLocal.sh > /dev/null)
include $(shell get_top_dir.pl)make/.env.mk
# Set some variables to use throughout the Makefile
export TOP_DIR    := $(shell get_top_dir.pl)
export PROJECT    := $(shell get_project.pl)
export VALID_DIR  := $(TOP_DIR)validation/
export INC_DIR    := $(VALID_DIR)include/
export COMMON_DIR := $(VALID_DIR)common/
export REGGEN_DIR := $(VALID_DIR)reggen_tests/
export BIN_DIR    := $(VALID_DIR)bin/
export UTIL_DIR   := $(TOP_DIR)util/
export BOOTROM_DIR := $(TOP_DIR)bootloader/src/
export XTENSA_CORE=hifi5_bd7_axin_V5_pdv31b
#export XTTOOLS=$(PROJECT_PATH)/share/ip/cadence/tensilica/Xplorer/XtDevTools/install/tools/RI-2019.1-linux/XtensaTools

# ARM_TOOLCHAIN and GNU_TOOLCHAIN should already have been included via Makefile.toolchain by including Makefile

TOOLCHAIN ?= $(GNU_TOOLCHAIN)
ARMBAR ?= 0

# By default, don't build for DSP
DSP ?= 0

# By default, don't build for DSP
RSS ?= 0
RSS_TESTNAME ?= hello_world
RSS_TESTDIR ?= tests
RSS_OFFSET ?= 0x1F0000
#by default, don't cpp link
#TODO: unify linker steps
CPPLINK ?= 0

# Pass down any secure boot blob addrs

SECBOOT_BLOB_ADDR0 ?= 0
SECBOOT_BLOB_ADDR1 ?= 0

# Remove any current implicit rules and ensure intermediate files are kept
.SUFFIXES:
.SECONDARY:
.IMPLICIT:


# Define CPU target
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
CPUTARGET  =   --cpu=Cortex-M4.fp -D__FPU_PRESENT
#CPUTARGET   =   --cpu=Cortex-M4
else
# Using -mfloat-abi=hard doesn't work - no libgcc.a which uses hard FPU calling
# convention available.  softfp uses FPU, but soft (emulation) calling
# convention.
#CPUTARGET = -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -D__FPU_PRESENT -Dgcc
#CPUTARGET = -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=softfp -mthumb -D__FPU_PRESENT -Dgcc
CPUTARGET = -mcpu=cortex-m55 -mfpu=fpv5-sp-d16 -mfloat-abi=softfp -mthumb -D__FPU_PRESENT -D__GCC -fomit-frame-pointer -mcmse -mtune=cortex-m55 -march=armv8.1-m.main+mve.fp
endif

ifeq ($(ARMBAR),1)
CPUTARGET = -D__FPU_PRESENT
endif

# DSP0TARGET = --xtensa-system=$(PROJECT_PATH)/share/ip/cadence/tensilica/Xplorer/Installs/RI-2019.1-linux/hifi5_bd7_axin_V5_pdv31b --xtensa-core=hifi5_bd7_axin_V5_pdv31b --xtensa-params=
# DSP1TARGET = --xtensa-system=$(PROJECT_PATH)/share/ip/cadence/tensilica/Xplorer/Installs/RI-2019.1-linux/hifi5_bd7_axin_V5_pdv31b --xtensa-core=hifi5_bd7_axin_V5_pdv31b --xtensa-params=

# DSPLSPLOCAL=$(COMMON_DIR)/DSP/min-rt-local
# #DSPLSPLOCAL=$(COMMON_DIR)/DSP/HiFi5/hifi5_bd7_base_altmm/min-rt-local
# DSPLSPROM=$(COMMON_DIR)/DSP/min-rt-rom
# DSPCC      = $(XTTOOLS)/bin/xt-xcc
# DSPLD      = $(XTTOOLS)/bin/xt-xc++
# DSPOBJDUMP = $(XTTOOLS)/bin/xt-objdump
# DSPOBJCOPY = $(XTTOOLS)/bin/xt-objcopy

# CMSIS
CMSIS_PATH = $(PROJECT_PATH)/share/sw/CMSIS_CM55
CMSIS_PATH_VERIF = $(VALID_DIR)/tests/CMSIS/
DEVICE_PATH = ../tests/Device
DEVICE_INCPATH = ../tests/Device/ARM/exectb_mcu/Include

# ETHOS_U_CORE_DRIVER
ETHOSU85_PATH = $(PROJECT_PATH)/share/sw/ethos_u_core_driver
ETHOSU85_SRC_PATH = $(PROJECT_PATH)/share/sw/ethos_u_core_driver/src
ETHOSU85_LIB_PATH = $(PROJECT_PATH)/share/sw/ethos_u_core_driver/lib

ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
# ARM tools
CC       =   $(ARM_DS_BASE)/bin/armcc
AS       =   $(ARM_DS_BASE)/bin/armasm
LD       =   $(ARM_DS_BASE)/bin/armlink
XXD      =   xxd
MK_RDMEM = $(UTIL_DIR)/mk_rdmem.pl
FROMELF     = $(ARM_DS_BASE)/bin/fromelf
LIBPATH     = $(ARM_DS_BASE)/lib
INCPATH     = $(ARM_DS_BASE)/include
else
# GNU tools
#LIBS_PATH   = $(ARM_TOOLS_PATH)
#TOOLS_PATH  = $(ARM_TOOLS_PATH)/bin
#INCPATH     = $(ARM_TOOLS_PATH)/arm-none-eabi/include
LIBS_PATH   =  $(PROJECT_PATH)/share/sw/gcc/gcc-arm-none-eabi-10.3-2021.10
TFLM_PATH   =  $(PROJECT_PATH)/share/sw/tflm
TOOLS_PATH  = $(LIBS_PATH)/bin
INCPATH     = $(LIBS_PATH)/arm-none-eabi/include

CC          = $(TOOLS_PATH)/arm-none-eabi-gcc
CPP         = $(TOOLS_PATH)/arm-none-eabi-g++
AS          = $(TOOLS_PATH)/arm-none-eabi-as
LD          = $(TOOLS_PATH)/arm-none-eabi-ld

XXD      = xxd
MK_RDMEM = $(UTIL_DIR)/mk_rdmem.pl
OBJCOPY  = $(TOOLS_PATH)/arm-none-eabi-objcopy
OBJDUMP  = $(TOOLS_PATH)/arm-none-eabi-objdump
PADBIN   = $(UTIL_DIR)/padbin
LIBPATH  =  $(LIBS_PATH)

AMBIQSUITE_UTILS = /projects/validation/ambiqsuite/utils
endif

ifeq ($(ARMBAR),1)
#TOOLS_PATH = /opt/cadence/installs/XCELIUM1809/tools/systemc/gcc/bin
TOOLS_PATH = /usr/bin
LIBS_PATH  = /usr
INCPATH    = /usr/include

NOP      = : \#

CC       = $(TOOLS_PATH)/gcc
AS       = $(NOP)
LD       = $(TOOLS_PATH)/ld
XXD      = $(NOP)
MK_RDMEM = $(UTIL_DIR)/mk_rdmem.pl
OBJCOPY  = $(TOOLS_PATH)/objcopy
OBJDUMP  = $(NOP)
PADBIN   = $(NOP)
LIBPATH  = $(LIBS_PATH)
endif

#
# MCU compiler options
# 		 -Wall -pedantic 
COMMON_CCFLAGS =   $(CPUTARGET)             \
                -I $(INC_DIR)               \
                -I $(INC_DIR)MCU            \
                -I $(CMSIS_PATH)/Core/Include \
                -I $(CMSIS_PATH)/DSP/Include \
				-I $(ETHOSU85_PATH)/include \
                -I $(ETHOSU85_PATH)/src     \
				-I $(BOOTROM_DIR) \
				-I $(TFLM_PATH)/src/tflite-micro \
				-I $(TFLM_PATH)/src/tflite-micro/tensorflow/lite/micro/tools/make/downloads/flatbuffers/include \
				-I $(TFLM_PATH)/src/tflite-micro/tensorflow/lite/micro/tools/make/downloads/gemmlowp \
				-I $(INC_DIR)am_reg         \
				-I $(INC_DIR)am_reg_info    \
                -I $(INC_DIR)val_lib        \
                -I $(INC_DIR)TB_DEBUG       \
                -I $(INCPATH)               \
                -I $(DEVICE_PATH)           \
                -I $(DEVICE_INCPATH)        \
				-I $(INC_DIR)Nema           \
				-I $(INC_DIR)NemaDC        \
				-I $(VALID_DIR)uart        \
				-I $(VALID_DIR)otp         \
				-I $(VALID_DIR)npu	\
                -I $(VALID_DIR)npu/tiny_kws	\
				-Wmaybe-uninitialized \
				-g -c

ifeq ($(RSS),1)
COMMON_CCFLAGS += -DRSS_OFFSET=$(RSS_OFFSET)
endif

CPPFLAGS     =   $(COMMON_CCFLAGS)    \
				-DARM_TOOLCHAIN=0     \
				-DGNU_TOOLCHAIN=1     \
				-ffunction-sections   \
				-fdata-sections       \
				-fpermissive	      \
				-fno-exceptions       \
				-fno-rtti 	          \
				-fno-unwind-tables    \
				-MMD -MP              \
				-std=c++11	          \
				-mfpu=vfp	          \
				-DTF_LITE_STRIP_ERROR_STRINGS \
				-DTF_LITE_STATIC_MEMORY	      \
				-DTF_LITE_DISABLE_X86_NEON

CPPLDFLAGS	=                                    \
				-Wl,--gc-sections                \
				-Wl,--strip-discarded            \
				-Wl,-T,$(VALID_DIR)$(LDSCRIPT)   \
				-Wl,--entry=am_reset_isr

ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
CCFLAGS	=    $(COMMON_CCFLAGS)    \
			-DARM_TOOLCHAIN=1     \
			-DGNU_TOOLCHAIN=0     \
			--c99                 \
            --data_reorder        \
            --diag_suppress=2874

ifeq ($(CPUTARGET),--cpu=Cortex-M4.fp)
    CCFLAGS    +=  -DENABLE_FPU=1
endif

else
# GNU
CCFLAGS     =   $(COMMON_CCFLAGS)     \
		-DARM_TOOLCHAIN=0     \
		-DGNU_TOOLCHAIN=1     \
		-ffunction-sections   \
		-fdata-sections       \
		-MMD -MP              \
		-std=gnu99
endif
ifeq ($(ARMBAR),1)
CCFLAGS     =   $(COMMON_CCFLAGS) \
                -std=c99 \
		-fPIC \
		-DARMBAR
endif
ASFLAGS     =   $(CPUTARGET) --keep -g


# # DSP
# ASMFLAGS = -Wa,--no-l32r-flix
# ASRC = \
#    crt1.S\
#   reset-vector-xea2.S

# DSP0_CCFLAGS = -O0 -g \
# 	       -DDSP0 \
#                -c

# DSP1_CCFLAGS = -O0 -g \
# 	       -DDSP1 \
#                -c

# DSP0_OBJ_FILES = $(ASRC:.S=.dsp0.o)
# DSP1_OBJ_FILES = $(ASRC:.S=.dsp1.o)
# DSP_DEP_FILES  = $(ASRC:.S=.d)

ifneq (,$(findstring FORCE_ALL_CODE_IN_SRAM,$(CC_OPTS)))
    SRAMONLY = 1
endif

#
# Use the following options to select the appropriate scatter file.
# Note that these selections are overridden if SCATTERFILE is specified
# in the test's Makefile.
#
ifeq ($(SCATTERFILE),)
ifeq ($(SRAMONLY),1)
SCATTERFILE = scatter_file_contsram
else
SCATTERFILE = scatter_file
endif
endif

ifeq ($(LDSCRIPT),)
  ifeq ($(SRAMONLY),1)
   LDSCRIPT = contsram.ld
  else
   LDSCRIPT = default.ld
  endif
endif

# DSPLSP = $(DSPLSPROM)
# ifeq ($(DSP_BUILDROM),)
#   DSPLSP = $(DSPLSPLOCAL)
# endif
# DSP0LDFLAGS = -mlsp=$(DSPLSP) -Wl,-Map -Wl,$*.dsp0.map -lc

# DSP1LDFLAGS = -mlsp=$(DSPLSP) -Wl,-Map -Wl,$*.dsp1.map -lc

ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
LDFLAGS     =                                               \
                --first='boot_mcu.o(vectors)'               \
                --datacompressor=off                        \
                --scatter=$(VALID_DIR)$(SCATTERFILE)        \
                --info=totals,unused --map --list=$(*F).map \
                --libpath $(LIBPATH)
else
# GNU
# We have to use --gc-sections (in combination with -fdata-sections and -ffunction-sections, above)
# in order to keep code size down to something reasonable in comparison to ARM DS-5 compiler.  Prior
# to this change, .data sections exceeded some run-in-8kB-SRAM limits.
LDFLAGS     =                                           \
		--nmagic	\
		--gc-sections                           \
		-L {LIBS_PATH}/arm-none-eabi/lib	\
		--strip-discarded                       \
		-T $(VALID_DIR)$(LDSCRIPT)              \
		--entry am_reset_isr
endif

# DSPDEPS     +=  $(INC_DIR)DSP/xtos-internal.h           \
#                 $(INC_DIR)DSP/xtos-params.h             \
#                 $(INC_DIR)DSP/reent_bss.c               \
#                 $(INC_DIR)DSP/board_init.c

# DSP0_CCFLAGS += $(DSPDEPS)                              \
#                 -I $(INC_DIR)DSP
# DSP1_CCFLAGS += $(DSPDEPS)                              \
#                 -I $(INC_DIR)DSP

# Dependencies - add new include files to this list
# Purposely removed:    $(INC_DIR)MCU/gpio_regs.h
MCUDEPS     +=  $(BOOTROM_DIR)bl_nv_helpers_INTERNAL_ONLY.h \
                $(CMSIS_PATH)/Core/Include/core_yamin.h   \
				$(CMSIS_PATH_VERIF)/Include/core_yamin.h	\
                $(INC_DIR)MCU/mcu.h                     \
                $(INC_DIR)MCU/mcu_irq.h                 \
                $(INC_DIR)MCU/am_hal_interrupt.h        \
                $(INC_DIR)MCU/regs_base_addresses.h     \
				$(INC_DIR)val_lib/keys.h                \
				$(INC_DIR)val_lib/adc_lib.h             \
				$(INC_DIR)val_lib/ble_lib.h             \
                $(INC_DIR)val_lib/clk_gen_proto.h       \
                $(INC_DIR)val_lib/ctimer_lib.h          \
                $(INC_DIR)val_lib/timer_lib.h           \
                $(INC_DIR)val_lib/secure_ctimer_lib.h          \
                $(INC_DIR)val_lib/secure_timer_lib.h           \
				$(INC_DIR)val_lib/dc_lib.h              \
				$(INC_DIR)val_lib/dispphy_lib.h         \
				$(INC_DIR)val_lib/flash_data_byte.h     \
				$(INC_DIR)val_lib/flash_data.h          \
                $(INC_DIR)val_lib/flash_lib.h           \
                $(INC_DIR)val_lib/gpio_lib.h            \
                $(INC_DIR)val_lib/gpu_lib.h             \
				$(INC_DIR)val_lib/i3c_lib.h             \
                $(INC_DIR)val_lib/mmu_lib.h             \
				$(INC_DIR)val_lib/ethosu85nummacs256a_lib.h             \
                $(INC_DIR)val_lib/lm_lib.h              \
                $(INC_DIR)val_lib/mcu_ctrl_lib.h        \
                $(INC_DIR)val_lib/mspi_lib.h            \
                $(INC_DIR)val_lib/pdm_lib.h             \
                $(INC_DIR)val_lib/pnm_lib.h             \
                $(INC_DIR)val_lib/power_lib.h           \
                $(INC_DIR)val_lib/reset_lib.h           \
                $(INC_DIR)val_lib/rtc_lib.h             \
                $(INC_DIR)val_lib/secure_rtc_lib.h      \
                $(INC_DIR)val_lib/uart_lib.h            \
                $(INC_DIR)val_lib/val_lib.h             \
                $(INC_DIR)MCU/ctimer_patlib.h           \
                $(INC_DIR)MCU/clk_gen.h                 \
                $(INC_DIR)MCU/clk_gen_regs.h            \
                $(INC_DIR)MCU/periph_crm_regs.h         \
                $(INC_DIR)MCU/timer_regs.h              \
                $(INC_DIR)MCU/stimer_regs.h             \
                $(INC_DIR)MCU/uart_regs.h               \
                $(INC_DIR)MCU/control_regs.h            \
                $(INC_DIR)MCU/vcomp_regs.h              \
                $(INC_DIR)MCU/adc_regs.h                \
                $(INC_DIR)MCU/security_regs.h           \
                $(INC_DIR)MCU/pdm_regs.h                \
                $(INC_DIR)MCU/rstgen_regs.h             \
                $(INC_DIR)MCU/wdt_regs.h                \
                $(INC_DIR)MCU/secure_wdt_regs.h         \
                $(INC_DIR)MCU/mspi_regs.h               \
                $(INC_DIR)MCU/mmu_regs.h                \
				$(INC_DIR)MCU/ethosu85nummacs256a_regs.h                \
                $(INC_DIR)MCU/flash_controller.h        \
                $(INC_DIR)MCU/system_mcu.h              \
				$(INC_DIR)MCU/mram_regs.h               \
				$(INC_DIR)am_reg/am_reg_adc.h 			\
				$(INC_DIR)am_reg/am_reg_adc_tb.h 		\
				$(INC_DIR)am_reg/am_reg_sec_tb.h 		\
				$(INC_DIR)am_reg/am_reg_usb_tb.h 		\
				$(INC_DIR)am_reg/am_reg_clkgen.h 		\
				$(INC_DIR)am_reg/am_reg_timer.h 		\
				$(INC_DIR)am_reg/am_reg_ctimer_tb.h 	\
				$(INC_DIR)am_reg/am_reg_extslv.h 		\
				$(INC_DIR)am_reg/am_reg_gpio.h 			\
				$(INC_DIR)am_reg/am_reg_gpio_tb.h 		\
				$(INC_DIR)am_reg/am_reg_i3c.h 		    \
				$(INC_DIR)am_reg/am_reg_i3c_tb.h 		\
                $(INC_DIR)am_reg/am_reg_mmu.h 	    	\
                $(INC_DIR)am_reg/am_reg_mmu_tb.h    	\
				$(INC_DIR)am_reg/am_reg_ethosu85nummacs256a.h 	    	\
                $(INC_DIR)am_reg/am_reg_ethosu85nummacs256a_tb.h    	\
                $(INC_DIR)am_reg/am_reg_iom.h 			\
				$(INC_DIR)am_reg/am_reg_ioslave_tb.h 	\
				$(INC_DIR)am_reg/am_reg_mcuctrl.h 		\
				$(INC_DIR)am_reg/am_reg_mcuctrlpriv.h 	\
				$(INC_DIR)am_reg/am_reg_mspi.h 			\
				$(INC_DIR)am_reg/am_reg_mspi_tb.h 		\
				$(INC_DIR)am_reg/am_reg_mram.h 			\
				$(INC_DIR)am_reg/am_reg_pdm.h 			\
				$(INC_DIR)am_reg/am_reg_pdm_tb.h 		\
				$(INC_DIR)am_reg/am_reg_pwrctrl.h 		\
				$(INC_DIR)am_reg/am_reg_rstgen.h 		\
				$(INC_DIR)am_reg/am_reg_rstgen_tb.h 	\
				$(INC_DIR)am_reg/am_reg_rtc.h 			\
				$(INC_DIR)am_reg/am_reg_secure_rtc.h 	\
				$(INC_DIR)am_reg/am_reg_security.h 		\
				$(INC_DIR)am_reg/am_reg_uart.h 			\
				$(INC_DIR)am_reg/am_reg_uart_tb.h 		\
				$(INC_DIR)am_reg/am_reg_vcomp.h 		\
				$(INC_DIR)am_reg/am_reg_vcomp_tb.h 		\
				$(INC_DIR)am_reg/am_reg_info_tb.h 		\
				$(INC_DIR)am_reg/am_reg_wdt.h 			\
				$(INC_DIR)am_reg/am_reg_secure_wdt.h 	\
                $(INC_DIR)MCUTests.h                    \
                $(INC_DIR)MCUConfig.h                   \
                $(INC_DIR)TB_DEBUG/tb_debug.h           \
                $(INC_DIR)TB_DEBUG/tb_components.h      \
                $(INC_DIR)TB_DEBUG/clk_gen_tb.h         \
                $(INC_DIR)MCU/ioslave_tb_regs.h			\
                $(INC_DIR)MCU/mspi_tb_regs.h       		\
                $(INC_DIR)MCU/i3c_tb_regs.h       		\
				$(INC_DIR)MCU/mmu_tb_regs.h       		\
				$(INC_DIR)MCU/ethosu85nummacs256a_tb_regs.h       		\
                $(INC_DIR)MCU/gpio_tb_regs.h       		\
                $(INC_DIR)MCU/vcomp_tb_regs.h      		\
                $(INC_DIR)MCU/adc_tb_regs.h        		\
                $(INC_DIR)MCU/sec_tb_regs.h        		\
                $(INC_DIR)MCU/usb_tb_regs.h        		\
                $(INC_DIR)MCU/rstgen_tb_regs.h     		\
                $(INC_DIR)MCU/uart_tb_regs.h       		\
                $(INC_DIR)MCU/extslv_regs.h        		\
                $(INC_DIR)TB_DEBUG/ioslave_cmds_proto.h \
				$(INC_DIR)/../../bootloader/src/bl_nv_helpers_INTERNAL_ONLY.h

#                $(INC_DIR)MCU/ioslave_tb_regs.h    	\
#                $(INC_DIR)MCU/mspi_tb_regs.h       	\
#                $(INC_DIR)MCU/gpio_tb_regs.h       	\
#                $(INC_DIR)MCU/vcomp_tb_regs.h      	\
#                $(INC_DIR)MCU/adc_tb_regs.h        	\
#                $(INC_DIR)MCU/rstgen_tb_regs.h     	\
#                $(INC_DIR)MCU/uart_tb_regs.h       	\
#                $(INC_DIR)MCU/extslv_regs.h        	\

#COMMON_DSPOBJS = dsp_lib.o
CMSIS_LIB=$(CMSIS_PATH)/DSP/Source/builddir/libCMSISDSP_GNU.a
ETHOSU85_LIB = $(ETHOSU85_LIB_PATH)/libethosu_core_driver.a

# Build val_lib.a for current toolchain
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
  VAL_LIB=$(COMMON_DIR)/bin-arm/val_lib.a
else
  VAL_LIB=$(COMMON_DIR)/bin-gcc/val_lib.a
endif

ifeq ($(ARMBAR),1)
  VAL_LIB=$(COMMON_DIR)/armbar/val_lib.a
endif


ifeq ($(BARE_BONES),1)
COMMON_MCUOBJS = boot_mcu.o      \
				 mcuinit_opts.o  \
                 system_mcu.o

    CCFLAGS    +=  -DBARE_BONES=1 -DNOMSGS

else
COMMON_MCUOBJS = boot_mcu.o     \
				mcuinit_opts.o  \
				am_hal_interrupt.o \
                system_mcu.o    \
                retarget_mcu.o  \
                ctimer_patlib.o \
				iom_lib.o	\
				i2s_lib.o	\
                ioslave_cmds.o  \
				$(TFLM_PATH)/lib/tflite-m55.a \
                $(VAL_LIB) \
                $(CMSIS_LIB)
endif

ifeq ($(ARMBAR),1)
COMMON_MCUOBJS =  $(VAL_LIB) \
		  		mcuinit_opts.o  \
	          	ioslave_cmds.o  \
		  		iom_lib.o
endif

ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
MCUOBJS     =   $(COMMON_MCUOBJS)
else
MCUOBJS     =   $(COMMON_MCUOBJS) \
		startup_gcc.o \
		$(LIBPATH)/arm-none-eabi/lib/thumb/v8-m.main+fp/softfp/libm.a	\
		$(LIBPATH)/arm-none-eabi/lib/thumb/v8-m.main+fp/softfp/libc.a	\
		$(LIBPATH)/lib/gcc/arm-none-eabi/10.3.1/thumb/v8-m.main+fp/softfp/libgcc.a
endif
ifeq ($(ARMBAR),1)
MCUOBJS     =   $(COMMON_MCUOBJS)
endif

COREMARK_DEPS   = core_portme.o \
                  core_util.o \
                  core_matrix.o \
                  core_list_join.o \
                  core_state.o \
                  core_main.o

#
# Dhrystone specific compiler options
#

# Must use MSC_CLOCK unless we have another timer for dhrystone
#CCFLAGS     +=  -DMSC_CLOCK -DITERATIONS=1

# Disable printing from Dhrystone if user set CM4_PRINTF to 0
ifeq ($(CM4_PRINTF),0)
    CCFLAGS     +=  -DNOMSG
endif

#
# If doing a Coremark TCF dump, set ITERATIONS to 1.
# #### NOTE: THIS NO LONGER WORKS BECAUSE SIM_OPTS MAY CONTAIN MORE THAN
# +DUMPTCF.  THIS IS NOW IMPLEMENTED VIA CORE_ITER DEFINE.
#ifeq ($(SIM_OPTS),+DUMPTCF)
#    CCFLAGS     +=  -DITERATIONS=1
#endif

#
# Performance options
#
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
OPTIMIZATION_FLAGS  ?= -O2 -Otime -Ono_autoinline -Ono_inline
else
# GNU
OPTIMIZATION_FLAGS  ?= -O2 -fno-inline
endif

CCFLAGS += $(OPTIMIZATION_FLAGS)

# Place users' flags last so that they can override OPTIMIZATION_FLAGS, for example
CCFLAGS += $(CC_OPTS)


################################################################################
#
# Rule deck
#
# ALL_TESTS = $(RUN_IN_FLASH) $(RUN_IN_SRAM)

## Include MTB test if source is found
##  ifeq ($(shell ls mtb.c),mtb.c)
## ALL  += mtb
##  endif

all: mcudeps_check ${ALL_TESTS}
	@echo Made all.

mcudeps_check: $(MCUDEPS)
	@echo "---------" $(ARM_TOOLCHAIN)
#	@echo "ERROR... mcudeps_check failed"
#	@for f in $(MCUDEPS); do echo "     file: $$f"; ls -al $$f;  done
#	@for f in $(MCUDEPS); do if [ ! -f "$$f" ]; then echo "$$f Missing"; fi; done
#	ERROR  Dependencies not present

################################################################################
#
# MCU
#

# Dummy target to cause mcuinit_opts.c, iom_lib.c, and ioslave_cmds.c to always get rebuilt (since they are dependent on CC_OPTS="-D*")
.FORCE:

.PHONY: .FORCE


mcuinit_opts.o: ../common/MCU/mcuinit_opts.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

# Boot file - vectors (.FORCE because stack can move with different defines)
boot_mcu.o: ../common/MCU/boot_mcu.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

# CMSIS System Initialization
system_mcu.o:   ../common/MCU/system_mcu.c $(MCUDEPS)
			@$(CC) $(CCFLAGS) -o $@ $<

# GNU only - vectors (.FORCE because stack can move with different defines)
startup_gcc.o:   ../common/MCU/startup_gcc.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

# GNU only - (.FORCE due to PUT_CODE_IN_SRAM)
am_util_stdio.o:   ../common/MCU/am_util_stdio.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

am_hal_interrupt.o: ../common/MCU/am_hal_interrupt.c $(MCUDEPS)	.FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

#MCUTests.o: ../common/MCUTests.c $(MCUDEPS) .FORCE
#			@$(CC) $(CCFLAGS) -o $@ $<

retarget_mcu.o: ../common/retarget_mcu.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

ctimer_patlib.o:  ../ctimer/ctimer_patlib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

mcu_ctrl_lib.o:  ../common/val_lib/mcu_ctrl_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

ioslave_cmds.o: ../common/MCU/ioslave_cmds.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

iom_lib.o: ../iom/iom_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

ioslave_lib.o: ../ioslave/ioslave_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

i2s_lib.o: ../i2s/i2s_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

pi_lib.o: ../math/pi_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

vcomp_lib.o: ../vcomp/vcomp_lib.c $(MCUDEPS) .FORCE
			@$(CC) $(CCFLAGS) -o $@ $<

# make keys.o TOOLCHAIN=0
keys.o: common/val_lib/keys.c $(MCUDEPS) .FORCE
			@bsub -I -XF -q compile $(CC) $(CCFLAGS) -o $@ $<

################################################################################
#
# Dhrystone Test - Requires multiple test source files
#

dhry_1.o:   dhry_1.c dhry.h $(MCUDEPS)
		$(CC) $(CCFLAGS) -o $@ $<

dhry_2.o:   dhry_2.c dhry.h $(MCUDEPS)
		$(CC) $(CCFLAGS) -o $@ $<

dhry.elf:   dhry_1.o dhry_2.o $(MCUOBJS)
		$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ dhry_1.o dhry_2.o $(MCUOBJS)

################################################################################
#
# Secure boot ROM sandbox
#

hello_world.mcu.bin: hello_world.axf
	rm -rf $@ $@.dir
	$(FROMELF) --bin -o $@ $<
	mv $@ $@.dir
	cp $@.dir/MCU_MRAM $@

hello_world.mcu.txt: hello_world.axf
	$(FROMELF) -cedrst -o $@ $<

################################################################################
#
# Coremark Test - Requires multiple test source files
#

#coremark.elf:   mcu_ctrl_lib $(COREMARK_DEPS) $(MCUOBJS)
coremark_flash.mcu.elf:   $(COREMARK_DEPS) $(MCUOBJS)
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ $^
else
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map coremark.map -o $@ $^
endif
coremark_xip.mcu.elf:   $(COREMARK_DEPS) $(OTHER_OBJS)  $(MCUOBJS)
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map coremark.map -o $@ $^

coremark_tcm.mcu.elf:   $(COREMARK_DEPS) $(MCUOBJS)
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ $^
else
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map coremark.map -o $@ $^
endif
coremark_sram.mcu.elf:   $(COREMARK_DEPS) $(MCUOBJS)
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ $^
else
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map coremark.map -o $@ $^
endif
coremark_tcmsram.mcu.elf:   $(COREMARK_DEPS) $(MCUOBJS)
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ $^
else
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map coremark.map -o $@ $^
endif

#mcu_ctrl_lib:
#	cd ../mcu_ctrl
#	make

################################################################################
#
# Pattern rules for all other tests
#

# %.dsp0.o : %.S .FORCE
# 	$(DSPLD) $(DSP0_CCFLAGS) $(ASMFLAGS)  -o $@ $<

# %.dsp0.o:    %.c .FORCE
# 	$(DSPCC) $(DSP0_CCFLAGS) -o $@ $<

##########################################################################
# Commenting out DSP1 build for now since this will need a lot more work #
##########################################################################
# %.dsp1.o : %.S .FORCE
# 	$(DSPLD) $(DSP1_CCFLAGS) $(ASMFLAGS)  -o $@ $<

# %.dsp1.o:    %.c .FORCE
# 	$(DSPCC) $(DSP1_CCFLAGS) -o $@ $<
#########################################################################

# For normal compile binaries (note .FORCE to rebuild .c file in case -D defines changed)
%.mcu.o:    %.c $(MCUDEPS) .FORCE
	cd ../security;make blob.bin
	$(CC) $(CCFLAGS) -o $@ $<

%.mcu.o:    %.cc $(MCUDEPS) .FORCE
	cd ../security;make blob.bin
	$(CPP) $(CPPFLAGS) -o $@ $<

# For ARMBAR binaries (note .FORCE to rebuild .c file in case -D defines changed)
%.armbar.o:    %.c $(MCUDEPS) .FORCE
	cd ../security;make blob.bin
	$(CC) $(CCFLAGS) -o $@ $<
	$(OBJCOPY) --redefine-sym main=test_main $*.armbar.o

%.o:    %.c $(MCUDEPS) .FORCE
	cd ../security;make blob.bin
	$(CC) $(CCFLAGS) -o $@ $<

%.o:    %.cc $(MCUDEPS) .FORCE
	cd ../security;make blob.bin
	$(CPP $(CPPFLAGS) -o $@ $<

# %.dsp0.elf:  %.dsp0.o $(DSP0_OBJ_FILES)
# 	@echo $(DSPLD) $(DSP0LDFLAGS) -o $@ $*.dsp0.o $(DSP0_OBJ_FILES)
# 	$(DSPLD) $(DSP0LDFLAGS) -o $@ $*.dsp0.o $(DSP0_OBJ_FILES)

##########################################################################
# Commenting out DSP1 build for now since this will need a lot more work #
##########################################################################
# %.dsp1.elf:  %.dsp1.o $(DSP1_OBJ_FILES)
# 	$(DSPLD) $(DSP1LDFLAGS) -o $@ $*.dsp1.o $(DSP1_OBJ_FILES)
#########################################################################

OTHER_OBJS += ../keys.o
OTHER_OBJS += $(ETHOSU85_LIB)

%.mcu.elf:  %.mcu.o $(OTHER_OBJS) $(MCUOBJS)
	@echo "OTHER_OBJS=$(OTHER_OBJS) MCUOBJS=$(MCUOBJS)"
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -o $@ $< $(OTHER_OBJS) $(MCUOBJS)
else

ifeq ($(CPPLINK),1)
	$(CPP) $(CPPLDFLAGS) $(EXTRA_LDFLAGS) $(CPUTARGET) --specs=rdimon.specs -fno-unwind-tables -fno-exceptions -fno-rtti -Xlinker -Map=$*.map -o $@ $< $(OTHER_OBJS) $(MCUOBJS)
else
	$(LD) $(LDFLAGS) $(EXTRA_LDFLAGS) -Map $*.map -o $@ $< $(OTHER_OBJS) $(MCUOBJS)
endif

endif

$(VAL_LIB): $(wildcard $(COMMON_DIR)/val_lib/*.c) $(wildcard $(INC_DIR)/val_lib/*.h) $(BOOTROM_DIR)bl_nv_helpers_INTERNAL_ONLY.h .FORCE
# ifeq ($(RSS),0)
#	@echo 	make -C $(VALID_DIR)/rss/$(RSS_TESTDIR) -s $(RSS_TESTNAME)
#	make -C $(VALID_DIR)/rss/$(RSS_TESTDIR) -s $(RSS_TESTNAME)
# endif
	make -C $(COMMON_DIR)

# %.dsp0.bin:  %.dsp0.elf
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -R.dsp0.xip                   $< $@
# 	$(PADBIN) $@
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -j.dsp0.xip --reverse-bytes=4 $< $@.dsp0.xip
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -j.dsp0.xip                   $< $@.dsp0.xip_le

# ##########################################################################
# # Commenting out DSP1 build for now since this will need a lot more work #
# ##########################################################################
# %.dsp1.bin:  %.dsp1.elf
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -R.dsp1.xip                   $< $@
# 	$(PADBIN) $@
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -j.dsp1.xip --reverse-bytes=4 $< $@.dsp1.xip
# 	$(DSPOBJCOPY) --xtensa-core=$(XTENSA_CORE) -Obinary -j.dsp1.xip                   $< $@.dsp1.xip_le
# #########################################################################

# %.dsp0.txt:  %.dsp0.elf
# 	$(DSPOBJDUMP) -D $< > $@

##########################################################################
# Commenting out DSP1 build for now since this will need a lot more work #
##########################################################################
# %.dsp1.txt:  %.dsp1.elf
# 	$(DSPOBJDUMP) -D $< > $@
# ##########################################################################

# %.dsp0.rcf:  %.dsp0.bin %.dsp0.txt
# 	$(XXD) -b -c4 $< | awk '{print $$5$$4$$3$$2;}' > $@

# ##########################################################################
# # Commenting out DSP1 build for now since this will need a lot more work #
# ##########################################################################
# %.dsp1.rcf:  %.dsp1.bin %.dsp1.txt
# 	$(XXD) -b -c4 $< | awk '{print $$5$$4$$3$$2;}' > $@
# ##########################################################################

# # dump out dat.xip file compatible with MSPI_PRELOAD make run option
# %.dsp0.dat:  %.dsp0.bin
# 	$(MK_RDMEM) $< $@
# 	if [ -e $<.xip ]; then od -t x1 -v -Anx -w4 $<.xip > $@.xip; od -t x1 -v -Anx -w4 $<.xip_le > $@.xip_le; fi

# ##########################################################################
# # Commenting out DSP1 build for now since this will need a lot more work #
# ##########################################################################
# %.dsp1.dat:  %.dsp1.bin
# 	$(MK_RDMEM) $< $@
# 	if [ -e $<.xip ]; then od -t x1 -v -Anx -w4 $<.xip > $@.xip; od -t x1 -v -Anx -w4 $<.xip_le > $@.xip_le; fi
# ##########################################################################

%.mcu.dat:  %.mcu.bin
	$(MK_RDMEM) $< $@
	if [ -e $<.xip ];  then od -t x1 -v -Anx -w4 $<.xip  > $@.xip;  od -t x1 -v -Anx -w4 $<.xip_le  > $@.xip_le;  fi
	if [ -e $<.x1ip ]; then od -t x1 -v -Anx -w4 $<.x1ip > $@.x1ip; od -t x1 -v -Anx -w4 $<.x1ip_le > $@.x1ip_le; fi
	if [ -e $<.x2ip ]; then od -t x1 -v -Anx -w4 $<.x2ip > $@.x2ip; od -t x1 -v -Anx -w4 $<.x2ip_le > $@.x2ip_le; fi
	if [ -e $<.x3ip ]; then od -t x1 -v -Anx -w4 $<.x3ip > $@.x3ip; od -t x1 -v -Anx -w4 $<.x3ip_le > $@.x3ip_le; fi
	if [ -e $<.vmem ]; then od -t x1 -v -Anx -w4 $<.vmem > $@.vmem; od -t x1 -v -Anx -w4 $<.vmem_le > $@.vmem_le; fi

ifneq ($(ARMBAR),1)

# code.bin consumed by flash_preload.v to get program into flash
%.mcu.bin:  %.mcu.elf
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(FROMELF) --bin -o $@ $<
else
	$(OBJCOPY) -Obinary -R.xip -R.x1ip -R.x2ip -R.x3ip -R.vmem $< $@
	$(PADBIN) $@
	$(OBJCOPY) -Obinary -j.xip  --reverse-bytes=4 $< $@.xip
	$(OBJCOPY) -Obinary -j.x1ip --reverse-bytes=4 $< $@.x1ip
	$(OBJCOPY) -Obinary -j.x2ip --reverse-bytes=4 $< $@.x2ip
	$(OBJCOPY) -Obinary -j.x3ip --reverse-bytes=4 $< $@.x3ip
	$(OBJCOPY) -Obinary -j.vmem --reverse-bytes=4 $< $@.vmem

	$(OBJCOPY) -Obinary -j.xip                    $< $@.xip_le
	$(OBJCOPY) -Obinary -j.x1ip                   $< $@.x1ip_le
	$(OBJCOPY) -Obinary -j.x2ip                   $< $@.x2ip_le
	$(OBJCOPY) -Obinary -j.x3ip                   $< $@.x3ip_le
	$(OBJCOPY) -Obinary -j.vmem                   $< $@.vmem_le

endif

%.mcu.txt:  %.mcu.elf
ifeq ($(TOOLCHAIN),$(ARM_TOOLCHAIN))
	$(FROMELF) -cedrst -o $@ $<
else
	$(OBJDUMP) -S $< > $@
endif

%.mcu.map:  %.mcu.elf
	nm $< > $@

#%.inc:  %.elf
#	@$(FROMELF) --cad -o $@ $<

#%.so:	%.mcu.o $(OTHER_OBJS) $(MCUOBJS)

%.mcu.rcf:  %.mcu.bin %.mcu.txt
	$(XXD) -b -c4 $< | awk '{print $$5$$4$$3$$2;}' > $@

# ifeq ($(DSP),1)
# #${ALL_TESTS}:   %: %.mcu.bin %.mcu.dat %.mcu.txt %.dsp0.bin %.dsp1.bin %.dsp0.dat %.dsp1.dat %.dsp0.txt %.dsp1.txt
# ${ALL_TESTS}:   %: %.mcu.bin %.mcu.dat %.mcu.txt %.dsp0.bin %.dsp0.dat %.dsp0.txt %.dsp1.bin %.dsp1.dat %.dsp1.txt
# 	@echo Made $@
# else
${ALL_TESTS}:   %: %.mcu.bin %.mcu.dat %.mcu.txt %.mcu.map
	@echo Made $@
#endif

# Use ARM ^^^
else
# ARMBAR

# Rule for x86 armbar build
%.so: %.armbar.o $(OTHER_OBJS) $(MCUOBJS)
	@echo "MCUOBJS=$(MCUOBJS)"
	@echo "OTHER_OBJS=$(OTHER_OBJS)"
	$(CC) -shared -Wl,-soname,test.so -o $*.so $^

# dump out dat.xip file compatible with MSPI_PRELOAD make run option
%.mcu.dat:  %.mcu.o
	$(MK_RDMEM) $< $@
	if [ -e $<.xip ];  then od -t x1 -v -Anx -w4 $<.xip  > $@.xip;  od -t x1 -v -Anx -w4 $<.xip_le  > $@.xip_le;  fi
	if [ -e $<.x1ip ]; then od -t x1 -v -Anx -w4 $<.x1ip > $@.x1ip; od -t x1 -v -Anx -w4 $<.x1ip_le > $@.x1ip_le; fi
	if [ -e $<.x2ip ]; then od -t x1 -v -Anx -w4 $<.x2ip > $@.x2ip; od -t x1 -v -Anx -w4 $<.x2ip_le > $@.x2ip_le; fi
	if [ -e $<.x3ip ]; then od -t x1 -v -Anx -w4 $<.x3ip > $@.x3ip; od -t x1 -v -Anx -w4 $<.x3ip_le > $@.x3ip_le; fi
	if [ -e $<.vmem ]; then od -t x1 -v -Anx -w4 $<.vmem > $@.vmem; od -t x1 -v -Anx -w4 $<.vmem_le > $@.vmem_le; fi


%.armbar.bin: %.armbar.o
	touch $@

# ifeq ($(DSP),1)
# #${ALL_TESTS}:   %: %.mcu.bin %.mcu.dat %.so %.dsp0.bin %.dsp1.bin %.dsp0.dat %.dsp1.dat
# ${ALL_TESTS}:   %: %.mcu.bin %.mcu.dat %.so %.dsp0.bin %.dsp0.dat %.dsp1.bin %.dsp1.dat
# 	@echo Made $@
# else
${ALL_TESTS}:   %: %.so
	@echo Made $@
#endif

endif
	@echo "======================="
	@echo "All CCFLAGS: $(CCFLAGS)"
	@echo "All LDFLAGS: $(LDFLAGS)"
	@echo "All LDFLAGS: $(CC_DEFS)"
	@echo "======================="

################################################################################
#
# Clean - remove all .o, .elf, .bin, .rcf
#

clean:
		@rm -f *.so *.inc *.rcf *.bin *.elf *.txt *.dat *.map *.log *.lst *.d *.xip *.xip_le *.x1ip *.x1ip_le *.x2ip *.x2ip_le *.x3ip *.x3ip_le *.vmem *.vmem_le  *.c~

clean_all:	clean
	@rm -f common/*/*.a rss/common/*/*.a */*.so */*.inc */*.rcf */*.bin */*.elf */*.o */*/*.o */*/*/*.o */*.txt */*.dat */*.map */*.log */*.lst */*.d */*/*.d */*/*/*.d */*.xip */*.xip_le */*.x1ip */*.x1ip_le */*.x2ip */*.x2ip_le */*.x3ip */*.x3ip_le */*.vmem */*.vmem_le  include/TB_DEBUG/*_tb_regs.h include/TB_DEBUG/extslv_regs.h common/bin-gcc/*.d common/bin-gcc/*.o

# EOF
