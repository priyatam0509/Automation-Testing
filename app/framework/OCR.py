"""
On-screen character recognition module for use in GVR Python automation.

Utilizes Google's open-source Tesseract OCR engine.
Provides functions for reading, finding, locating, and clicking on text.
Please do not import this module directly in your scripts.
Instead, import generic.py and use the wrappers it provides.
"""

__author__ = 'Cassidy Garner'

from PIL import Image, ImageGrab, ImageOps, ImageFilter
from app import pytesseract
from time import sleep, time
import logging
import pywinauto
import sys
import math
import inspect

#############
# Constants #
#############

# Constants for Tesseract page segmentation modes I have found useful
# If you're having trouble with OCR not picking up characters/strings, you might
# want to try these.
# Consult Tesseract (CMD: tesseract --help-psm) for more information.
PSM_DEFAULTPAGESEG = 3      # Automatic page segmentation, no orientation + script detection. Tesseract default
PSM_UNIFORMTEXTBLOCK = 6    # Assume a single uniform block of text
PSM_SPARSETEXT = 11         # Find as much text as possible in no particular order
PSM_SPARSEOSD = 12          # Sparse text with orientation+script detection. Our default

# Constants for click_location
LEFT = -1
CENTER = 0
RIGHT = 1

tessdata_dir = "D:/Automation/Program Files/Tesseract-OCR/tessdata"
log = logging.getLogger()

###################
# Debug variables #
###################

initial_click_coords = (320, 10)

# Image processing settings
scaleFactor = (3,3)
resize_filter = Image.ANTIALIAS
img_filters = [ImageFilter.SMOOTH]
save_img = None
show_img = False
screenshot_workaround = True

cache = []
cache_attempt = False
max_cache_size = 25
#############
# Functions #
#############

def searchAndClick(searchText, color='000000', bbox=None,
                   tolerance='000000', psm=(12, 6, 3, 11), timeout=0,
                   clicks=1, occurrence=1, maxDist=0, click_location=0,
                   offset=(0,0), filter_strings=[]):
    """
    @Creator: Cassidy Garner
    @Name: searchAndClick
    @Description: Use Tesseract OCR to locate and click on a string.
    @params:
        >searchText (String,list): The text to search for.
        >color (String,list:'000000'): The hex color(s) of text to search for.
        >bbox (list,tuple:None): The bounding box (left, top, right, bottom)
               in which to search for the text. (Optional)
        >tolerance (String:'000000'): The amount of variation in the color to
                    accept.
        >psm (int,tuple:(12,6,3,11)): The page segmentation mode(s)
               to attempt. See Tesseract documentation for more info.
        >timeout (int:0): Approx. number of seconds to continue attempting
                  to find the text. All PSMs will be attempted before timing out.
        >clicks (int:1) Number of times to click on the string, if found.
        >occurrence (int:1): Which instance of the string to click on if
                     it is found multiple times. Order from left to right, top
                     to bottom.
        >maxDist (int:0): The maximum Levenshtein distance between the result
                  and the search text to consider a match.
        >click_location (int:0): which part of the string to click on. 
                         0 for center, -1 for left end, 1 for right end
        >offset (tuple:(0,0)): how much to offset the click relative to the 
                 string's location.
        >filter_strings (list,str:[]): Strings to remove from OCR output before 
                         searching it.
    @return:
        >tuple: The coordinates clicked on
    @throws:
    """

    # Try a cached bounding box, if this is a repeated call without a bbox
    global cache_attempt, cache
    args = inspect.getargvalues(inspect.currentframe()).locals
    # Cache attempt global to prevent recursion. Kind of ugly.
    if not cache_attempt and bbox is None:
        result = [None]
        del args['bbox'] # We know bbox is None, no need to compare it
        for cached_args in cache:
            # Check if args match a cached call (minus bounding box)
            if args.items() <= cached_args.items():
                print("Trying cached bounding box %s" % str(cached_args['bbox']))
                cache_attempt = True
                tmp_psm = cached_args['psm']
                cached_args['psm'] = 12
                result = searchAndClick(**cached_args)
                cached_args['psm'] = tmp_psm
                cache_attempt = False
                if result is not None:
                    return result

    if isinstance(psm, int): # convert integer input to list format
        psm = [psm]
    if type(filter_strings) == str:
        filter_strings = [filter_strings]
    pywinauto.mouse.click(coords=initial_click_coords) # Click somewhere out of the way to prevent mouseover and highlight shenanigans
    bestDist = float('inf')
    bestResult = ''
    bestPSM = 0
    
    # Try to find + click text until timeout
    startTime = time()
    while time() - startTime <= timeout:
        for mode in psm:
            log.debug('With PSM %s:' % mode)
            # Use OCR to find coords of text
            coords, dist, result, bboxes = getTextCoords(searchText=searchText,
                                                         color=color,
                                                         tolerance=tolerance,bbox=bbox,
                                                         psm=mode, maxDist=maxDist,
                                                         coord_location=click_location,
                                                         filter_strings=filter_strings)

            # Record new best result for later logging
            if dist < bestDist:
                bestDist = dist
                bestResult = result
                bestPSM = mode

            # Check if there are enough occurrences of the search string
            if occurrence > len(coords):
                if maxDist > 0:
                    log.debug('Expected at least %s strings within distance %s of '
                        'search string %s, but only found %s'
                        % (occurrence, maxDist, searchText, len(coords)))
                else:
                    log.debug('Expected at least %s occurrences of %s but only found '
                        '%s' % (occurrence, searchText, len(coords)))
                continue

            # Check for result(s) that qualify as matches
            if (coords[occurrence-1][0] >= 0 and coords[occurrence-1][1] >= 0
                and dist <= maxDist):
                click_coords = (coords[occurrence-1][0] + offset[0],
                                 coords[occurrence-1][1] + offset[1])
                if len(coords) > 1:
                    if dist == 0:
                        msg = ('Found %s occurrences of %s at locations %s. '
                              'Clicking occurrence %s at %s' % (len(coords),
                              searchText, coords, occurrence, click_coords))
                    else:
                        msg = ('Found %s strings with distance %s from the '
                              'search string %s at locations %s. Clicking '
                              'occurrence %s at %s' % (len(coords), dist,
                              searchText, coords, occurrence, click_coords))
                else:
                    if dist == 0:
                        msg = 'Found %s, clicking at %s' % (searchText,
                                                            click_coords)
                    else:
                        msg = ('Found a string with distance %s from the search'
                              ' string %s, clicking at %s' % (dist, searchText,
                              click_coords))

                # Success. Click the text! 
                for i in range(clicks):
                    pywinauto.mouse.click(coords=click_coords)
                log.debug(msg)

                # Cache the args for this call and the bbox for the found text
                # to speed things up if the same call is made again.
                args['bbox'] = tuple(bboxes[occurrence-1])
                if args not in cache:
                    cache.append(args)
                    if len(cache) >= max_cache_size:
                        cache.pop(0)

                return click_coords

        # Failed. Check for timeout    
    else:
            if maxDist > 0:
                msg = ('Did not find any strings within distance %s of the '
                      'search string %s. Minimum distance found was %s'
                      % (maxDist, searchText, dist))
            else:
                msg = 'Did not find %s' % searchText
            log.warning('%s. Closest OCR result (using page seg mode %s): \n%s'
                    % (msg, bestPSM, bestResult))
            return None

