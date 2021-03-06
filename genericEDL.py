############################################################################
####
####  Copyright (c) 2012, Anima Vitae Ltd. All rights reserved.
####
####  Redistribution and use in source and binary forms, with or without
####  modification, are permitted provided that the following conditions are
####  met:
####
####     * Redistributions of source code must retain the above copyright
####       notice, this list of conditions and the following disclaimer.
####
####     * Redistributions in binary form must reproduce the above copyright
####       notice, this list of conditions and the following disclaimer in the
####       documentation and/or other materials provided with the distribution.
####
####     * Neither the name of Anima Vitae Ltd. nor the names of any
####       other contributors to this software may be used to endorse or
####       promote products derived from this software without specific prior
####       written permission.
####
####  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
####  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
####  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
####  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
####  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
####  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
####  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
####  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
####  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
####  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
####  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
####
############################################################################

## @package animaCore.genericEDL - has been part of animaCore - let's see if that gets to gitHub as well
#  @note the commenting format is made for doxygen
#  Functions and classes to describe edit data in a multimedia project
import math

# FOR VALIDATING DATA

## returns default FPS(left over format).
#  @param None
#  @retval  'film' as these tool have been used mostly for 24fps proects so far 
def aDefaultFPS():
    return 'film'

## These FPS formats are currently supported - all formats non-drop frame
#  @param None
#  @retval  dictionary of format names with their correspondig frames/sec values 
#  @note use lowercase in naming when adding new types
#  @note nanos is not frames/second format but can be mathematically treated as such
def aSupportedFPS():
    return {'pal':25, 'ntsc':30, 'film':24, 'nanos':1000000000}

#CLASSES
## base class for testing and validating time input, used in aTimeHandler and in classes that have time input
#  @retval  new object
#  @note this might be canged into a function that objects would just use - now these methods are inheirted to objects 
class aTimeTest(object):
    ## tests if given FPS is supported and makes FPS non-case sensitive
    #  @retval FPS in lowercase 
    def testFPS(self,FPS=aDefaultFPS()):
        supportedFPS=aSupportedFPS()
        if FPS.lower() in supportedFPS:
            return FPS.lower()
        else:
            return 'INVALID FPS FORMAT ', FPS      
    ## tests if smpte format is string, list or tuple
    #  @retval smpte as list
    def testSmpte(self,smpte):
        if type(smpte)==tuple or type(smpte)==list:
            return smpte
        elif type(smpte)==str:
            return smpte.replace(',',':').replace(';',':').split(':')
        else:
            print 'Non-supported SMPTE time format: ' , smpte         
    ## tests if frames are used as string (starting with f) or numeric value
    #  @retval frames in float
    def testFrames(self,frames):
        if type(frames)==str:
            return float(frames.replace('f',''))
        elif type(frames)==int or type(frames)==float:
            return frames
        else:
            print 'Non-supported type for frames ', type(frames)
    ## tries to convert input arg to time in seconds
    #  @retval time as seconds
    def testTime(self,time,FPS=aDefaultFPS()):
        if type(time)==str or type(time)==tuple or type(time)==list:
            if 'f' in time and type(time)==str:
                time = self.framesAsTime(time.replace('f',''), FPS)
            else:
                time = self.smpteAsTime(time, FPS)
        elif type(time)==aTime:
            time=time.time 
        return time
    ## returns given input data written into aTime
    #  @param time - input time
    #  @param FPS fps for converting frames or smpte into seconds
    #  @param orgValue - used for overiding __setAttr__. If orginal value has been aTime the data is writen into this object instead of craeting new one 
    #  @retval aTime object      
    def testObject(self,time,FPS=aDefaultFPS(),orgValue=None):
        if type(time)==str or type(time)==tuple or type(time)==list:
            if 'f' in time and type(time)==str:
                time = aTime(self.framesAsTime(time.replace('f',''), FPS))
            else:
                time = aTime(self.smpteAsTime(time, FPS))
        elif type(time)!=aTime:
            time=aTime(time)
        if orgValue:
            if type(orgValue)==aTime:
                orgValue.time=time.time
                time=orgValue
        return time
    
