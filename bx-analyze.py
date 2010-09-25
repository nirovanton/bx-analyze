############################################################################
#    Copyright (C) 2010 by John Harris <harrisj@mnstate.edu>               #
#                                                                          #
#    This program is free software; you can redistribute it and or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

import sys
import png
import numpy
import itertools
import optparse

class Bxanalysis:
    def __init__(self,argv):
        self._tolerance = False
        self._row = ""
        self._width = ""
        self._slide = ""
        self._mask = 0
        self._verbose = False
        self._Xi = False
        self._Xf = False
        self._Yi = False
        self._Yf = False
        self._image = ""
 
        usage = "usage: %prog [options]"
        parser = optparse.OptionParser(usage=usage)
        variables, arguments = self._parseOptions(argv, parser)

        self._tolerance = variables.tolerance
        self._row = variables.row
        self._width = variables.width
        self._slide = variables.slide
        self._verbose = variables.verbose
        self._Xi = variables.Xi
        self._mask = variables.mask
        self._Xf = variables.Xf
        self._Yi = variables.Yi
        self._Yf = variables.Yf
        self._image = variables.image

    def _parseOptions(self, argv, parser):
        row_selection_help_list = [
            "This option allows you to so specify a specific row. ",
            "When a row number is not specified, the program will ",
            "analyze every row in the given .png image."
            ]
        parser.add_option('--row', '-r', default='all',
            help=''.join(row_selection_help_list))
        
        tolerance_help_list = [
            "The tolerance setting allows you to establish a base ",
            "brightness value at which the program detects wrinkles. ",
            "By default the tollerance is set to -15 for the fft.",
            ]
        parser.add_option('--tolerance', '-t', default=-15,
            help=''.join(tolerance_help_list))

        width_help_list = [
            "The width settings alow you to specify the minimum ",
            "and maximum width values for wrinkle detection. By ",
            "default, once a wrinkle is detected, it needs to be ",
            "in the range: 2 - 9 pixels , -w 2:9",
            ]
        parser.add_option('--width', '-w', default='2:9',
            help=''.join(width_help_list))

        verbose_help_list = [
            "There are 2 levels of verbosity:  Low and High.",
            "Low: prints out the average wavelength / line.",
            "High: prints out every wrinkle match / line.",
            ]  
        parser.add_option('--verbose', '-v', default=False,
            help=''.join(verbose_help_list))
        
        slide_help_list = [
            "This option allows you to specify the pdms settings. ",
            "The pdms within an image shall be isolated to either ",
            "side, you need to specify a tolerance, span, range, ",
            "and side.   -s 10:39:5:right ",
            "'consder a span of pixels 10 long with an intensity ",
            "of 39 +/- 5  on the right side to be pdms.'",
            ]
        parser.add_option('--slide', '-s', default='none',
            help=''.join(slide_help_list))

        position_help_list = [
            "You can specify both a starting position and an ",
            "ending position as the range over which the program ",
            "will count wrinkles. The default is an entire row. ",
            "I.E: analizing row 34 from x=400 to 1000",
            "   -r 34 -s 400 -e 1000",
            ]
        parser.add_option('--Xi', '-x', default=False,
            help=''.join(position_help_list))
        parser.add_option('--Xf','-e', default=False,
            help='')
        parser.add_option('--Yi', '-y', default=False,
             help='')
        parser.add_option('--Yf','-b', default=False,
             help='')
  
        image_help_list = [
            "you need to specify the file, a directory path ",
            "will be needed if the file is not in the same ",
            "dir as this script,"
            ]
        parser.add_option('--image', '-i', default='',
            help=''.join(image_help_list))

        mask_help_list = [
            "The mask option specifies how many consecutive 0's "
            "are appended to the begining of the mask array. "
            "These are used  to filter out the longer wavelegths "
            "from the fourier transforms that are applied to "
            "each row."
            ]
        parser.add_option('--mask','-m',default = 10,
            help=''.join(mask_help_list))

        return parser.parse_args()
    
    def run(self):
        pass