def findText(searchText, color='000000', bbox=None, tolerance='000000',
             psm=(12, 6, 3, 11), timeout=0, maxDist=0, filter_strings=[]):
    """
    @Creator: Cassidy Garner
    @Name: findText
    @Description: Use Tesseract OCR to determine if one or more strings are
                  present on-screen.
    @params:
        >searchText (str,list): The text to search for.
        >color (str,list:'000000'): The hex color(s) of text to search for.
        >bbox (int, tuple:None): The bounding box (left, top, right, bottom)
               in which to search for the text. (Optional)
        >tolerance (str:'000000'): The amount of variation in the color to
                    accept.
        >psm: (int, tuple:(12,6,3,11)): The page segmentation mode(s)
               to attempt. See Tesseract documentation for more info.
        >timeout: (int:0) Approx. number of seconds to continue attempting
                  to find the text. All PSMs will be attempted before timing out.
        >maxDist: (int:0) The maximum Levenshtein distance between the result
                  and the search text to consider a match.
        >filter_strings (list,str:[]): Strings to remove from OCR output before 
                         searching it.
    @return:
        >bool: Whether or not the search text was found successfully
    @throws:
    """

    startTime = time()
    if isinstance(searchText, str):
        searchText = [searchText]
    if isinstance(psm, int): # convert integer input to list format
        psm = [psm]
    if type(filter_strings) == str:
        filter_strings = [filter_strings]
    numTexts = len(searchText)
    minTotalDist = float('inf')
    bestPSM = 0
    bestResult = ''
    missingStrings = []
    while time() - startTime <= timeout:
        for mode in psm:
            log.debug('With PSM %s:' % mode)
            # Use OCR to read the screen
            tessOut = OCRRead(bbox, color, tolerance, mode)
            tessOutNoBreak = tessOut.replace('\n', ' ')
            tessOutNoWhtsp = tessOutNoBreak.replace(' ', '')

            failures = []
            totalDist = 0
            # Look for matches in the OCR output
            for text in searchText:
                searchTextNoWhtsp = text.replace(' ', '')
                for string in filter_strings: # Remove filtered strings
                    string = string.replace('\n', '').replace(' ', '')
                    searchTextNoWhtsp = searchTextNoWhtsp.replace(string, '')
                matches, dist = closestMatch(tessOutNoWhtsp, searchTextNoWhtsp)
                totalDist += dist

                if dist <= maxDist:
                    if dist == 0:
                        log.debug('Exact match found: %s' % text)
                    else:
                        log.debug('Match(es) for %s found with distance %s: %s'
                            % (text, dist, matches))
                    # Remove the match from our result so we can't find it again
                    tessOutNoWhtsp = tessOutNoWhtsp.replace(matches[0], '', 1) 
                else:
                    log.debug('Did not find %s' % text)
                    failures.append(text)

            if len(failures) == 0:
                if numTexts > 1:
                    msg = 'Successfully found all %s strings' % numTexts
                    log.debug(msg)
                else:
                    msg = 'Exact match found: %s' % text
                log.debug(msg)
                return True
            else:
                # Save closest match for logging purposes in case we fail
                if totalDist < minTotalDist:
                    minTotalDist = totalDist
                    bestResult = tessOutNoBreak
                    bestPSM = mode
                    missingStrings = failures
                
    else:
        # Time's up, fail with an informative error message
        if maxDist == 0:
            if numTexts > 1:
                msg = 'Did not find %s' % missingStrings
            else:
                msg = 'Did not find %s' % searchText
        else:
            if numTexts > 1:
                msg = ('Did not find %s within distance %s'
                % (missingStrings, maxDist))
            else:
                msg = ('Did not find %s within distance %s'
                % (searchText, maxDist))
        log.warning('%s. Closest OCR result (with page seg mode %s):\n %s'
                % (msg, bestPSM, bestResult))
        return False