## base class for time conversion operations. Does also data validation. Used in aTime
#  @retval  new object 
class aTimeHandler(aTimeTest):
    ## converts an array to SMPTE-string format
    #  @param array is the unput array
    #  @param dotFormat the way time units are divided in string default being ##:##:##:##  
    #  @retval SMPTE string
    def arrayToSmpte(self,array,dotFormat=':::'):
        dotFormat=dotFormat + ' '
        stmpeStr=''
        i=0
        for item in array:
            stmpeStr=stmpeStr+str(int(item)).rjust(2,'0')+dotFormat[i]
            i=i+1
        return stmpeStr[0:(len(stmpeStr)-1)]
    ## calculates SMPTE array (not string!) into time in seconds
    #  @retval time in seconds
    def arrayToTime(self,array,FPS=aDefaultFPS()):
        i=0
        time=0.0
        for item in array:
            if i<3:
                time=time+math.pow(60,(2-i))*float(item)
            else:
                time=time+float(item)/aSupportedFPS()[FPS]
                if float(item)>aSupportedFPS()[FPS]:
                    print 'WARNING: value in SMPTE:', smpte, 'is out of range in format:', FPS 
            i=i+1
        return time
    ## calculates SMPTE array (not string!) into frames
    #  @retval time in frames
    def arrayToFrames(self,array,FPS=aDefaultFPS()):
        return self.arrayToTime(array,FPS)*FPS
    ## calculates given frames into time
    #  @retval time in seconds  
    def framesAsTime(self,frames,FPS=aDefaultFPS()):
        FPS = self.testFPS(FPS)
        return float(self.testFrames(frames))/float(aSupportedFPS()[FPS])
    ## converts given smpte into time using arrayToTime method
    #  @retval time in seconds 
    def smpteAsTime(self,smpte,FPS=aDefaultFPS()):
        FPS = self.testFPS(FPS)
        return self.arrayToTime(self.testSmpte(smpte), FPS)
    ## calculates time into SMPTE units
    #  @retval SMPTE list or string depending on returnAsList-attribute
    def timeAsSmpte(self,time,FPS=aDefaultFPS(),returnAsList=0,dotFormat=':::'):     
        FPS = self.testFPS(FPS)
        h=[int(time/math.pow(60,2)), time/math.pow(60,2)]
        m=[int(60*(h[1]-h[0])), 60*(h[1]-h[0])]
        s=[int(60*(m[1]-m[0])), 60*(m[1]-m[0])]
        lo=[round(aSupportedFPS()[FPS]*(s[1]-s[0])), aSupportedFPS()[FPS]*(s[1]-s[0])]
        fpsTest=aSupportedFPS()[FPS]
        if lo[0]==aSupportedFPS()[FPS]:
            lo[0]=0
            s[0]=s[0]+1
        if returnAsList:
            return h[0],m[0],s[0],lo[0]
        else:
            return self.arrayToSmpte((h[0],m[0],s[0],lo[0]), dotFormat)
    ## calculates frames into SMPTE units using 2 other methods
    #  @retval SMPTE list or string depending on returnAsList-attribute
    def framesAsSmpte(self,frames,FPS=aDefaultFPS(),returnAsList=0):
        FPS = self.testFPS(FPS)
        return self.timeAsSmpte(self.framesAsTime(self.testFrames(frames)),FPS, returnAsList, dotFormat=':::')
    ## calculates time into frames based on FPS
    #  @retval frames
    def timeAsFrames(self,time,FPS=aDefaultFPS()):
        FPS = self.testFPS(FPS)
        return float(time*aSupportedFPS()[FPS])
    ## calculates SMPTE string or list into frames using other methods
    #  @retval frames
    def smpteAsFrames(self,smpte,FPS=aDefaultFPS()):
        FPS = self.testFPS(FPS)
        return float(self.smpteAsTime(smpte)*aSupportedFPS()[FPS])

## base time class that contains time as seconds and can convert own or given time to smpte and frames
#  @param time in seconds and FPS format
#  @retval  new aTime object (also by +-*/ operations)
class aTime(aTimeHandler):
    #  @param time = float(seconds), frames f(frames) or SMPTE(string,tuple or list)
    #  @param FPS = units/second format that defines units smaller than second  
    #  @note init as SMPTE format (hours, minutes, seconds, leftover) example '12:10:01:15' or (12,10,1,15) 
    #  @note example of init as frames = 'f120'
    #  @note does not contain FPS info itself - must be defined by user or aDefaultFPS()
    def __init__(self, time=0.0, FPS=aDefaultFPS()):
        self.time=self.testTime(time)
        FPS = self.testFPS(FPS)
    ## OPERATIONS +-*/
    #  @param other parameter can be a time object or numeric value
    #  @retval new aTime object 
    def __add__(self, other):
        time=0.0
        if type(other)==aTime:
            time=self.time+other.time
        else:
            time=self.time+float(other)
        return aTime(time)
    def __sub__(self, other):
        time=0.0
        if type(other)==aTime:
            time=self.time-other.time
        else:
            time=self.time-float(other)
        return aTime(time)
    def __mul__(self, other):
        time=0.0
        if type(other)==aTime:
            time=self.time*other.time
        else:
            time=self.time*float(other)
        return aTime(time)
    def __div__(self, other):
        time=0.0
        if type(other)==aTime:
            time=self.time/other.time
        else:
            time=self.time/float(other)
        return aTime(time)
    # TO DO __copy function          
    #FOR READING CLASS ATTRIBUTES  
    ## returns the value of time attribute
    #  @retval time in seconds
    def asTime(self):
        return self.time
    ## calculates object's time attribute into frames
    #  @retval frames
    def asFrames(self, FPS=aDefaultFPS()):
        FPS = self.testFPS(FPS)
        return float(self.time*aSupportedFPS()[FPS])  
    ## uses timeAsSmpte method to convert object's time attribute into SMPTE
    #  @retval SMPTE string or list
    def asSmpte(self, FPS=aDefaultFPS(), returnAsList=0, dotFormat=':::'):
        FPS = self.testFPS(FPS)
        return self.timeAsSmpte(self.time,FPS,returnAsList,dotFormat)
    ## behaves like copy 
    #  @retval new aTime object
    def asObject(self, FPS=aDefaultFPS(), returnAsList=0, dotFormat=':::'):
        return aTime(self.time)

