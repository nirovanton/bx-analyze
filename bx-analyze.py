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
        self._tolerance = 0
        self._row = ""
        self._fft = 0
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
        self._verbose = variables.verbose
        self._Xi = variables.Xi
        self._fft = variables.fft
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
            "By default the tollerance is set to 50 for regulat scans.",
            ]
        parser.add_option('--tolerance', '-t', default=50,
            help=''.join(tolerance_help_list))

        verbose_help_list = [
            "There are 2 levels of verbosity:  Low and High.",
            "Low: prints out the average wavelength / line.",
            "High: prints out every wrinkle match / line.",
            ]  
        parser.add_option('--verbose', '-v', default=False,
            help=''.join(verbose_help_list))
        
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

        fft_help_list = [
            "The fft option specifies that you would like to run ",
            "the fft filter on the rows. the passed value specifies ",
            "the mask filter strength.",
            ]
        parser.add_option('--fft','-f',default='',
            help=''.join(fft_help_list))

        return parser.parse_args()
    
    def run(self):
        pass


if __name__ == "__main__": 

    ###    Opening the image file and creating a 2d array of intesity.
    app = Bxanalysis(sys.argv)
    lambda_array = []
    pixel_ratio = (1/(3.552))  # microns/pixel
    wrinkle_count = 0
    png_file = png.Reader(app._image)
    width, height, iterable, image_info = png_file.read()
    image_array = numpy.vstack(itertools.imap(numpy.uint8, iterable))


    #TODO: place all of these into an error function.
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


    ###    Establishing the Y boundaries
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


    ###    Establishing the X boundaries
    if app._Xi == False:
        x_start = 0
    else:
        x_start = int(app._Xi)
    if app._Xf == False:
        x_stop = width
    else:
        x_stop = int(app._Xf)


    ###    Extracting the file name from the full file path
    image = app._image.split("/")
    i = 0
    while i<= len(image):
        if i == len(image):
            png_file = image[i-1]
        i+=1
    

    ###    Gathering FFT information
    if app._fft != '':
        fft_data = app._fft.split(":")
        fft = True
        tolerance = int(fft_data[1])
        fft_mask = int(fft_data[0])
    else:
        fft = False
        tolerance = int(app._tolerance) 


    ###    Collecting data from the individual rows.
    pdms_detection = False
    y_index = y_start
    while y_index <= y_stop:
        x_index = 0
        pdms_pixel_count = 0
        row_total = 0
        white_count = 0
        row_array = []
        pdms_location = 'none'
        pdms_count = 0
        row_fault = False
        pdms = False
        lambda_sum = 0
        while x_index < width:
            if x_index < x_start or x_index > x_stop:
                row_array.append(70)
                white_count += pdms_count
            else:    
                if image_array[y_index][x_index] == 70:
                    if x_index == 5:
                        pdms_location = 'left'
                    if x_index == x_stop -1 and pdms_count >= 5:
                        white_count += pdms_count
                        pdms_location = 'right'
                    pdms_count += 1
                else:
                    if pdms_count >= 5:
                        white_count += pdms_count
                    pdms_count = 0
                row_array.append(int(image_array[y_index][x_index]))
            x_index += 1
       
        if white_count >= .75*(x_stop-x_start) and app._verbose != 'file':
            print "row:"+str(y_index)+" Row analysis aborted, not enough data for an accurate answer."
            y_index += 1
            continue

        
        ###    Passing each array to the FFT 
        final_dict = {}
        if fft:
            fourier = numpy.fft.rfft(row_array)
            mask_array = []
            mask_count = 0
            s_start = 0
            while mask_count < len(fourier):
                if mask_count < fft_mask:
                    mask_array.append(0)
                else:
                    mask_array.append(1)
                mask_count +=1
            final_product = numpy.fft.irfft(fourier*mask_array)
            dict_index = 0
            for line in final_product:
                final_dict[dict_index] = line
                dict_index += 1
        else:
            dict_index = 0
            while dict_index < len(row_array):
                final_dict[dict_index] = row_array[dict_index]
                dict_index += 1
          
        
        ###    Scanning the pixel array for wrinkles
        success = False
        ind = 1
        avg = 0
        for key in final_dict.keys():
            if key > 1 and key < (width-1) \
            and ( key > x_start and key < x_stop) \
            and final_dict[key] <= tolerance:
               if final_dict[key] < final_dict[key-1] \
               and final_dict[key] < final_dict[key+1]:
                   success = True
               if final_dict[key] == final_dict[key-1]\
               and final_dict[key] < final_dict[key+1]\
               and final_dict[key] < final_dict[key-2]:
                   success = True
            if success:
                wrinkle_count += 1
                if app._verbose == 'high':
                    print ind, "\t(x,y): ("+ str(key)+","+ str(y_index)+")"
                    ind += 1
            success = False
        ind = 1

        
        ###    FFT verbosity output
        if app._verbose == "plot":
            counter = 0
            while counter < len(row_array):
                if app._fft == '':
                    print str(counter)+":"+str(row_array[counter])
                    counter += 1
                else:
                    print str(counter)+":"+str(row_array[counter])+":"+str(final_product[counter])
                    counter += 1

        
        ###    Calculating lambda for each row.
        delta_x = x_stop - x_start - white_count
        if wrinkle_count >= 1:
            wavelength = (delta_x*pixel_ratio)/wrinkle_count
            lambda_array.append(wavelength)
            if app._verbose != False and app._verbose != 'plot' and app._verbose != 'file':
                print "row:"+str(y_index)+", wrinkles:"+str(wrinkle_count)+", lambda:"+str(wavelength)
            lambda_array.append(wavelength)
            wrinkle_count = 0

        #gapping the output.
        if app._verbose == 'high':
            print "Calculated over",delta_x,"nanotube pixels."
  
        y_index += 1

        
    ###    Printing the stats for every file.
    for wavelength in lambda_array:
        lambda_sum += wavelength
    if app._verbose == 'file':
        if app._fft == '':
            print png_file,"\t",lambda_sum/len(lambda_array),"um\ttol:",tolerance
        else:
            print png_file,"\t",lambda_sum/len(lambda_array),"um\tfft:",app._fft
    if app._verbose != 'plot' and app._verbose != 'file':
        print "=========================================================="
        print "Image File:\t\t"+png_file
        if fft:
            print "FFT tolerance:\t\t"+str(tolerance)
            print "FFT mask value:\t\t"+str(fft_mask)
        else:
            print "Sample tolerance:\t"+str(tolerance)
        print "Starting (x,y):\t\t("+str(x_start)+","+str(y_start)+") pixels"
        print "Ending (x,y):\t\t("+str(x_stop)+","+str(y_stop)+") pixels"
        print "Approx wavelength\t"+str(lambda_sum/len(lambda_array))+" microns"
        print "=========================================================="
        
