# This script works on Windows 10 Python 3.5
#      By Conrad Braam
# Create an animation, of a typewriter keys being pressed
# uses a real image as a background and overlays the keys simply snipping a
# mask and re-painting it but lower down a few pixels. This is a more
# advanced version of the plain quare-keys version. This porogram uses an
# overlay mask to know where the keys are.
# python docs on the masking api:
#    http://www.pygame.org/docs/ref/mask.html
# example code:
#    http://stackoverflow.com/questions/16880128/pygame-is-there-any-way-to-only-blit-or-update-in-a-mask
#
# 1. save image series to disk for visualizing a person pressing letters
# A-z 0-9 and space and period.
#
#
# comandline is the message to type out in the movie. not all characters are
# supported in the message. Unsupported characters do not make any noise
# when pressed (pauses).
#
# REQUIRES: ffmpeg for Windows
# INPUTS: are 4 audio files and a jpg background image file.
# OUTPUTS: 2 movie files, an audio file and a folder called images is 
# created with all the images used.
import sys, os, pygame
from pygame.locals import Color
import shutil, subprocess
import random,wave

# screen size (image will be resized
size = width, height = 1080, 720
black = 0, 0, 0
lgray = 40, 40, 40
dgray = 20,20,25
white = 255,255,255
red   = 255,0,0
orange= 255,153,0
green   = 0,255,0
cyan    = 0,255,255
boxwidth = 20 # grid size


timeFrame = 0 # start at frame 0
noise_output = None

SAMPLERATE44K = 44100
AUDIOOUTFILE = "noise.wav"
AUDIOSILENT = "silence.wav"

clackData = dict()
fileNames = ('clack1.wav','clack2.wav','clack3.wav','clack4.wav',AUDIOSILENT)
ffMpegPath = "C:\\Tools\\ffmpeg\\bin\\ffmpeg.exe"
keyTravel = 10 # distance a key will travel downwards


def LoadClackData():
    """ Load all the sound effects files into a global
    dictionary called clackData.
    The last sample is a silent sample. Samples must be the same length"""
    global fileNames,clackData
    ideal = 29200# 16650
    logging.info("Loading sounds...")
    for name in fileNames:
        inputwav = wave.open(name)
        clackData[name] = inputwav.readframes(inputwav.getnframes())
        #sampleLength = inputwav.getnframes()
        logging.info("  sample %s length %d loaded" % (name,len(clackData[name])))
        inputwav.close()
        #pad the sample a bit : We use 44.100Hz 2 channels 1/10 second per image
        if (len(clackData[name]) > ideal): #trim the raw data
            logging.warning("  sample sound %s truncated to %d samples" % (name, ideal/2))
            clackData[name] = clackData[name][0:ideal]
        else:
            clackData[name]+= bytearray(ideal - len(clackData[name]))
            logging.info("  sample padded out to %d" % (len(clackData[name])))

    
def AddSound(data):
    """Add a sound effect. Raw data frames as a parameter(bytearray)"""
    global noise_output
    if noise_output is None:
        noise_output = wave.open(AUDIOOUTFILE, 'w')
        noise_output.setparams((2, 2, SAMPLERATE44K, 0, 'NONE', 'not compressed'))
        logging.info("  created %s wav file OK" % AUDIOOUTFILE)
    #logging.debug("  appending output wav file %d frames" % (len(data)/2))
    noise_output.writeframes(data)

def EndSound():
    """Just to close the file in one place only."""
    logging.debug("  closing output %s wav file" % AUDIOOUTFILE)
    noise_output.close()

def SaveFrame(silence=True):
    """ Save video frame and about 1/3 second of sound.
    By default (silence=true) we append silence audio,
    else we append a random key-tap sound"""
    SaveImage()
    global clackData,fileNames
    if len(clackData.keys()) == 0:
        LoadClackData()
    AddSound(clackData[AUDIOSILENT]) # silence.wav
    if silence:
        AddSound(clackData[AUDIOSILENT])
    else:
        keyTapindexes = len(fileNames)-2 # 0 based, but also omit the "silent" sample
        soundName = fileNames[random.randint(0, keyTapindexes)]
        AddSound(clackData[soundName])
        #logging.debug(soundName)

def SaveImage():
    """ Save a jpg file screenshot. increments the screenshot number"""
    global timeFrame
    fname = "images\keyb%03d.jpg" % timeFrame
    #logging.debug("saving %s" % fname)
    timeFrame = timeFrame +1
    pygame.image.save(screen, fname)