## a base class to describe a clips range - used in clips
#  @retval new object 
#  @note setattr is overridden but getattr not
class aRange(aTimeTest):
    #  @param IN point in to the clips own time space clip starts from zero
    #  @param parentIN a sync point to parent's time (for example Edit's global time)
    #  @param duration duration in real time (not clip's internal time code)
    def __init__(self, IN=aTime(0.0), parentIN=aTime(0.0), duration=aTime(0.0)):
        # object testing might be changed just to ordinary function
        self.IN=self.testObject(IN)
        self.parentIN=self.testObject(parentIN)
        self.duration=self.testObject(duration)
    ## function to return the IN time 
    #  @retval range's IN time aTime
    def getIN(self):
        return self.IN
    ## function to return the parent timecode's IN 
    #  @retval range's parent IN time aTime 
    def getParentIN(self):
       return self.parentIN
    ## function to return the duration 
    #  @retval range's duration time as aTime, 
    def getDuration(self):
        return self.duration
    ## function to return the OUT time 
    #  @retval range's OUT time as aTime
    def getOUT(self):
        return self.IN+self.duration
    ## function to return the parent timeline's OUT 
    #  @retval range's parent OUT as aTime
    def getParentOUT(self):
        return self.parentIN+self.duration
    # override setattr to ensure the datatypes for time units to be aTime
    def __setattr__(self, name, value):
        if name=='IN' or name=='parentIN' or name=='duration':
            #check if attr has been initalized yet
            if hasattr(self, name):
                value=self.testObject(value, 'no fps data to provide',self.__dict__[name])
            else:
                value=self.testObject(value)
        self.__dict__[name]=value

    
## a base class for locating media files 
#  @retval new object
#  @ JUST A SKETCH
class aPath(object):
    #  @param name is used as deafult for writing files or describe the objects
    #  @param search array is to used to store the potential locations to search the msiiing file
    def __init__(self, path='', name='',search=[]):
        self.path=path
        self.search=search
    ## basic string replacing operation
##    def replace(self, searchExp, replaceExp, caseSensitive=1):
##        print 'TO DO'
##    ## changing path name and cheking if new path is exists
##    def replacePath(self, path, newPath, caseSensitive=1):
##        print 'TO DO'
##    ## searching for the file under given path
##    def search(self, name, path, partialMatch=0, ignoreExtension=0, caseSensitive=1):
##        print 'TO DO'
##    def nextAvailableName(self, path):
##        print 'TO DO'

## a base media properties 
#  @retval new object 
class aMedia(aTimeTest):
    #  @param start is internal start time 
    #  @param end is internal end time
    #  @param FPS is media's native FPS format
    #  @param path media's file path
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path=aPath()):
        self.start=self.testObject(start)
        self.end=self.testObject(end)
        #FPS as is actually more of a video property - might be left out from the base media?
        # lets see how often we would like to know this
        self.FPS=FPS
        self.path=path
    ## function to return media' start time 
    #  @retval media's start time as aTime
    def getStart(self):
        return self.start
    ## function to return media' end time 
    #  @retval media's end time as aTime
    def getEnd(self):
        return self.end
    ## function to return media' duration 
    #  @retval media's duration as aTime
    def getDuration(self):
        return self.end-self.start
    # override setattr to ensure the datatypes for time units to be aTime
    def __setattr__(self, name, value):
        if name=='start' or name=='end':
            value=self.testObject(value)
        self.__dict__[name]=value

