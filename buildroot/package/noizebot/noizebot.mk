################################################################################
#
# noizebot-hifiberry
#
################################################################################

NOIZEBOT_VERSION = cec29b5e59f558b528b26348999d6548d3bf3dee
NOIZEBOT_SITE = $(call github,tysonnorris,noizebot-hifiberry,$(NOIZEBOT_VERSION))
NOIZEBOT_SETUP_TYPE = setuptools
NOIZEBOT_LICENSE = MIT
NOIZEBOT_LICENSE_FILES = LICENSE.md

$(eval $(python-package))