def DepressKey(key):
    """ Works out if the key pressed is one we recognise in our
    map of the keyboard. If not, the function does not update
    the screen. You can use this function multiple times to
    depress many keys so long they do not overlap too much.
    Only updates the screen"""
    valid = 1
    key = key.upper()
    if key in keyrow1:
        rRow = row1
        offset = keyrow1.index(key)
        alph = keyrow1
    elif key in keyrow2:
        rRow = row2
        offset = keyrow2.index(key)
        alph = keyrow2
    elif key in keyrow3:
        rRow = row3
        offset = keyrow3.index(key)
        alph = keyrow3
    elif key in keyrow4:
        rRow = row4
        offset = keyrow4.index(key)
        alph = keyrow4
    elif key in keySPACE:
        rRow = space
        offset = 0
        alph = keySPACE
    else:
        valid=0
    if (valid):
        # got the rect and the offset
        keyRectangle = pygame.Rect(rRow.left, rRow.top, rRow.width / len(alph), rRow.height)
        keyRectangle = keyRectangle.move(offset*keyRectangle.width, 0)
        pygame.draw.rect(screen, dgray, keyRectangle, 0)
        my_little_copy = keyboard.subsurface(keyRectangle).copy()
        screen.blit(my_little_copy, (keyRectangle.left, keyRectangle.top + 3))
        pygame.display.flip()
    return valid==1
    
def ConvertMovie(foldername):
    """ Convert all the files in \images (folderName) folder to an mp4 silent-movie"""
    # C:\Tools\ffmpeg\bin\ffmpeg.exe -framerate 30/1 -i .\images\snake%03d.jpg -r 30 -pix_fmt yuv420p out.mp4 -y
    commandLine = ("-framerate ", "3/1 ", "-i ",
                   ".\\images\\keyb%03d.jpg ", "-r ", "30 ",
                   "-pix_fmt ", "yuv420p ", "out.mp4 ", "-y ")
    logging.info("[=============]")
    logging.info("ffmpeg: %s" % ffMpegPath)
    logging.info("args: %s" % " ".join(commandLine))
    subprocess.call([ffMpegPath, commandLine],shell=False)
    logging.info("  Movie saved OK")

def MergeMovieSound(movieIn,soundIn,movieOut):
    """Mixes the sound file 'soundIn' into the movie file 'movieIn'
    Outputs result to 'movieOut'. No errors are trapped/detected."""
    # we could to the movie + sound all in one, but for this we do is in 2 passes to
    # make dissasembly easier
    logging.info("[=============]")
    logging.info("Mix video %s and Audio file %s" % (movieIn, soundIn))
    # -i video.mp4 -i audio.m4a -c:v copy -c:a copy output.mp4
    commandLine = ("-i ", (movieIn + " "),
                   "-i ", (soundIn + " "),
                   "-c:v ", "copy ", # dont copy audio parameters
                   "-y " , (movieOut + " "))
    logging.info(("ffmpeg: %s" % ffMpegPath))
    logging.info(("args: %s" % " ".join(commandLine)))
    subprocess.call([ffMpegPath, commandLine],shell=False)
    logging.info("  Movie converted OK")


def Finnish():
    screen.set_clip()
    screen.blit(keyboard,(0,0))
    pygame.display.flip()
    SaveFrame() # 3 frames of no key pressed
    SaveFrame()
    SaveFrame()
    
    EndSound()  # close sound-file
    
    # save movie file:
    ConvertMovie('images')
    #merge movie and the soundfile
    MergeMovieSound('out.mp4', AUDIOOUTFILE, 'final.mp4')
    sys.exit()
    
class KeyboardMask:
    def __init__(self, rect, mask, alpha, background):
        self.rect  = rect
        self.mask  = mask
        self.alpha = alpha
        self.background = background