#### SOME OF THESE CLASSES ARE PARTLY COMMENTED OUT - THEY ARE PLACEHOLDERS AT THE MOMENT      

## a base video properties 
#  @retval new object 
class aVideoProperties(object):
    def __init__(self,  FPS=aDefaultFPS(), x=0, y=0, bitDepth=8, fileFormat='', compression=''):
        self.FPS=FPS
        self.x=x
        self.y=y
        self.bitDepth=bitDepth
        #TO DO etc.
'''
## a base audio properties 
#  @retval new object 
class aAudioProperties(object):
    def __init__(self, sampeRate=44100.0,bitDepth=16, numOfChannles=1,samples=44100):
        self.bitDepth=bitDepth
        self.bitDepth=bitDepth
        print 'TO DO etc.'
         
## a base media container 
#  @retval new object 
class aMedia(aPath,aMediaProperties):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='',name='',search=[]):
        aMediaProperties.__init__(self,start,end)
        aPath.__init__(self,path,name,search)

## a base video container 
#  @retval new object 
class aVideo(aMedia):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='',name='',search=[], properties=aVideoProperties()):
        aMedia.__init__(self, start, end, FPS, path, name, search)
        self.properties=properties

## a base audio container 
#  @retval new object        
class aAudio(aMedia):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='', name='',search=[], properties=aVideoProperties()):
        aMedia.__init__(self, start, end, FPS, path, name, search)
        self.properties=properties
'''
## a base class to describe a clips - clip combines range and to media and defines the sync - by default clip's start frame 0 is in sync in media start time x.
#  @retval new object 
#  @note setattr is overridden 
#  @note for better undersanding of clip's timecode see: https://github.com/fisuKlonkku/genericEDL/wiki/Understanding-clip%27s-timecode
class aBaseClip(aTimeTest):
    #  @param ranges = aRange object 
    #  @param clip's playback speed, affect's clips internal tc  
    #  @param speed the range content is "played"
    #  @param offset is used to alter clips start time's (0) sync to media's start time.  
    #  @param media is used if
    #  @param subClips is used if
    #  @param FPS is used if 
    def __init__(self, ranges=aRange(),media=aMedia(),speed=1.0,offset=aTime(0.0),fadeIN=aTime(0.0),fadeOUT=aTime(0.0)):
        self.ranges=ranges
        self.media=media
        self.speed=speed
        self.offset=self.testObject(offset)
        self.fadeIN=self.testObject(fadeIN)
        self.fadeOUT=self.testObject(fadeOUT)
        #### these are not initialized - atributes are not have use yet, just for the record 
        ## for defining the shape of the fade curve
        # self.fadeINtangetStart=45
        # self.fadeINtangetStart=45
        # self.fadeOUTtangetStart=45
        # self.fadeOUTtangetStart=45
        ## for defining what happpens before and after the clip starts
        # self.preInfinity=0
        # self.postInfinity=0
        ## defines if the speed shoud be over ridden by the parents playbackRate (FPS or sampleRate or such)
        # self.forcePlaybackRate=0
        ## possible nesting of clips
        # self.subClips=[]
        ####
    ## returns media's time at certain point in time - clips speed and offset are evaluated 
    #  @param time - point on time
    #  @param reltive - if true, media's start time is converted to 0
    #  @retval media's time at given time as aTime 
    ### CET CLIPTIME, CLIP IN,OUT;DURATION
    ### above with offset: GET MEDIA TIME,  GET MEDIA IN OUT; 
    
    #### help functions to convert time spaces of range,clip and media 
    ## basically just adding offset to clips's time 
    #  @param - offset to to media's tc, clip's own offset is used by default    
    def clipAsMedia(self,time=aTime(),offset=None):
        time=self.testObject(time)
        if not offset:
            offset=self.offset
        else:
            offset=self.testObject(offset)
        return time+offset
    ## converts certain point on clips's TC to range's time - clips IN is in sync with range'sbut clips speed is evaluated into the reasult
    #  @param time - point in time in clip's internal TC
    #  @retval time as ranges absolute time 
    #  @note the function sets clip's IN time and range's IN time to sync before evaluating the speed
    def clipAsRange(self,time=aTime()):
        time=self.testObject(time)
        return self.ranges.getIN()+ aTime((time.asTime()-self.ranges.getIN().asTime())/self.speed)
    ## basically just removing offset from media 
    #  @param - offset to to media's tc, clip's own offset is used by default    
    def mediaAsClip(self,time=aTime(),offset=None):
        time=self.testObject(time)
        if not offset:
            offset=self.offset
        else:
            offset=self.testObject(offset)
        return time-offset
    # same as clipAsRange but evaluates offset
    #  @param time - point in time in maedia's internal TC 
    #  @offset - offset to to media's tc, clip's own offset is used by default
    #  @retval time as ranges absolute time 
    def mediaAsRange(self,time=aTime(),offset=None):
        time=self.testObject(time)
        if not offset:
            offset=self.offset
        else:
            offset=self.testObject(offset)
        return self.clipAsRange() - offset
    ## coverts certain point in range's time into clip's TC- clips IN is in sync with ranges in but clips speed is evaluated into the reasult 
    #  @param time - absolute time on range
    #  @retval time as clips internal time where speed is evaluated
    #  @note the function sets clip's IN time and range's IN time to sync before evaluating the speed
    def rangeAsClip(self,time=aTime()):
        time=self.testObject(time)
        return self.ranges.getIN()+ aTime((time.asTime()-self.ranges.getIN().asTime())*self.speed)
    ## basically same function as rangeAsClip but is modified with offset
    #  @param time - absolute time on range
    #  @param - offset to to media's tc, clip's own offset is used by default
    #  @retval time as media's internal time where speed and offset are evaluated
    #  @note the function sets media's IN time and range's IN time to sync before evaluating the speed
    def rangeAsMedia(self,time=aTime(),offset=None):
        time=self.testObject(time)
        if not offset:
            offset=self.offset
        else:
            offset=self.testObject(offset)
        return self.rangeAsClip(time) + offset 
    ####functions to return IN and OUT points and durations 
    ## shortcut to range's IN time 
    #  @retval clip's absolute (&range's) IN time as aTime 
    def IN(self):
       return self.ranges.getIN()
    ## shortcut to range's OUT time 
    #  @retval clip's absolute (&range's) OUT time as aTime 
    def OUT(self):
       return self.ranges.getOUT()
    ## shortcut to range's duration 
    #  @retval clip's absolute (&range's) duration as aTime 
    def duration(self):
       return self.ranges.getDuration()
    ## clips IN time 
    #  @retval clips (&range's) IN time as aTime
    #  @note this is obsolete because the IN point is in sync with range regardless of speed
    def clipIN(self):
       return self.rangeAsClip(self.ranges.getIN())
    ## same as clip's OUT time in clip's internal TC 
    #  @retval clips (&range's) OUT time as aTime 
    def clipOUT(self):
       return self.rangeAsClip(self.ranges.getOUT())
    ## same as range's duration 
    #  @retval clips duration as aTime 
    def clipDuration(self):
       return aTime(self.ranges.getDuration().asTime()*self.speed)
    ## media's IN time in media's internal timecode 
    #  @retval medias's IN time as aTime in media's own time code
    def mediaIN(self):
       return self.rangeAsMedia(self.ranges.getIN())
    ## media's OUT time 
    #  @retval media's OUT time as aTime 
    def mediaOUT(self):
       return self.rangeAsMedia(self.ranges.getOUT())
    ## same as clips's duration - obsolete because clipDuration returns the smae value
    #  @retval meedias) duration as aTime 
    def mediaDuration(self):
       return aTime(self.ranges.getDuration().asTime()*self.speed)
    #### functions to modify classes atributes
    ## set's the offset by default the offset is set to media's start time to sync clip and media
    #  @param time - if none media's start time is used   
    #  @retval none  
    def setOffset(self, time=None):
        if not time:
            time=self.media.getStart()
        else:
            time=self.testObject(time)
        self.offset=time
    def setSpeedFPS(self):
        pass
    # override setattr to ensure the datatypes for time units to be aTime
    def __setattr__(self, name, value):
        if name=='fadeIN' or name=='fadeOUT' or name=='offset':
            value=self.testObject(value)
        self.__dict__[name]=value