def OCRRead(bbox=None, color='000000', tolerance='000000', psm=12):
    """
    @Creator: Cassidy Garner
    @Name: OCRRead
    @Description: Use Tesseract OCR to read on-screen text.
    @params:
        >bbox (list,tuple:None) The bounding box in which to read.
        >color (String,list:'000000'): The hex color(s) of text to read.
        >tolerance (String:'000000'): The amount of variation in the color to
                    accept.
        >psm: (int:12) The page segmentation mode to use.
              See Tesseract documentation for more info. (Default: 12)
    @return:
        >String: the text found by Tesseract.
    @throws:
    """
    # ImageGrab can't see the WPF GUI, use print screen instead
    if screenshot_workaround:
        #NOTE: If this fails we may need to retry the print screen function
        pywinauto.keyboard.send_keys('{PRTSC}')
        #Timeout loop waiting for the clipboard to load
        starttime = time()
        while time() - starttime <= 30:
            img = ImageGrab.grabclipboard()
            if img != None:
                break
        else:
            log.error("Failed to generate a failure screenshot within timeout")
            return None
        if bbox is not None:
            img = img.crop(bbox)     
    else:
        img = ImageGrab.grab(bbox)
    img = processImage(img, color, tolerance)
    return pytesseract.image_to_string(img, None, f"--psm {psm} --tessdata-dir '{tessdata_dir}'")