if __name__ == "__main__": 

    app = Bxanalysis(sys.argv)

    lambda_array = []

    success = 0
    pixel_ratio = (1/(3.552))  # microns/pixel
    wrinkle_count = 0
    png_file = png.Reader(app._image)
    width, height, iterable, something_else = png_file.read()
    image_array = numpy.vstack(itertools.imap(numpy.uint8, iterable))
    w_min,w_max = app._width.split(":")



#Todo place all of these into an error function.
    if (app._row != 'all') and (app._Yi != False or app._Yf != False):
        print "Error: You cannot specify a single row [ -r ] and a range [ Yi or Yf ] fix one."
        sys.exit()
    if ((app._Yf != False) and (app._Yi != False) and (int(app._Yi) > int(app._Yf))):
        print "Error: Your Yf is less than Yi, switch them around please."
        sys.exit()
    if ((app._Xf != False) and (app._Xi != False) and (int(app._Xi) > int(app._Xf))):
        print "Error: Your Xf is less than Xi, switch them around please."
        sys.exit()
    if (int(app._Xi) < 0 or int(app._Xi) > width):
        print "Error: Specified coordinates are out of pixel range!"
        sys.exit()
    if (int(app._Xf) < 0 or int(app._Xf) > width):
        print "Error: Specified coordinates are out of pixel range!"
        sys.exit()
    if (int(app._Yi) < 0 or int(app._Yi) > height):
        print "Error: Specified coordinates are out of pixel range!"
        sys.exit()
    if (int(app._Yf) < 0 or int(app._Yf) > height):
        print "Error: Specified coordinates are out of pixel range!"
        sys.exit()
    if (int(w_min) > w_max):
        print "Error: Your width quantities are bass-ackwards."
        sys.exit()


    #Establishing the Y boundaries
    if app._row != 'all':
        y_start = int(app._row)
        y_stop = int(app._row)
    else:
        if app._Yi == False:
            y_start = 0
        else:
            y_start = int(app._Yi)
        if app._Yf == False:
            y_stop = height-1
        else: 
            y_stop = int(app._Yf)
    
    #Establishing the X boundaries
    if app._Xi == False:
        x_start = 0
    else:
        x_start = int(app._Xi)
    if app._Xf == False:
        x_stop = width
    else:
        x_stop = int(app._Xf)


    #gap the output
    print ""
    pdms_detection = False
    y_index = y_start
    while y_index <= y_stop:
        x_index = x_start
        pdms_pixel_count = 0
        row_total = 0
        white_count = 0
        row_array = []
        pdms_location = 'none'
        row_fault = False
        pdms = False
        while x_index < x_stop:
            if image_array[y_index][x_index] == 255:
                if x_index == 0:
                    pdms_location = 'left'
                if x_index == x_stop - 1:
                    pdms_location = 'right'
                white_count += 1
            row_array.append(int(image_array[y_index][x_index]))
            x_index += 1
        if white_count > x_stop/3:
            print "row:",y_index," - Row wavelength estimate has been aborted."
            row_fault == True

        
        # PRE WHITE-OUT
        """
        if pdms:
            if app._slide != 'none':
                if (pdms_location == 'left' and x_index <= int(width)/2) \
                or (pdms_location == 'right' and x_index >= int(width)/2):
                    if image_array[y_index][x_index] >= (int(slide_tol)-int(slide_tol_range)):
                        if image_array[y_index][x_index] <= (int(slide_tol)+int(slide_tol_range)):
                            if pdms_pixel_count == 0 and pdms == False : 
                                pdms_Xi = x_index
                            pdms_pixel_count += 1
            #               print x_index,"count",pdms_pixel_count
                            if x_index == x_stop-1:
                                row_total += pdms_pixel_count
                    if image_array[y_index][x_index] < int(slide_tol)-int(slide_tol_range) \
                    or image_array[y_index][x_index] > int(slide_tol)+int(slide_tol_range) \
                    or x_index == x_stop-1:
                        if pdms_pixel_count >= int(span): 
                            pdms_Xf = x_index
                            pdms = True
                            pdms_detection = True
                            row_total += pdms_pixel_count
           #                print "DETECTED:",x_index-pdms_pixel_count+1,"to",x_index
                        pdms_pixel_count = 0
            x_index += 1
#            print "start:",pdms_Xi,"stop:",pdms_Xf

        if pdms:
            swnt_Xi = x_start
            swnt_Xf = x_stop
            if pdms_location == 'left':
                swnt_Xi = pdms_Xf
                swnt_Xf = x_stop 
            if pdms_location == 'right':
                swnt_Xi = x_start
                swnt_Xf = pdms_Xi
        else:
            swnt_Xi = x_start
            swnt_Xf = x_stop
            pdms_row_location = 'none'
   
        print "row:",y_index,"- pdms-detection",pdms_row_location," :: start", swnt_Xi, "stop",swnt_Xf
        y_index += 1
        """
        
        fourier = numpy.fft.rfft(row_array)
        mask_array = []
        mask_filter_size = int(app._mask)
        mask_count = 0
        s_start = 0
        while mask_count < len(fourier):
            if mask_count < mask_filter_size:
                mask_array.append(0)
            else:
                mask_array.append(1)
            mask_count +=1
        final_product = numpy.fft.irfft(fourier*mask_array)
        fft_dict = {}
        
        dict_index = x_start
        for line in final_product:
            fft_dict[dict_index] = line
            dict_index += 1
        
        for key in fft_dict.keys():
            if fft_dict[key] <= int(app._tolerance):
                success += 1
                if success == 1:
                    s_start = key
            else:
                if (success >= int(w_min) and success < int(w_max)):
                    wrinkle_count += 1
                    if app._verbose == 'high':
                        print "("+str(s_start)+","+ str(y_index)+")->("+ str(key)+","+ str(y_index)+")"
                success = 0

        if app._verbose == "fft":        
            counter = 0
            image_indexer = x_start
            while counter < len(final_product):
                print str(image_indexer)+":"+str(row_array[counter])+":"+str(final_product[counter])
                counter += 1
                image_indexer += 1

        delta_x = x_stop - x_start - white_count
        if wrinkle_count >= 1:
            wavelength = (delta_x*pixel_ratio)/wrinkle_count
            lambda_array.append(wavelength)
            if app._verbose != False and app._verbose != 'fft':
                print "row:"+str(y_index)+", wrinkles:"+str(wrinkle_count)+", lambda:"+str(wavelength)
            lambda_array.append(wavelength)
            wrinkle_count = 0
        y_index += 1

        #gap the row output
        if app._verbose == 'high':
            print "Calculated over",delta_x,"pixels of nanotubes."
            print ""
        if y_index > y_stop and app._verbose == 'low':
            print ""

    lambda_sum = 0
    
    for wavelength in lambda_array:
        lambda_sum += wavelength

    if app._verbose != 'fft':
        print "=========================================================="
        print "Image File:\t\t"+app._image
        if pdms_detection:
            print "Scan type:\t\tEdge"
        else:
            print "scan type:\t\tMiddle"        
        print "Starting (x,y):\t\t("+str(x_start)+","+str(y_start)+") pixels"
        print "Ending (x,y):\t\t("+str(x_stop)+","+str(y_stop)+") pixels"
        print "Mask size:\t\t"+str(app._mask)
        print "Sample tolerance:\t"+str(app._tolerance)
        print "Wrinkle size range:\t"+w_min+" to "+w_max+" pixels"
        print "Approx wavelength\t"+str(lambda_sum/len(lambda_array))+" microns"
        print "=========================================================="
