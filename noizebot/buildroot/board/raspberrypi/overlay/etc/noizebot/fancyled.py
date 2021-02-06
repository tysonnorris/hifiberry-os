#!/usr/bin/env python
# by djazz, using various bits of code found over the web

# works with both python2 and python3
# requires: python-alsaaudio, python-numpy, python-smbus, piglow
# install piglow: curl get.pimoroni.com/piglow | bash

# usage:
# this script accepts raw audio in this format: S16LE 44100 kHz Mono
#  script-that-outputs-audio | python piglow_fft.py
#  echo raw.pcm | piglow_fft.py
# see usage suggestions below

# examples:
#  mpg123 -s --no-seekbuffer -m -r 44100 http://icecast.djazz.se:8000/radio | python piglow_fft.py
#  avconv -i http://icecast.djazz.se:8000/radio  -f s16le -acodec pcm_s16le -ar 44100 -ac 1 - -nostats -loglevel info | python piglow_fft.py
# you can replace the url with a local file path
# currently it's pointing to http://radio.djazz.se


import sys
import io
from time import sleep
from struct import unpack
import numpy as np
import alsaaudio as aa

# comment out all lines referencing piglow
# if you want to try just the fft analyzer
#import piglow
import neopixel
import board

import adafruit_fancyled.adafruit_fancyled as fancy

#basecolor1 = fancy.CHSV(0.7, 1.0, 0.3)
basecolor1 = fancy.CHSV(0.75, 1.0, 0.3)
#basecolor1 = fancy.CHSV(0.85, 1.0, 0.3)




pixels = neopixel.NeoPixel(board.D12, 16, brightness=0.1, auto_write=False)


# Return power array index corresponding to a particular frequency
def piff(val):
  return int(2 * chunksize * val/sample_rate)

def update(position, i, p):
  #color = fancy.CHSV(i*0.125*basecolor1.hue, basecolor1.saturation, p*basecolor1.value)
  #color = fancy.CHSV((1-i*0.15)*basecolor1.hue, basecolor1.saturation, p*basecolor1.value)
  #print("updating", i)

  color = fancy.CHSV((1-i*0.06)*basecolor1.hue, basecolor1.saturation, p*basecolor1.value)
  newcolor = color.pack()
  

  #color = fancy.gamma_adjust(color,gamma_value=0.8,brightness=0.8)
  #print(str(i) + ' ' + str(p) + ' ' + str(color))
  #newcolor = color.pack()

  #print('i ', i)
  #print('newcolor ', newcolor)
  pixels[position] = newcolor 
  #print('pixels ', pixels[i])


num_pixels=16
half_pixels=int(num_pixels/2)

# Initialize the arrays
#bins       = [0,0,0,0,0,0]
#smoothbins = [0,0,0,0,0,0] # for smoothing
##weighting = [1, 1.5, 3, 4, 6.5, 9] # Change these according to taste
#weighting = [1, 1.5, 3, 4.5, 6, 7.5] # Change these according to taste

bins = [0]*half_pixels
smoothbins = [0]*half_pixels
weighting = [0]*half_pixels
#weighting = [1, 1.5, 3, 4.5, 6, 9, 10, 11] # Change these according to taste



for i in range(half_pixels):
  weighting[i] = 1 + (1.45 * i) 

print('weighting', weighting)
print('half', half_pixels)

# Precalculate weighting bins
weighting = np.true_divide(weighting, 1000000)

# audio settings
sample_rate = 44100
no_channels = 1 # mono only
chunksize = 2048

# stdin acts as a file, read() method
#stdin = getattr(sys.stdin, 'buffer', sys.stdin)

# setp up audio output
#output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
#output.setchannels(no_channels)
#output.setrate(sample_rate)
#output.setformat(aa.PCM_FORMAT_S16_LE)
#output.setperiodsize(chunksize*no_channels)

#print("Loading...")
#data = stdin.read(chunksize*5)

#print("Playing...")
#output.write(data)

sample_rate = 44100
no_channels = 2
chunk = 512 # Use a multiple of 8

#input = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, "hw:Loopback,1", rate=44100)
input = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, "looprec", rate=44100)
#recoder.setchannels(1)
input.setchannels(no_channels)
#input.setrate(samplerate)
input.setperiodsize(chunk)
input.setformat(aa.PCM_FORMAT_S16_LE)

(dl, data) = input.read()


counter = 0

while data!='':
  #data = stdin.read(chunksize)
  (dl, data) = input.read()
  #output.write(data)

  if dl <= 0:
    continue


  #npdata = np.array(unpack("%dh"%(len(data)/2), data), dtype='h')
  #npdata = np.frombuffer(data, dtype='i2' )
  
  fmt = "%dH"%(len(data)/2)
  npdata = unpack(fmt, data)
  npdata = np.array(npdata, dtype='h') 
  #print('Array PCM: \n',dl)


  fourier = np.fft.rfft(npdata)
  fourier = np.delete(fourier, len(fourier) -1)
  power = np.abs(fourier)

  #print("len:", len(fourier))

  #lower_bound = 0
  #upper_bound = 64
  lower_bound = 16
  upper_bound = 30
  lower_bound = 0
  upper_bound = 16
  upper_bound = 12



  for i in range(len(bins)):
    mean = np.mean(power[piff(lower_bound) : piff(upper_bound):1])
    bins[i] = int(mean) if np.isnan(mean) == False else 0
    # if counter == 0:
    #   print([piff(lower_bound), piff(upper_bound)])
    lower_bound = upper_bound
    upper_bound = upper_bound << 1


#  print("lower:", lower_bound)
#  print("upper:", upper_bound)


  bins = np.divide(np.multiply(bins,weighting),5)

  a = ''

  for i in range(half_pixels):
    m = bins[i]
    #print("smoothbins:",smoothbins[i]) 
    #smoothbins[i] *= 0.93
    #smoothbins[i] *= 0.99
    smoothbins[i] *= 0.93
    if m > smoothbins[i]:
      smoothbins[i] = m
      #smoothbins[i] = m
    value = smoothbins[i]
    if value > 1:
      value = 1
    #brightness = int(value*255)
    brightness = value
    #brightness = int(value)
    
    #if brightness < 1:
    #  brightness = 1
    #piglow.ring(i, brightness)
    
    #update(i, i, brightness)
    update(half_pixels -1 -i, i, brightness)

    # update the mirror half
    #update(num_pixels - 1 -i, i, brightness)
    update(i + half_pixels, i, brightness)

    s = "|"
    s = s.ljust(int(value*20), "#")
    s = s.ljust(20)

    a += s
  a += "|"

  # print bars
  # if counter % 1 == 0:
  #   print(a)

  #piglow.show()
  pixels.show()
  
  counter += 1