def getTextCoords(searchText, bbox=None, color='000000', tolerance='000000',
                  psm=12, maxDist=0, coord_location=0, filter_strings=[]):
    """
    @Creator: Cassidy Garner
    @Name: getTextCoords
    @Description: Use Tesseract OCR to locate the coordinates string.
    @params:
        >searchText (String): The text to search for.
        >bbox (int list,tuple:None): The bounding box (left, top, right, bottom)
               in which to search for the text. (Optional)
        >color (String,list:'000000'): The hex color(s) of text to search for.
        >tolerance (String:'000000'): The amount of variation in the color to
                    accept.
        >psm (int:12): The page segmentation mode to use. See Tesseract
              documentation for more info.
        >maxDist (int:0): The maximum Levenshtein distance between the result
                  and the search text to consider a match.
        >coord_location (int:0): which part of the string to return coords for. 
                         0 for center, -1 for left end, 1 for right end
        >filter_strings (list,str:[]): Strings to remove from OCR output before 
                         searching it.
    @return:
        >tuple: List of coord pairs for each match, the distance between the
                matches and the search text (only the result(s) with least
                possible dist will be returned), and the raw OCR result.
    @throws:
    """
    if type(filter_strings) == str:
        filter_strings = [filter_strings]
    
    searchText = searchText.replace(' ', '')
    # ImageGrab can't see the WPF GUI, use print screen instead
    if screenshot_workaround:
        #NOTE: If this fails we may need to retry the print screen function
        pywinauto.keyboard.send_keys('{PRTSC}')
        #Timeout loop waiting for the clipboard to load
        starttime = time()
        while time() - starttime <= 30:
            img = ImageGrab.grabclipboard()
            if img != None:
                break
        else:
            log.error("Failed to generate a failure screenshot within timeout")
            return None
        if bbox is not None:
            img = img.crop(bbox)   
    else:
        img = ImageGrab.grab(bbox)
    img = processImage(img, color, tolerance)
    # Pass image to Tesseract which does the heavy lifting for us
    tesseractOut = pytesseract.image_to_boxes(img, None, f"--psm {psm} --tessdata-dir '{tessdata_dir}'")
    if tesseractOut == '':
        log.debug('Did not find any text!')
        return [[-1, -1]], float('inf'), '', []
    textFound = []
    # Construct list of characters and their bounding boxes
    charBoxes = tesseractOut.split('\n') 
    for box in charBoxes:
        textFound.append(box[0]) # Build string of characters found
    textFound = ''.join(textFound)
    for string in filter_strings: # Remove filtered strings
        string = string.replace('\n', '').replace(' ', '')
        left = textFound.find(string)
        right = left + len(string)
        textFound = textFound.replace(string, '')
        charBoxes = charBoxes[:left] + charBoxes[right:]
    log.debug('Found text:\n%s' % textFound.encode('utf-8'))
    result = textFound
    
    # Find matching text
    matches, dist = closestMatch(textFound, searchText)
    numMatches = len(matches)
    if dist > maxDist or numMatches == 0:
        return [[-1, -1]], dist, result, []
    coords = []
    bboxes = []
    startIndex = 0
  
    for i in range(numMatches):
        lIndex = textFound.find(matches[i])
        midIndex = lIndex + int(len(matches[i])/2)
        rIndex = lIndex + len(matches[i]) - 1

        # Record bounding box for the match
        lBox = [int(n) for n in charBoxes[lIndex].split()[1:5]]
        rBox = [int(n) for n in charBoxes[rIndex].split()[1:5]]
        y_size = img.size[1]/scaleFactor[1]
        match_bound = [int(lBox[0]/scaleFactor[0]-5), int(y_size-rBox[3]/scaleFactor[1]-5),
                       int(rBox[2]/scaleFactor[0]+5), int(y_size-lBox[1]/scaleFactor[1]+5)]
        coord = [-1, -1]
        if coord_location == 0:
            # Get the center coords of the middle character
            mBox = charBoxes[midIndex].split()[1:5]
            coord[0] = int(math.floor((int(mBox[2])+int(mBox[0]))/(2*scaleFactor[0])))
            coord[1] = int(y_size
                           - math.floor((int(mBox[3])+int(mBox[1]))
                                        /(2*scaleFactor[1])))
        elif coord_location < 0:
            # Get the center-left edge of the leftmost character
            coord[0] = int(int(lBox[0])/scaleFactor[0])
            coord[1] = int(y_size
                           - math.floor((int(lBox[3])+int(lBox[1]))
                                        /(2*scaleFactor[1])))
        else:
            # Get the center-right edge of the rightmost character
            coord[0] = int(int(rBox[2])/scaleFactor[0])
            coord[1] = int(y_size
                           - math.floor((int(rBox[3])+int(rBox[1]))
                                        /(2*scaleFactor[1])))
            
        # Account for bounding box offset
        if bbox is not None:
            coord[0] += bbox[0]
            coord[1] += bbox[1]
            match_bound[0] += bbox[0]
            match_bound[1] += bbox[1]
            match_bound[2] += bbox[0]
            match_bound[3] += bbox[1]
        
        # Cache the result
        bboxes.append(tuple(match_bound))
        coords.append(tuple(coord))
        # Remove the match we just grabbed so we can find the next one
        # (but maintain the same length so we don't break coord calculations)
        textFound = textFound.replace(matches[i], ' '*len(matches[i]), 1) 

    return coords, dist, result, bboxes