def BuildMasks():
    """Scans the mask image and builds a rectange progressively which covers each key
    of the typewriter. 
    """
    global letterMasks
    global mask
    
    build=False
    delta = 5
    y = 0
    hitBoxes = []
    while (y < size[1]):
        x=0
        while (x < size[0]):
            pixel = mask.get_at((x,y))
            
            if (pixel[3] and (not build)):
                build = True
                buildx = x
                buildy = y
                #logging.info("pixel %04d %04d = %s " % (x,y, pixel))
            else:
                if ((build) and (not pixel[3])):
                    #logging.info("scanned from %04d,%04d to %04d,%04d" % (buildx,buildy,x,y))
                    # scan vertically to bottom
                    bottom = y
                    left = x-delta
                    pixel = mask.get_at((left,bottom))
                    while (pixel[3]):
                        bottom += delta
                        pixel = mask.get_at((left,bottom))
                    #logging.info("1 mask from %04d,%04d to %04d,%04d" % (buildx,buildy,x,bottom))                
                    hitBoxes.append( pygame.Rect(buildx-delta,buildy-delta, x-buildx +delta,bottom-y +delta) )
                    build=False
            x += delta
        y += delta
    #merge any colliding rectangles
    newBoxes = []
    last = len(hitBoxes) -1
    logging.info("%d elements merging..." % (len(hitBoxes)))                
    for index in range(0, last-1):
        box = hitBoxes[index].copy()
        test = box.copy()
        if (test.x < size[0]):
            for search in range(index+1, last):
                if (test.colliderect(hitBoxes[search])):
                    box.union_ip(hitBoxes[search]) # join the boxes area "in-place"
                    hitBoxes[search].x=size[0]  # make this rectangle offscreen so we don't include it again
                    hitBoxes[search].y=size[1]
            newBoxes.append(box)
    logging.info("Found %d elements OK" % (len(newBoxes)))

    #make sub-masks for each rect from the mask
    letterMasks = []
    alpahabetical = list("6134578902wqertyuiop-asdfghjklzxcvbn.m ")
    offset = 0
    for box in newBoxes:
        masked = background.copy()
        masked.blit(mask, box, box, pygame.BLEND_RGBA_MULT)
        if (offset < 21):
            eraseBackground = erase_gray
        else:
            eraseBackground = erase_black
        letterMasks.append( KeyboardMask(box, masked, alpahabetical[offset], eraseBackground))
        offset += 1
    logging.info("Compiled %d keys OK" % (len(letterMasks)))

def GetLetterMask(letter):
    ret = None
    for mask in letterMasks:
        if (mask.alpha.upper() == letter.upper()):
            ret = mask
    return ret
    pass

def DepressKey(mask):
    pass

import logging
logging.basicConfig(filename='typewrite.log', level=logging.DEBUG)

message = "HELLO WORLD. 1234567"
if (len(sys.argv) > 1):
    message = sys.argv[1]
logging.info("Starting. message text= %s" % message)
#create a new empty /images folder
if os.path.exists('images'):
    shutil.rmtree('./images')
os.makedirs('images')

logging.info("Init Graphics mode...")
pygame.init()
screen = pygame.display.set_mode(size)

#load the background image
erase_black = pygame.image.load("erase_black.png")
erase_gray = pygame.image.load("erase_gray.png")
keyboard = pygame.image.load("keyboard.jpg").convert_alpha()
keyboard = pygame.transform.scale(keyboard, size)

background = keyboard.convert_alpha()
maskimg = pygame.image.load("keymask.png")
mask = pygame.transform.scale(maskimg, size).convert_alpha()

masked = keyboard.copy()
masked.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MULT)
logging.info("Graphics mode OK, artwork loaded")

# build masks from the images
BuildMasks()

delays = 0 # whether we will slow screen updates 1=normal 0=fast
myfont = pygame.font.SysFont("monospace",35)
screen.blit(keyboard,(0,0))
SaveFrame(True) # no sound, an idle Frame
SaveFrame(True) # no sound, an idle Frame
SaveFrame(True) # no sound, an idle Frame

for letter in list(message):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: quit()
        screen.set_clip()
        screen.blit(keyboard,(0,0))
        SaveFrame(True) # no sound, an idle Frame
        
        mask = GetLetterMask(letter)
        if (mask):
            eraserect = mask.rect.copy()
            eraserect.height = mask.rect.height/2

            # erase key background color
            travelRect = mask.rect.copy()
            travelRect.height = keyTravel*2
            screen.set_clip(travelRect)
            screen.blit(mask.background, mask.rect)
            screen.blit(mask.background, mask.rect.move(0,keyTravel))
            screen.set_clip(mask.rect.move(0, keyTravel))
            screen.blit(mask.mask, (0, keyTravel))
            #save image
            SaveFrame(False)
        else:
            SaveFrame(True) # no sound
        
        pygame.display.flip()
        pygame.time.delay(1000*delays)

Finnish()
