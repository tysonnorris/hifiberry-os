# Customizing buildroot

See some tips here: https://www.viatech.com/en/2015/06/buildroot/

## Additional kernel modules

### basic extensions
* add additional overlay dir by adding `noizebot/buildroot/board/raspberrypi/overlay` to `BR2_ROOTFS_OVERLAY`
* add `buildroot/package/noizebot` for `BR2_PACKAGE_NOIZEBOT`

TODO: 
* can there be an additional "packages dir"?


### specifics
* To avoid `modprobe  snd_aloop`, added file
`noizebot/buildroot/board/raspberrypi/overlay/etc/modules-load.d/aloop.conf`



# TODO:
## missing python modules:
adafruit-circuitpython-neopixel #is there a better module?
- BR2_PACKAGE_PYTHON_RPI_WS281X
adafruit-circuitpython-fancyled #is there a better module?
- refactoring
board
- refactoring

## missing modules for powerpot
gpiozero