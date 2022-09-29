# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 23:20:13 2022

@author: ifyij
"""

# No Imports Allowed!


def backwards(sound):
    audi = sound.get('samples')
    audi1 = audi.copy()
    audi1 = audi[::-1]
    ans = {}
    ans['rate']= sound['rate']
    ans['samples']= audi1
    return ans
    


def mix(sound1, sound2, p):
    samp1 = sound1.get('samples')
    samp2 = sound2.get('samples')
    ans = {}
    ans_samples = []
    if sound1.get('rate') != sound2.get('rate'):
        return None
    x = 0
    if len(samp1) <= len(samp2):
        x = len(samp1)
    else:
        x = len(samp2)
    
    for ele in range(x):
        ans_samples.append(samp1[ele]*p + samp2[ele]*(1-p))
    ans['rate']= sound1['rate']
    ans['samples']= ans_samples
    return ans
    


def convolve(sound, kernel):
    samp = list(sound.get('samples'))
    sample = list(samp.copy())
    ans = {}
    alm = [0 for i in range(len(sample)+len(kernel)-1)]
    for x in range(len(kernel)):
        if kernel[x] != 0:
            for y in range(len(sample)):
                
                alm[x+y] += sample[y]*kernel[x]
    ans['rate']= sound['rate']
    ans['samples'] = alm
    return ans
        


def echo(sound, num_echoes, delay, scale):
    sample_delay = round(delay * sound['rate'])
    sd = sample_delay
    num = num_echoes
    samp = list(sound.get('samples'))
    sample = list(samp.copy())
    ans = {}
    kernel = []
    count = 0
    while num > 0:
        ran = []
        ran.append(scale**count)
        ran.extend([0 for i in range(sd-1)])
        kernel.extend(ran)
        num -=1 
        count +=1
    kernel.append(scale**count)
    return convolve(sound, kernel) 
        
                


def pan(sound):
    rig = list(sound.get('right'))
    right = list(rig.copy())
    lef = list(sound.get('left'))
    left = list(lef.copy())
    samp_num = len(rig)
    right_ans = []
    left_ans =[]
    ans = {}
    for x in range(samp_num):
        right_ans.append((x/(samp_num-1))*right[x])
    for x in range(samp_num):
        left_ans.append((1-(x/(samp_num-1)))*left[x])
    ans['rate']= sound['rate']
    ans['right'] = right_ans
    ans['left'] = left_ans
    return ans

def remove_vocals(sound):
    rig = list(sound.get('right'))
    right = list(rig.copy())
    lef = list(sound.get('left'))
    left = list(lef.copy())
    samp_ans = []
    ans = {}
    for i in range(len(left)):
        samp_ans.append(left[i]-right[i])
    ans['rate']= sound['rate']
    ans['samples'] = samp_ans
    return ans


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    #hello = load_wav('sounds/hello.wav')
    mystwav = backwards(load_wav('mystery.wav'))
    '''
    #mystery_backwards = write_wav(mystwav,'mysterybackwards.wav')
    water = load_wav('water.wav')
    synth = load_wav('synth.wav')
    mix_synthwater = mix(synth,water, 0.2)
    #write_wav(mix_synthwater, 'mixedwater.wav')
    ice_and_chilli = load_wav('ice_and_chilli.wav')
    kern = bass_boost_kernel(1000,1.5)
    newice = convolve(ice_and_chilli, kern)
    '''
    #write_wav(newice,'newice.wav')
    chord = load_wav('chord.wav')
    chordecho = echo(chord, 5, 0.3, 0.6)
    #write_wav(chordecho,'chordecho.wav')
    car = load_wav('car.wav',True)
    carpan = pan(car)
    write_wav(carpan, 'carpan.wav')
    lookout = load_wav('lookout_mountain.wav', True)
    lookoutnew = remove_vocals(lookout)
    write_wav(lookoutnew, 'lookoutnew.wav')

    # write_wav(backwards(hello), 'hello_reversed.wav')