def processImage(img, color='000000', tolerance='000000'):
    """
    @Creator: Cassidy Garner
    @Name: processImage
    @Descrption: Transform an image into something readable by Tesseract.
    @params:
        >img (PIL.Image): the image to process
        >color (String,list:'000000') the RGB color(s) to filter for
        >tolerance (String:'000000') the amount of variance to accept in the
                    color
    @return:
        >PIL.Image: the filtered image
    @throws:
    """
    if isinstance(color, str):
        color = [color]
    source = img.split()
    R, G, B = 0, 1, 2
    images = []
    for c in color:
        rVal = int(c[0:2], 16)
        gVal = int(c[2:4], 16)
        bVal = int(c[4:6], 16)
        rTol = int(tolerance[0:2], 16)
        gTol = int(tolerance[2:4], 16)
        bTol = int(tolerance[4:6], 16)

        # Filter each band for the specified color value, then paste them together exclusively
        rBand = source[R].point(lambda i: (i >= rVal-rTol and i <= rVal+rTol)
                                and 255)
        gBand = source[G].point(lambda i: (i >= gVal-gTol and i <= gVal+gTol)
                                and 255)
        bBand = source[B].point(lambda i: (i >= bVal-bTol and i <= bVal+bTol)
                                and 255)
        rBand.paste(gBand, None, rBand)
        rBand.paste(bBand, None, rBand)
        rBand = ImageOps.invert(rBand)
        images.append(rBand)

    # Merge the image for each desired color into a single image
    mergedImg = images.pop()
    for image in images:
        mergedImg = Image.composite(mergedImg, image, image)
        
    # Upscale and filter the image to make it easier to read
    newSize = (img.size[0]*scaleFactor[0], img.size[1]*scaleFactor[1])
    finalImg = mergedImg.resize(newSize, resize_filter)
    for img_filter in img_filters:
        finalImg = finalImg.filter(img_filter)
    finalImg.convert('L')
    if save_img is not None:
        finalImg.save(save_img)
    if show_img:
        finalImg.show()
    return finalImg

def closestMatch(text, pattern):
    """
    @Creator: Cassidy Garner
    @Name: closestMatch
    @Description: Fuzzy string matching algorithm using Levenshtein distance.
                  Uses dynamic programming, so it's fast!
    @params:
        >text (String): the string to search within
        >pattern (String): the string to try and match
    @return:
        >tuple: A list of the closest matches, and the Levenshtein distance
                between them and the search string.
    @throws:
        >ClosestMatchError: Raised if something goes wrong computing matches.
                            Should never be thrown unless I messed something up.
    """
    
    tLen = len(text)
    pLen = len(pattern)

    ## Initialize data array.
    ## D(0,j) = 0
    minDists = [[float('inf') for x in range(tLen+1)] for y in range(pLen+1)]
    for j in range(tLen+1):
        minDists[0][j] = 0

    ## For all (i,j) in minDists, compute the minimum edit distance...
    ## ...between the first i chars of P and all substrings of T ending at j
    ## D(i,j) = min( D(i-1,j)+1,
    ##               D(i-1,j-1)+(Pi != Tj),
    ##               D(i,j-1)+1 )
    ## And save the computation path
    paths = [[-1 for x in range(tLen+1)] for y in range(pLen+1)]
    for j in range(tLen+1):
        for i in range(1,pLen+1):
            if j == 0:
                minDists[i][j] = minDists[i-1][j] + 1
                paths[i][j] = 1
            else:
                # Compute minDists[i][j]
                path1 = minDists[i-1][j] + 1
                path2 = minDists[i-1][j-1] + (pattern[i-1] != text[j-1])
                path3 = minDists[i][j-1] + 1
                minDists[i][j] = min(path1, path2, path3)
                # Save computation path
                if minDists[i][j] == path1: paths[i][j] = 1
                elif minDists[i][j] == path2: paths[i][j] = 2
                else: paths[i][j] = 3

    ## Compute the closest match(es) by following the computation path backwards
    ## from the min. value(s) in last row
    minDist = float('inf')
    starts = []
    matches = []
    for j in range(tLen+1):
        if minDists[pLen][j] < minDist:
            starts = []
            starts.append(j)
            minDist = minDists[pLen][j]
        elif minDists[pLen][j] == minDist:
            starts.append(j)
    for start in starts:
        y = start
        x = pLen
        while x > 0 and y > 0:
            if paths[x][y] == 1:
                x = x-1
            elif paths[x][y] == 2:
                x = x-1
                y = y-1
            elif paths[x][y] == 3:
                y = y-1
            else:
                log.error('ERROR: Invalid computation path')
                msg = ('Tried to follow a bad path in closest match ',
                      'algorithm. This should never happen! Contact Cassidy!')
                raise ClosestMatchError(msg)
            
        matches.append(text[y:start])
    return (matches, minDist)

class ClosestMatchError(RuntimeError):
    """Exception to raise if closest match algorithm somehow breaks."""
    def __init__(self, arg):
        self.args = arg