'''to be con't
rng=aRange(2,2,3)
media=aMedia(5,20)

bclip=aBaseClip(rng,media,2.0,5)
print 'clip'
print bclip.rangeAsClip(2).asTime()
print 'mediatime test'
print bclip.rangeAsMedia(2).asTime()
print 'rangetime from clip'
print bclip.mediaAsClip(2).asTime()
print 'clip out'
print bclip.OUT().asTime()
print bclip.clipOUT().asTime()
print 'media'
print bclip.mediaIN().asTime()
print bclip.mediaOUT().asTime()


## TO DO CHECK WHAT HAPPENS WHEN aTime is inited as int 0 - something wrong
## should second init be forced to float?


clip=aRange(1,2,3)
print clip.getParentOUT('frames')

    def getIN(self, tFormat='aTime'):
        if tFormat=='aTime':
            return self.IN
        if tFormat=='seconds':
            return self.IN.asTime()
        if tFormat=='frames':
            return self.IN.asFrames()
        if tFormat=='SMPTE':
            return self.IN.asSmpte()
        
    ## returns the parentIN time as object
    #  @retval parent (clip or track) IN point as aTime
    def getparentIN(self):
        return self.parentIN
    ## returns the parentOUT time as object
    #  @retval parent (clip or track) OUT point as aTime
    def getparentOUT(self):
        return self.parentIN+self.duration
    ## returns the OUT time relative to clips own TC
    #  @retval parent (clip or track) IN point as aTime
    def getOUT(self):
        return self.parentIN
        
    # override setAttr to ensure the datatypes for time units to be aTime
    def __setattr__(self, name, value):
        self.__dict__[name]=value
        print name
        if name=='fadeIN' or name=='fadeOUT' or name=='tcOffset':
            value=self.testObject(value)
            self.__dict__[name]=value


 

## a base class to describe a clip on a track 
#  @retval new object (also by +-*/ operations)
class aBaseClip(aTimeTest):
    #  @param IN point in to the clips own time space clip starts from zero
    #  @param parentIN a sync point to parent's time (for example Edit's global time)
    #  @param duration duration in real time (not clip's internal time code)
    #  @param clip's playback speed, affect's clips internal tc  
    #  @param speed the range content is "played"
    ##  @param tcOffset is used if
    ##  @param media is used if
    ##  @param subClips is used if
    ##  @param FPS is used if
    
    def __init__(self, IN=aTime(0.0), parentIN=aTime(0.0), duration=aTime(0.0),speed=1.0,tcOffset==aTime(0.0),fadeIN=aTime(0.0),fadeOUT=aTime(0.0)):
        self.IN=self.testObject(IN)
        self.parentIN=self.testObject(parentIN)
        self.duration=self.testObject(duration)
        self.speed=speed
        self.fadeIN=fadeIN
        self.fadeOUT=fadeOUT
        ## these are not initialized - atributes are not have use yet, just for the record 
        # for defining the shape of the fade curve
        # self.fadeINtangetStart=45
        # self.fadeINtangetStart=45
        # self.fadeOUTtangetStart=45
        # self.fadeOUTtangetStart=45
        ## for defining what happpens before and after the clip starts
        # self.preInfinity=0
        # self.postInfinity=0
        ## defines if the speed shoud be over ridden by the parents playbackRate (FPS or sampleRate or such)
        #self.forcePlaybackRate=0
    ## returns the IN time as object
    #  @retval IN point as aTime, or defined by tFormat
    def getIN(self, tFormat='aTime'):
        if tFormat=='aTime':
            return self.IN
        if tFormat=='seconds':
            return self.IN.asTime()
        if tFormat=='frames':
            return self.IN.asFrames()
        if tFormat=='SMPTE':
            return self.IN.asSmpte()
        
    ## returns the parentIN time as object
    #  @retval parent (clip or track) IN point as aTime
    def getparentIN(self):
        return self.parentIN
    ## returns the parentOUT time as object
    #  @retval parent (clip or track) OUT point as aTime
    def getparentOUT(self):
        return self.parentIN+self.duration
    ## returns the OUT time relative to clips own TC
    #  @retval parent (clip or track) IN point as aTime
    def getOUT(self):
        return self.parentIN
        
    # override setAttr to ensure the datatypes for time units to be aTime
    def __setattr__(self, name, value):
        self.__dict__[name]=value
        print name
        if name=='IN' or name=='parentIN' or name=='duration' or name=='fadeIN' or name=='fadeOUT' or name=='tcOffset':
            value=self.testObject(value)
            self.__dict__[name]=value
 
clip=aBaseClip(1,2,3)
print clip.getIN('frames')

  
    ## returns object attributes as SMPTE,replacing speed with parent OUT - useful for writing EDL
    #  @retval all class atributes as they are - range duration = [-1]
    ## returns object attributes
    #  @retval all class atributes as aTime objects and range's duration (index[-1])
    def asArray(self):
        return self.IN, self.OUT, self.parentIN, self.speed,self.OUT-self.IN
    ## returns object time as seconds,replacing speed with parent OUT - useful for writing EDL
    #  @retval in/out and duratuin infi in seconds

    def asSmpte(self, FPS=aDefaultFPS(), returnAsList=0, dotFormat=':::'):
        return self.IN.asSmpte(FPS, returnAsList,dotFormat), self.OUT.asSmpte(FPS, returnAsList,dotFormat), self.parentIN.asSmpte(FPS, returnAsList,dotFormat), (self.OUT+(self.parentIN-self.IN)).asSmpte(FPS, returnAsList,dotFormat),(self.OUT-self.IN).asSmpte(FPS, returnAsList,dotFormat)
    #TO DO: get setAttr convert time input to aTime
    ## returns object attributes as SMPTE,replacing speed with parent OUT - useful for writing EDL
    #  @retval all class atributes as they are - range duration = [-1]
    def asFrames(self, FPS=aDefaultFPS()):
        print type(self.IN)
        return self.IN.asFrames(FPS), self.OUT.asSmpte(FPS, returnAsList,dotFormat), self.parentIN.asSmpte(FPS, returnAsList,dotFormat), (self.OUT+(self.parentIN-self.IN)).asSmpte(FPS, returnAsList,dotFormat),(self.OUT-self.IN).asSmpte(FPS, returnAsList,dotFormat)
    #TO DO: __getAttr__ and __setAttr__ 
    def __setAttr__(self,name,value):
        print 'how the hell does this work?'
    def __add__(self, other):
        print 'TO DO'
    def __sub__(self, other):
        print 'TO DO'





       
## a base video properties 
#  @retval new object 
class aVideoProperties(object):
    def __init__(self,  FPS=aDefaultFPS(), x=0, y=0, bitDepth=8, fileFormat='', compression=''):
        self.FPS=FPS
        self.x=x
        self.y=y
        self.bitDepth=bitDepth
        print 'TO DO etc.'

## a base audio properties 
#  @retval new object 
class aAudioProperties(object):
    def __init__(self, bitDepth=16, numOfChannles=1,samples=44100):
        self.bitDepth=bitDepth
        print 'TO DO etc.'
         
## a base media container 
#  @retval new object 
class aMedia(aPath,aMediaProperties):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='',name='',search=[]):
        aMediaProperties.__init__(self,start,end)
        aPath.__init__(self,path,name,search)

## a base video container 
#  @retval new object 
class aVideo(aMedia):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='',name='',search=[], properties=aVideoProperties()):
        aMedia.__init__(self, start, end, FPS, path, name, search)
        self.properties=properties

## a base audio container 
#  @retval new object        
class aAudio(aMedia):
    def __init__(self, start=aTime(0.0), end=aTime(0.0), FPS=aDefaultFPS(), path='', name='',search=[], properties=aVideoProperties()):
        aMedia.__init__(self, start, end, FPS, path, name, search)
        self.properties=properties

## Container class for clips not used yet
class aClips(list):
    #  @param trackType: 0=base 1=video 2=audio
    def __init__(self,items=[],clipType=0):
        #list.__init__(self,items)
        self.clipType=clipType
        self.typeList=[aBaseClip, aVideoClip, aAudioClip]
        for i in items:
            self.append(i)
    ## this prevents of adding clips with same source media - this is useful media bins are not used
    def safeAppend(self, item):
        items=list(self)
        media=self.getMediaPaths
        if type(item)==aAudioClip or type(item)==aVideoClip  or type(item)==aBaseClip:
            if not item.media.path in paths:
                items.append(item)
                list.__init__(self,items) 
        else:
            print 'Can not append type ', type(item), ' to tracks'
    def getMediaPaths(self):
        paths=[]
        for item in self.media:
            paths.append(item.path)
        return path
    


## video clip used in track
class aVideoClip(aBaseClip):
    def __init__(self, ranges=aRange(), media=aVideo(), infinity=[0,0], sourcePath=aPath('','UNKNOWN'),clips=aClips()):
        aBaseClip.__init__(self, ranges, media, infinity, sourcePath, clips)
        

## audio clip used in track
class aAudioClip(aBaseClip):
    def __init__(self, ranges=aRange(), media=aVideo(),infinity=[0,0], sourcePath=aPath('','UNKNOWN'),clips=aClips()):
        aBaseClip.__init__(self, ranges, media, infinity, sourcePath, clips)


        

## base track object used by edit as a timeline. Track contains aClips   
class aBaseTrack(aBaseClip):
    def __init__(self, name='', clips=aClips()):
        self.name=name
        self.clips=clips

## video track object used by edit as layers. Track contains clips 
class aVideoTrack(aBaseTrack):
    def __init__(self, name='', clips=aClips(),opacity=1.0):
        self.name=name
        self.clips=clips
        self.opacity=opacity

## audio track object used by edit as a layers. Track contains clips   
class aAudioTrack(aBaseTrack):
    def __init__(self, name='', clips=aClips(),volume=0.0, channels=2):
        self.name=name
        self.clips=clips
        self.volume=volume
        self.channels=channels

## Container class for tracks
class aTracks(list):
    #  @param trackType: 0=aBaseTrack 1=video 2=audio
    def __init__(self,items=[],trackType=0):
        #list.__init__(self,items)
        self.trackType=trackType
        self.typeList=[aBaseTrack, aVideoTrack, aAudioTrack]
        for i in items:
            self.append(i)
    ## append overided - this prevents of adding track objects with same name 
    def append(self, item):
        items=list(self)
        names=self.getNames()
        if type(item)==aAudioTrack or type(item)==aVideoTrack  or type(item)==aBaseTrack:
            #how about new tracks with empty names??!!!
            if not item.name in names:
                items.append(item)
                list.__init__(self,items) 
        else:
            print 'Can not append type ', type(item), ' to tracks'
    def getNames(self):
        names=[]
        for item in self:
            names.append(item.name)
        return names
            

      
## class that can contain aTracks and aBins. Can write supported EDL types or parse them to aClips and aTracks. Currently supported formats: CMX3600
#  @retval  new aEdit object (also by +/- operation)
class aEdit(aEditEvent):
    #  @param name is used as deafult for writing files or describe the edit.
    #  @param range= array of aEditEvent objects, usually just one object that definen IN and OUT time
    #  @param tracks = array of track objects - the placement in list defines the visibility. The topomost layer is at index 0  
    #  @note info such as resolution and audio sample rate, current time etc. can be included by extending the video and audio properties classes
    def __init__(self, path=aPath(),ranges=aRange,tracks=aTracks(),bins=[],video=aVideoProperties(),audio=aAudioProperties()):
        self.ranges=ranges
        self.bins=bins
        self.tracks=tracks
        self.video=video
        self.audio=audio
        self.path=path
    ## adds more time to edit or joins two edits
    def __add__(self, other):
        time=0.0
        if type(other)==aTime:
#taa on vaarin, pitaa theda oma luokka RANGEILLE
            self.end=self.end+other.time
        if type(other)==aEdit:
            aEdit.bins=aEdit.bins+other.bins
            #join tracks when know how to do it
            #how about fps differences?
        else:
            time=self.time+float(other)
        return aTime(time)
    def __sub__(self, other):
        time=0.0
        if type(other)==aTime:
            time=self.time-other.time
        else:
            time=self.time-float(other)
        return aTime(time)
    ## FOR EDL PARSING

    ##
    def parseEdl(self, fName='', fFormat='vegas'):
        i,tracks,clips=0,{},{}
        rCheck,wCheck=1,1
        try:
            f = open(fName, 'r')
        except IOError:
            f=[]
            print 'Could not open file:' + fName + '\nIt might be protected or used by another user'
        media=[]
        for line in f:
            #kahtellaa...
            if len(line.strip())>1:
                if i==0:
                    self.path.name=line.strip().split(' ')[-1]
                    i=i+1
                elif i==1 and line.strip().replace(':','').split(' ')[0]=='FCM':
                    if not 'non' in line.lower():
                        print line, 'DROP FRAME NOT SUPPORTED!!'
                    i=i+1
                else:
                    line=line.strip().split(' ')
                    try:
                        eventNum=float(line[0])
                        if 'V' in line[3]:
                            currentTrack=self.tracks.append(aVideoTrack(line[3]))
                            #clip=currentTrack.clips.safeAppend()
                            #p.append(line[3])
                        else:
                            currentTrack=self.tracks.append(aAudioTrack(line[3]))
                            
                    except ValueError:
                        print line
        print 'hep', tracks, 'hep', self.tracks
##                    if '*' in line: 
##                        if 'clip' in line.lower()                         
##                            print len(line)
##                    print line
##                    a=line.split(' ')
##                    print 'a:', a
##                    print 'b:', line.strip().split(' ')
##      
jaa=aEdit()
jippu=[aEditEvent(10,20)]
jaa.ranges=jippu
#jaa.ranges.IN=aTime(21)
#jaa.ranges.OUT=aTime(34)
print 'in time', jaa.ranges[0].IN.asSmpte()
print 'info', jaa.ranges[0].asTime()
#jaa=aEdit('kakka', 'film/buu', (aEditEvent(11.22,20.5)))
#print jaa.ranges.asSmpte(jaa.FPS)
#print jaa.duration.asFrames(jaa.FPS)
klip=aEditEvent(0,10.3344)
klip.IN=aTime(5.5)
print klip.asTime(), 'klipdur'
print klip.asSmpte()
jaa.parseEdl('/media/USB DISK/vegasEDL_strip.edl', 'vegas')
jaa.parseEdl('E:/vegasEDL_strip.edl', 'vegas')
print jaa.tracks.getNames()

#\xef\xbb\xbf
muu=aTracks([1,2,3,4])

print muu
print type(muu)
muu.append('kakka')

haa=aTracks([aVideoTrack('juuso'),aVideoTrack('polja')])
print haa.getNames()
print haa

'''
