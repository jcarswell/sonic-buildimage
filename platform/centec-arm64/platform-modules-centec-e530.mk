# Centec E530-48T4X-P Platform modules


CENTEC_E530_48T4X_P_PLATFORM_MODULE_VERSION =1.3
CENTEC_E530_24X2C_PLATFORM_MODULE_VERSION =1.3
CENTEC_E530_48S4X_PLATFORM_MODULE_VERSION =1.3
CENTEC_E530_24X2Q_PLATFORM_MODULE_VERSION =1.3

export CENTEC_E530_48T4X_P_PLATFORM_MODULE_VERSION

CENTEC_E530_48T4X_P_PLATFORM_MODULE = platform-modules-e530-48t4x-p_$(CENTEC_E530_48T4X_P_PLATFORM_MODULE_VERSION)_arm64.deb

$(CENTEC_E530_48T4X_P_PLATFORM_MODULE)_SRC_PATH = $(PLATFORM_PATH)/sonic-platform-modules-e530
$(CENTEC_E530_48T4X_P_PLATFORM_MODULE)_PLATFORM = arm64-centec_e530_48t4x_p-r0
$(CENTEC_E530_48T4X_P_PLATFORM_MODULE)_DEPENDS += $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)
SONIC_DPKG_DEBS += $(CENTEC_E530_48T4X_P_PLATFORM_MODULE)

CENTEC_E530_24X2C_PLATFORM_MODULE = platform-modules-e530-24x2c_$(CENTEC_E530_24X2C_PLATFORM_MODULE_VERSION)_arm64.deb
$(CENTEC_E530_24X2C_PLATFORM_MODULE)_PLATFORM = arm64-centec_e530_24x2c-r0
$(eval $(call add_extra_package,$(CENTEC_E530_48T4X_P_PLATFORM_MODULE),$(CENTEC_E530_24X2C_PLATFORM_MODULE)))

CENTEC_E530_48S4X_PLATFORM_MODULE = platform-modules-e530-48s4x_$(CENTEC_E530_48S4X_PLATFORM_MODULE_VERSION)_arm64.deb
$(CENTEC_E530_48S4X_PLATFORM_MODULE)_PLATFORM = arm64-centec_e530_48s4x-r0
$(eval $(call add_extra_package,$(CENTEC_E530_48T4X_P_PLATFORM_MODULE),$(CENTEC_E530_48S4X_PLATFORM_MODULE)))

CENTEC_E530_24X2Q_PLATFORM_MODULE = platform-modules-e530-24x2q_$(CENTEC_E530_24X2Q_PLATFORM_MODULE_VERSION)_arm64.deb
$(CENTEC_E530_24X2Q_PLATFORM_MODULE)_PLATFORM = arm64-centec_e530_24x2q-r0
$(eval $(call add_extra_package,$(CENTEC_E530_48T4X_P_PLATFORM_MODULE),$(CENTEC_E530_24X2Q_PLATFORM_MODULE)))