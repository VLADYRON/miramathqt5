
#------------------------------------------------------------------------------
#   Copyright (c) 2008
#       Roger Hale    roger314159@hotmail.com
#
#   This file is part of MiraMath.
#
#   MiraMath is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   MiraMath is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with MiraMath.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------
from keywords import *

_FONTSCALEFACTOR                 = 0.8       # How much font changes when going to sub/super-scripts
_MINFONTSIZE                     = 6         # Min font size for sub/superscripts
_DIVIDE_LINE_VERT_SHIFT_FUDGE    = 0.25      # Fine tune vertical shift of divide
_MATRIX_COL_SPACING              = 0.8       # Spacing between columns
_MATRIX_ROW_SPACING              = 0.4       # Spacing between rows
_SUMMATION_LIMIT_VERT_SPACING    = 0.3       # Vertical spacing between summation limits and sum sign
_SIZE_OF_INTEGRAL_CHAR           = 1.3       # Size of int char
_INTGERAL_LIMIT_VERT_SPACING     = 0.5       # Spacing between integral limits and int char
_SPACE_AFTER_INT_VAR             = 0.7       # Horiz spacing to the right of variable of integration
_SPACING_BETWEEN_INT_BODY_AND_D  = 0.6       # Horiz spacing between integral body and the dee
_SPACING_BETWEEN_PROGRAM_LINES   = 0.85      # Vert spacing between program lines
_ADDITIONAL_BAR_HEIGHT           = 0.3       # Addtional height of determinant and norm lines
_ADDITIONAL_PAREN_HEIGHT         = 0.2       # Additional height of parenthesis
_FILENAME_VERT_SPACING           = 0.5       # Spacing below image and above file name
_LIMIT_VERT_SPACING              = 0.6       # Spacing below lim
_SUBSTITUTION_HORIZ_SPACING      = 0.5       # Spacing between vertical line and substitution values
_ADDITIONAL_CEILING_HEIGHT       = 0.5       # Extra height of ceil and floor operators


class Layout:
    """This class lays out the equations"""
    def __init__(self):
        self.minFontSize = 6                     # Min font size for sub/super scripts

        #Dictionary containing keywords and corresponding methods
        self.formatingMethods = \
        { \
            Keyword.POWERSTART          : self.handlePowerKeyword, \
            Keyword.TRANSPOSESTART      : self.handlePowerKeyword, \
            Keyword.HERMITIANSTART      : self.handlePowerKeyword, \
            Keyword.CONJUGATESTART      : self.handlePowerKeyword, \
            Keyword.SUPERSCRIPTSTART    : self.handlePowerKeyword, \
            Keyword.SUBSCRIPTSTART      : self.handleSubscriptKeyword, \
            Keyword.INDEXSTART          : self.handleIndexKeyword, \
            Keyword.LEFTPAREN           : self.handleLeftParenKeyword, \
            Keyword.LEFTSQUARE          : self.handleLeftParenKeyword, \
            Keyword.SQUAREROOTSTART     : self.handleSquarerootKeyword, \
            Keyword.ORDERNROOTSTART     : self.handleOrderNRootKeyword, \
            Keyword.DIVIDESTART         : self.handleDivideKeyword, \
            Keyword.MATRIXSTART         : self.handleMatrixKeyword, \
            Keyword.ARRAYSTART          : self.handleMatrixKeyword, \
            Keyword.SUMSTART            : self.handleSumKeyword, \
            Keyword.PRODUCTSTART        : self.handleSumKeyword, \
            Keyword.MATRIXSUMSTART      : self.handleMatrixSumKeyword, \
            Keyword.RANGESUMSTART       : self.handleRangeSumKeyword, \
            Keyword.RANGEPRODUCTSTART   : self.handleRangeSumKeyword, \
            Keyword.DETERMINANTSTART    : self.handleDeterminantKeyword, \
            Keyword.ABSOLUTESTART       : self.handleDeterminantKeyword, \
            Keyword.NORMSTART           : self.handleDeterminantKeyword, \
            Keyword.INTEGRALSTART       : self.handleDefiniteIntegralKeyword, \
            Keyword.INDEFINTEGRALSTART  : self.handleIndefiniteIntegralKeyword,  \
            Keyword.TABLESTART          : self.handleTableKeyword, \
            Keyword.AVERAGESTART        : self.handleAverageKeyword, \
            Keyword.PROGRAMSTART        : self.handleProgramKeyword,  \
            Keyword.VECTORIZESTART      : self.handleAverageKeyword,  \
            Keyword.FILESTART           : self.handleFileKeyword,  \
            Keyword.LIMITSTART          : self.handleLimitKeyword,   \
            Keyword.SUBSUPSTART         : self.handleSubSupKeyword,  \
            Keyword.SUBSTITUTIONSTART   : self.handleSubstitutionKeyword,  \
            Keyword.FLOORSTART          : self.handleFloorCeilKeyword,  \
            Keyword.CEILSTART           : self.handleFloorCeilKeyword,  \
        }

    def layoutEquationPart(self, eqnlist, start, end, fontsize):
        """This function recursively calls itself to determine where to draw characters"""
        px = 0
        py = 0
        top_of_previous_character = fontsize
        i = start
        while i < end:  # Must use while loop since loop variable i gets modified inside loop
            c = eqnlist[i]

            if c.object_type == 'character':
                #No keyword found, process character
                c.setSize(fontsize)
                c.setPosition(px, py)
                top_of_previous_character = c.top
                px += c.width

            #Look in dictionary for method corresponding to keyword
            elif self.formatingMethods.has_key(c.value):
                method = self.formatingMethods[c.value]
                i, px, py, top_of_previous_character = method(eqnlist, i, c, px, py,  fontsize, top_of_previous_character)

            #End of while loop, increment counter
            i += 1

        #Now get size of current equation part and return the size
        return self.getSizeOfEquationPart(eqnlist[start:end])

    def moveEquationPart(self, eqnlist, deltax, deltay):
        [c.moveBy(deltax, deltay) for c in eqnlist]

    def getSizeOfEquationPart(self, eqnlist):
        #Now get size of equation part and return the size
        left = 10000
        right = -10000
        top = 10000
        bottom = -10000
        for c in eqnlist:
            if c.object_type == 'character':
                x, y = c.getPosition()
                w = c.width
                t = c.top
                b = c.bottom
                if x+w > right:
                    right = x + w
                if x < left:
                    left = x
                if y+t < top:
                    top = y + t
                if y+b > bottom:
                    bottom = y + b
        return left, right, top, bottom

    #**********************Methods below do the actual laying out*****************************
    def handlePowerKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        n = c.match  #Index of matching keyword

        #Fix fontsize
        powerfontsize = fontsize * _FONTSCALEFACTOR
        if powerfontsize < _MINFONTSIZE:
            powerfontsize = _MINFONTSIZE

        #Get size of power operand
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+1, n, powerfontsize)

        #Now shift contents of power up so that it fits inside
        self.moveEquationPart(eqnlist[i+1: n], px, py+top_of_previous_character-bottom)

        #Now skip ahead to characters after power
        px += (right - left)
        i = n

        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleSubscriptKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        n = c.match

        subscriptfontsize = fontsize * _FONTSCALEFACTOR
        if subscriptfontsize < _MINFONTSIZE:
            subscriptfontsize = _MINFONTSIZE

        #Get size of subscript
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+1, n, subscriptfontsize)

        #Now shift down contents of subscript
        self.moveEquationPart(eqnlist[i+1: n], px, py+0.5*fontsize)

        #Now skip ahead to characters after subscript
        px += (right - left)
        i = n

        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleIndexKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        n = c.match

        indexfontsize = fontsize * _FONTSCALEFACTOR
        if indexfontsize < _MINFONTSIZE:
            indexfontsize = _MINFONTSIZE

        #Get size of index
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+1, n, indexfontsize)

        #Now shift contents of index down
        self.moveEquationPart(eqnlist[i+1: n], px, py-top)

        #Now skip ahead to characters after index
        px += (right - left + 0.2 * fontsize)

        i = n

        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleLeftParenKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Find size of characters inside of parenthesis
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+3, n-2, fontsize)

        #Compute vertical shift of parenthesis if contents is smaller than fontsize
        d = bottom - top
        extra_height = _ADDITIONAL_PAREN_HEIGHT * fontsize
        shifty = 0.5 * extra_height
        if d < fontsize:
            shifty += (fontsize - d) * 0.5

        #Compute size of parentheses
        if -top < fontsize:
            top = -fontsize     # Minimum size of parenthesis
        h = bottom - top + extra_height

        top_of_previous_character = top  # Used by power,superscript

        #Set the size and position of (
        lp = eqnlist[i+1]
        lp.setSize(h, fontsize) # The ( symbol object
        lp.setPosition(px, py+bottom+shifty)

        #Shift contents of parenthesis right by width of left (
        self.moveEquationPart(eqnlist[i+3: n-1], px+lp.width, py)

        #Set size and position of )
        rp = eqnlist[n-1]
        rp.setSize(h, fontsize)
        rp.setPosition(px+lp.width+right-left, py+bottom+shifty)

        total_width = lp.width + right-left + rp.width

        #Compute x position of items following right parenthesis
        px += total_width
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleSquarerootKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Found a square root keyword, now go find contents size recursively
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+3, n-1, fontsize)
        h = bottom - top
        top_of_previous_character = top

        bottom += 2  # Fudge

        #Set the size of the square root
        sqrtchar = eqnlist[i+1]
        sqrtchar.setSize(right-left, h, fontsize)  # The square root symbol object
        sqrtchar.setPosition(px, py+bottom)

        #Now shift contents of square root to right so that it fits inside
        dist = sqrtchar.contentsOffset
        self.moveEquationPart(eqnlist[i+3: n], px+dist, py)

        #Update position of next character after squareroot
        px += sqrtchar.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize
        return i, px, py, top_of_previous_character

    def handleOrderNRootKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        orderfontsize = fontsize * _FONTSCALEFACTOR
        if orderfontsize < _MINFONTSIZE:
            orderfontsize = _MINFONTSIZE

        #Get size of order part
        c1 = eqnlist[i+1] # Order start keyword
        n1 = c1.match     # Index of orderend keyword
        (oleft, oright, otop, obottom) = self.layoutEquationPart(eqnlist, i+2, n1, orderfontsize)
        owidth = oright - oleft

        #Get size of root contents
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, n1+3, n-1, fontsize)
        top_of_previous_character = top
        bottom += 2  # Fudge

        #Set the size of the square root using contents size
        sqrtchar = eqnlist[n1+1]
        sqrtchar.setSize(right-left, bottom-top, fontsize)  # The square root symbol object

        #Get numbers needed to move around the root symbol and order
        x1 = sqrtchar.orderBottomRHCx
        y1 = sqrtchar.orderBottomRHCy

        #Compute how far to the right to move root symbol to make space for root order
        if owidth < x1:
            symboloffsetx = 0
            orderoffsetx = x1 - owidth
        else:
            symboloffsetx = owidth - x1
            orderoffsetx = 0

        #Move the Order part
        self.moveEquationPart(eqnlist[i+2: n1], px+orderoffsetx, py+bottom+y1)

        px += symboloffsetx

        #Move the root symbol, include width of order in calculation of x movement
        sqrtchar.setPosition(px, py+bottom)

        #Move the contents of square root to right so that it fits inside
        dist = sqrtchar.contentsOffset
        self.moveEquationPart(eqnlist[n1+3: n], px+dist, py)

        #Update position of next character after squareroot
        px += sqrtchar.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleDivideKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match
        old_py = py

        #Find index of numerator end keyword
        c1 = eqnlist[i+1] # Numerator start keyword
        n1 = c1.match  # Index of NUMEND keyword
        divide_line_index = n1 + 1

        #Get size of numerator
        (num_left, num_right, num_top, num_bottom) = self.layoutEquationPart(eqnlist, i+2, n1, fontsize)
        num_width = num_right - num_left
        num_height = num_bottom - num_top

        #Find index of matching denominator keyword
        c2 = eqnlist[n1+2]  # Denominator keyword
        n2 = c2.match     # Index of DENOMEND keyword

        #Get size of denominator
        (denom_left, denom_right, denom_top, denom_bottom) = self.layoutEquationPart(eqnlist, n1+3, n2, fontsize)
        denom_width = denom_right - denom_left
        denom_height = denom_bottom - denom_top

        #Fine tune position so that divide line is lined up with surrounding text
        py -= fontsize * _DIVIDE_LINE_VERT_SHIFT_FUDGE

        #Position the divide line
        div_line = eqnlist[divide_line_index]
        div_line.setPosition(px, py)

        #Compare numerator and denominator sizes
        if num_width >= denom_width:
            #Size the divide line
            div_line.setSize(fontsize, num_width)
            div_line_width = div_line.width

            #Get offset so that num and denom are centered relative to divide line
            div_line_offset = (div_line_width - num_width)/2.0

            #Position numerator relative to line
            num_x = px + div_line_offset
            num_y = py - num_bottom + div_line.top
            self.moveEquationPart(eqnlist[i+2: n1], num_x, num_y)

            #Position denominator relative to line
            delta_x = (num_width - denom_width)/2.0
            denom_x = px + delta_x + div_line_offset
            denom_y = py - denom_top + div_line.bottom
            self.moveEquationPart(eqnlist[n1+3: n2], denom_x, denom_y)

        else:
            #Size the divide line
            div_line.setSize(fontsize, denom_width)
            div_line_width = div_line.width

            #Get offset so that num and denom are centered relative to divide line
            div_line_offset = (div_line_width - denom_width)/2.0

            #Position numerator relative to line
            delta_x = (denom_width - num_width)/2.0
            num_x = px + delta_x + div_line_offset
            num_y = py - num_bottom + div_line.top
            self.moveEquationPart(eqnlist[i+2: n1], num_x, num_y)

            #Position denominator relative to line
            denom_x = px + div_line_offset
            denom_y = py - denom_top + div_line.bottom
            self.moveEquationPart(eqnlist[n1+3: n2], denom_x, denom_y)

        #Adjust px, py to just after end of divide
        px += div_line_width
        py = old_py
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleMatrixKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        """Matrix layout:
        MATRIXSTART LEFTBRACKET
        ROWSTART  ( ELEMENTSTART characters ELEMENTEND ) * num cols ROWEND
        ...
        RIGHTBRACKET MATRIXEND"""

        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match
        nrows = c.rows
        ncols = c.cols

        #Initialize: each element holds max top and bottom coordinates for each
        #matrix row, and the max width of each column
        rowsmaxtop = [0] * nrows
        rowsmaxbot = [0] * nrows
        colsmaxwidth = [0] * ncols

        horiz_spacing = fontsize * _MATRIX_COL_SPACING      # Spacing between columns
        vert_spacing = fontsize * _MATRIX_ROW_SPACING       # Spacing between rows
        bracket_height = -vert_spacing
        matrix_width = 0

        #Find the max height of each row and max width of each column
        m1 = i + 2
        for row in xrange(nrows):
            m1 += 1  # Skip ROWSTART keyword
            for col in xrange(ncols):
                #Find matrix element
                c = eqnlist[m1]    # Get ELEMENTSTART keyword
                m2 = c.match    # Get index to matching ELEMENTEND keyword

                #Get width, top and bottom of each matrix element
                (l, r, t, b) = self.layoutEquationPart(eqnlist, m1+1, m2, fontsize)

                #Calc width of element
                w = r - l

                #For each row find the highest matrix element and for each
                #column find the widest matrix element
                m1 = m2 + 1
                if w > colsmaxwidth[col]:
                    colsmaxwidth[col] = w
                if t < rowsmaxtop[row]:
                    rowsmaxtop[row] = t
                if b > rowsmaxbot[row]:
                    rowsmaxbot[row] = b

            #Add up heights of each row, including spacing between rows
            h = rowsmaxbot[row] - rowsmaxtop[row]
            bracket_height += (h + vert_spacing)

            m1 += 1 # Skip ROWEND keyword

        y = py - bracket_height * 0.5 - rowsmaxtop[0] - fontsize * 0.5

        #Make the brackets a little bigger than contents of matrix
        bracket_height += fontsize

        #Set bracket size
        lbracket = eqnlist[i+1]   # Left bracket
        rbracket = eqnlist[n-1]   # Right bracket
        lbracket.setSize(bracket_height, fontsize)
        rbracket.setSize(bracket_height, fontsize)

        #Now move every element around
        m1 = i + 2  # m1 points to first ROWSTART keyword
        for row in xrange(nrows):
            m1 += 1  # Skip ROWSTART keyword
            x = px + lbracket.width
            for col in xrange(ncols):
                c = eqnlist[m1]    # Get ELEMENTSTART keyword
                m2 = c.match    # Find matching keyword index

                #Now move everythang between START and END keywords
                self.moveEquationPart(eqnlist[m1+1: m2], x, y)

                #make m1 point to next ELEMENTSTART keyword
                m1 = m2 + 1

                #Calc. where to put element in next column to the right
                x += (colsmaxwidth[col] + horiz_spacing)

            if x-px-lbracket.width-horiz_spacing > matrix_width:
                matrix_width = x - px - lbracket.width - horiz_spacing

            #Get vertical offset of next row
            b = rowsmaxbot[row]   # Bottom of current row
            if row < nrows-1:
                t2 = rowsmaxtop[row+1]  #Top of next row
                y += (b - t2 + vert_spacing)  # Amount to shift down next row

            m1 += 1  # Skip ROWEND keyword

        #Move brackets
        bracket_y_pos = y + b + fontsize * 0.5  # Add 0.5*fontsize for the extra padding around contents
        lbracket.setPosition(px, bracket_y_pos)
        px += (lbracket.width + matrix_width)
        rbracket.setPosition(px, bracket_y_pos)
        px += rbracket.width

        #Used for power
        top_of_previous_character = py - bracket_height * 0.5 - fontsize * 0.5
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleSumKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match  # Index of SUMEND

        #Reduce font size for 'from' and 'to' parts
        fromtofontsize = fontsize * _FONTSCALEFACTOR
        if fromtofontsize < _MINFONTSIZE:
            fromtofontsize = _MINFONTSIZE

        #Find size of 'from' part
        c1 = eqnlist[i+2]  # FROMSTART keyword
        n1 = c1.match   # FROMEND
        (from_left, from_right, from_top, from_bottom) = self.layoutEquationPart(eqnlist, i+3, n1, fromtofontsize)
        from_width = from_right - from_left

        #Find size of 'to' part
        c2 = eqnlist[n1+1]  # TOSTART keyword
        n2 = c2.match    # TOEND
        (to_left, to_right, to_top, to_bottom) = self.layoutEquationPart(eqnlist, n1+2, n2, fromtofontsize)
        to_width = to_right - to_left

        #Find size of sum body
        c3 = eqnlist[n2+1]  # BODYSTART
        n3 = c3.match    # BODYEND
        (body_left, body_right, body_top, body_bottom) = self.layoutEquationPart(eqnlist, n2+2, n3, fontsize)
        body_width = body_right - body_left

        #Vertical spacing between sum limits and sum sign
        limit_vert_spacing = _SUMMATION_LIMIT_VERT_SPACING * fontsize

        #Shift entire summation to right if limits are wider than sum sign
        sumchar = eqnlist[i+1]  # Sum character
        sumchar.cursorClickMoveRight = n2 + 1 - i  # Used if mouse clicks on right half of sum sign, move cursor to sum body
        sumchar.setSize(1.8*fontsize)  # Set size of sum character before using it

        #Calc how much to move sum sign vertically so that it is aligned with sumand
        h = sumchar.bottom - sumchar.top
        shifty = (h - fontsize) * 0.5 - sumchar.bottom

        w1 = from_width * 0.5
        w2 = to_width * 0.5
        w3 = sumchar.width * 0.5
        shift1 = w1 - w3
        shift2 = w2 - w3
        shift = 0
        shiftbody = sumchar.width
        if shift1 > 0 or shift2 > 0:
            if shift1 > shift2:  # From is wider than to
                shift = shift1
                shiftbody = w3 + w1 # = 2 * w3 + shift = 2 * w3 + w1 - w3 = w3 + w1
            else:
                shift = shift2
                shiftbody = w3 + w2 # = 2 * w3 + shift = 2 * w3 + w2 - w3 = w3 + w2

        shiftbody += fontsize * 0.6    # Add some spacing between sum sign and body
        px += shift   # Add the correct amount of shift

        #Set the position of the sum symbol
        sumchar.setPosition(px, py+shifty)

        #Shift from part
        fromx = px - shift1
        fromy = sumchar.bottom - from_top + limit_vert_spacing + shifty
        self.moveEquationPart(eqnlist[i+3: n1], fromx, fromy)

        #Shift to part
        tox = px - shift2
        toy = sumchar.top - to_bottom - limit_vert_spacing + shifty
        self.moveEquationPart(eqnlist[n1+2: n2], tox, toy)

        #Shift sum body
        px += shiftbody
        self.moveEquationPart(eqnlist[n2+2: n3], px, py)

        px += body_width

        #Put some space after the end of the sum
        spacechar = eqnlist[n-1]
        spacechar.setSize(fontsize)
        spacechar.setPosition(px, py)

        px += spacechar.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleMatrixSumKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Find size of sum body
        c1 = eqnlist[i+2]   # BODYSTART
        n1 = c1.match    # BODYEND
        (body_left, body_right, body_top, body_bottom) = self.layoutEquationPart(eqnlist, i+2, n1, fontsize)
        body_width = body_right - body_left

        #Shift entire summation to right if limits are wider than sum sign
        sumchar = eqnlist[i+1]   # Sum character
        sumchar.setSize(1.8*fontsize)   # Set size of sum character before using it

        #Calc how much to move sum sign vertical so that it is aligned with integrand
        h = sumchar.bottom - sumchar.top
        shifty = (h - fontsize) * 0.5 - sumchar.bottom
        sumchar.setPosition(px, py+shifty)

        px += (sumchar.width + fontsize * 0.3)   # Add some spacing between sum sign and body

        #Shift sum body
        self.moveEquationPart(eqnlist[i+2: n1], px, py)

        px += body_width
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleRangeSumKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Reduce font size for 'from' and 'to' parts
        fromtofontsize = fontsize * _FONTSCALEFACTOR
        if fromtofontsize < _MINFONTSIZE:
            fromtofontsize = _MINFONTSIZE

        #Find size of 'from' part
        c1 = eqnlist[i+2]   # FROMSTART keyword
        n1 = c1.match    # FROMEND
        (from_left, from_right, from_top, from_bottom) = self.layoutEquationPart(eqnlist, i+3, n1, fromtofontsize)
        from_width = from_right - from_left

        #Find size of sum body
        c2 = eqnlist[n1+1]   # BODYSTART
        n2 = c2.match    # BODYEND
        (body_left, body_right, body_top, body_bottom) = self.layoutEquationPart(eqnlist, n1+2, n2, fontsize)
        body_width = body_right - body_left

        #Vertical spacing between sum limits and sum sign
        limit_vert_spacing = _SUMMATION_LIMIT_VERT_SPACING * fontsize

        #Shift entire summation to right if limits are wider than sum sign
        sumchar = eqnlist[i+1]   # Sum character
        sumchar.setSize(1.8*fontsize)  #Set size of sum character before using it

        #Calc how much to move sum sign vertical so that it is aligned with body
        h = sumchar.bottom - sumchar.top
        shifty = (h - fontsize) * 0.5 - sumchar.bottom

        w1 = from_width * 0.5
        w2 = sumchar.width * 0.5
        if w1 > w2:
            shiftx = w1 - w2
            shiftx2 = shiftx
            shiftbody = w2 + w1
        else:
            shiftx = 0
            shiftx2 = -(w2 - w1)
            shiftbody = sumchar.width

        shiftbody += fontsize * 0.6   # Add some spacing between sum sign and body
        px += shiftx    # Add the correct amount of shift

        #Set the position of the sum symbol
        sumchar.setPosition(px, py+shifty)

        #Shift from part
        fromx = px - shiftx2
        fromy = sumchar.bottom - from_top + limit_vert_spacing + shifty
        self.moveEquationPart(eqnlist[i+2: n1], fromx, fromy)

        #Shift sum body
        px += shiftbody
        self.moveEquationPart(eqnlist[n1+2: n2], px, py)

        px += body_width
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleDeterminantKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Find size of characters inside of parenthesis
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+3, n-2, fontsize)
        width = right - left
        h = bottom - top

        #Set the size and position of |
        leftbar = eqnlist[i+1]
        barfudge = fontsize * _ADDITIONAL_BAR_HEIGHT   # Make the vertical bars a bit longer than height
        barheight = h + 2 * barfudge
        bar_yoffset = (barheight - h) * 0.5 + bottom

        leftbar.setSize(barheight, fontsize)   # The | symbol object
        leftbar.setPosition(px, py+bar_yoffset)

        top_of_previous_character = py + top - barfudge

        #Shift contents of parenthesis right by width of left (
        self.moveEquationPart(eqnlist[i+3: n-2], px+leftbar.width, py)

        #Set size and position of |
        rightbar = eqnlist[n-1]
        rightbar.setSize(barheight, fontsize)
        rightbar.setPosition(px+rightbar.width+width, py+bar_yoffset)

        #Compute x position of items following right parenthesis
        px += (2 * leftbar.width + width)
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleDefiniteIntegralKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Reduce font size for 'from' and 'to' parts
        fromtofontsize = fontsize * _FONTSCALEFACTOR
        if fromtofontsize < _MINFONTSIZE:
            fromtofontsize = _MINFONTSIZE

        #Find size of 'from' part
        c1 = eqnlist[i+3]   # FROMSTART keyword
        n1 = c1.match   # FROMEND
        (from_left, from_right, from_top, from_bottom) = self.layoutEquationPart(eqnlist, i+4, n1, fromtofontsize)
        from_width = from_right - from_left

        #Find size of 'to' part
        c2 = eqnlist[n1+1]   # TOSTART keyword
        n2 = c2.match    # TOEND
        (to_left, to_right, to_top, to_bottom) = self.layoutEquationPart(eqnlist, n1+2, n2, fromtofontsize)
        to_width = to_right - to_left

        #Find size of integral body
        c3 = eqnlist[n2+1]   # BODYSTART
        n3 = c3.match    # BODYEND
        (body_left, body_right, body_top, body_bottom) = self.layoutEquationPart(eqnlist, n2+2, n3, fontsize)
        body_width = body_right - body_left
        body_height = body_bottom - body_top

        #Find size of variable of integration
        c4 = eqnlist[n3+2]   # INVARSTART
        n4 = c4.match     # INTVAREND
        (intvar_left, intvar_right, intvar_top, intvar_bottom) = self.layoutEquationPart(eqnlist, n3+3, n4, fontsize)
        intvar_width = intvar_right - intvar_left

        #Vertical spacing between integration limits and integral sign
        limit_vert_spacing = _INTGERAL_LIMIT_VERT_SPACING * fontsize

        #Get integral characters
        intchar1 = eqnlist[i+1]   # Integral character top
        intchar2 = eqnlist[i+2]   # Integral character bottom

        #Size integral characters
        size_of_integral_part = _SIZE_OF_INTEGRAL_CHAR * fontsize
        intchar1.setSize(size_of_integral_part)
        intchar2.setSize(size_of_integral_part)
        width_of_integral_char = intchar1.width
        height_of_integral_char_part = intchar1.bottom - intchar1.top
        limit_shiftx_fudge = width_of_integral_char * 0.3

        #Create a fudge so that integral character looks vertically centered
        shifty = height_of_integral_char_part * 0.6

        #Determine widths of limits and how much to move things around laterally
        w1 = from_width * 0.5
        w2 = to_width * 0.5
        w3 = width_of_integral_char * 0.5

        #Do some calculations for x-positions. For all calcs assume integral symbol is at x=0
        from_left_edge_position = w3 - limit_shiftx_fudge - w1
        from_right_edge_position = from_left_edge_position + from_width
        to_left_edge_position = w3 + limit_shiftx_fudge - w2
        to_right_edge_position = to_left_edge_position + to_width
        if from_left_edge_position < 0 or to_left_edge_position < 0:  # Does the left hand edge of either limit extend beyond the left hand edge of integral char?
            if from_left_edge_position <= to_left_edge_position:
                px -= from_left_edge_position        # If we get here then from_left_edge_position is negative, hence the minus sign
            else:
                px -= to_left_edge_position            # If we get here then to_left_edge_position is negative, hence the minus sign

        #Set the position of the integral symbol
        intchar1.setPosition(px, py+shifty-height_of_integral_char_part)  #top part
        intchar2.setPosition(px, py+shifty)   # bottom part

        #Shift from part
        fromx = px + from_left_edge_position    # from_left_edge_position can be positive or negative RELATIVE to integral sign position
        fromy = py + shifty + intchar2.bottom - from_top + limit_vert_spacing
        self.moveEquationPart(eqnlist[i+3: n1], fromx, fromy)

        #Shift to part
        tox = px + to_left_edge_position        # to_left_edge_position can be positive or negative RELATIVE to integral sign position
        toy = py + shifty - height_of_integral_char_part + intchar1.top - to_bottom - limit_vert_spacing
        self.moveEquationPart(eqnlist[n1+2: n2], tox, toy)

        #Shift integral body
        if to_right_edge_position > width_of_integral_char or from_right_edge_position > width_of_integral_char:
            #If right edge of either limit extends beyond right edge of integral char then position integral body to the right of both limits
            if to_right_edge_position >= from_right_edge_position:
                px += to_right_edge_position
            else:
                px += from_right_edge_position
        else:
            #If the right edge of neither limit extends beyond right edge of integral char then position integral body to right of integral char
            px += width_of_integral_char
        self.moveEquationPart(eqnlist[n2+2: n3], px, py)

        #Add a little spacing before the 'd'
        px += (body_width + fontsize * _SPACING_BETWEEN_INT_BODY_AND_D)

        #Now move the 'd'
        dee = eqnlist[n3+1]
        dee.setSize(fontsize)
        dee.setPosition(px, py)
        px += dee.width

        #Move integration variable
        self.moveEquationPart(eqnlist[n3+3: n4], px, py)

        px += intvar_width

        #Put some space after the end of the dx
        spacechar = eqnlist[n-1]
        spacechar.setSize(fontsize*_SPACE_AFTER_INT_VAR)
        spacechar.setPosition(px, py)

        px += spacechar.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleIndefiniteIntegralKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Find size of integral body
        c1 = eqnlist[i+3]   # BODYSTART
        n1 = c1.match       # BODYEND index
        (body_left, body_right, body_top, body_bottom) = self.layoutEquationPart(eqnlist, i+4, n1, fontsize)
        body_width = body_right - body_left
        body_height = body_bottom - body_top

        #Find size of variable of integration
        c2 = eqnlist[n1+2]   # INVARSTART
        n2 = c2.match        # INTVAREND index
        (intvar_left, intvar_right, intvar_top, intvar_bottom) = self.layoutEquationPart(eqnlist, n1+3, n2, fontsize)
        intvar_width = intvar_right - intvar_left

        #Get integral characters
        intchar1 = eqnlist[i+1]   # Integral character top
        intchar2 = eqnlist[i+2]   # Integral character bottom

        #Size integral characters
        size_of_integral_part = _SIZE_OF_INTEGRAL_CHAR * fontsize
        intchar1.setSize(size_of_integral_part)
        intchar2.setSize(size_of_integral_part)
        width_of_integral_char = intchar1.width
        height_of_integral_char_part = intchar1.bottom - intchar1.top
        limit_shiftx_fudge = width_of_integral_char * 0.3

        #Create a fudge so that integral character looks vertically centered
        shifty = height_of_integral_char_part * 0.6

        #Set the position of the integral symbol
        intchar1.setPosition(px, py+shifty-height_of_integral_char_part)  #top part
        intchar2.setPosition(px, py+shifty)   # bottom part

        #Position body
        px += width_of_integral_char
        self.moveEquationPart(eqnlist[i+4: n1], px, py)

        #Add a little spacing before the 'd'
        px += (body_width + fontsize * _SPACING_BETWEEN_INT_BODY_AND_D)

        #Now move the 'd'
        dee = eqnlist[n1+1]
        dee.setSize(fontsize)
        dee.setPosition(px, py)
        px += dee.width

        #Move integration variable
        self.moveEquationPart(eqnlist[n1+3: n2], px, py)

        px += intvar_width

        #Put some space after the end of the dx
        spacechar = eqnlist[n-1]
        spacechar.setSize(fontsize*_SPACE_AFTER_INT_VAR)
        spacechar.setPosition(px, py)

        px += spacechar.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleTableKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Get the table widget
        table = eqnlist[i+1]
        table.setFontSize(fontsize)

        h = table.bottom - table.top
        shifty = (h + fontsize)/2
        table.setPosition(px, py-shifty)
        px += table.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleAverageKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        #Find size of characters under bar/arrow
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, i+3, n, fontsize)
        width = right - left
        h = bottom - top

        #Set the size and position of bar/arrow
        bar = eqnlist[i+1]
        bar.setSize(width, fontsize)   # The bar/arrow symbol object
        bar.setPosition(px, py+top)
        shiftx = (bar.width - width) * 0.5

        top_of_previous_character = py + top + bar.top

        #Shift contents
        self.moveEquationPart(eqnlist[i+3: n], px+shiftx, py)

        #Compute x position of items following right parenthesis
        px += bar.width
        i = n

        #Save some data used for cursor positioning in keyword object
        c2 = eqnlist[n]
        c2.cursorX = px
        c2.cursorY = py
        c2.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleProgramKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        vert_spacing = _SPACING_BETWEEN_PROGRAM_LINES * fontsize  #Spacing between lines

        vert_line_char = eqnlist[i+1]   # Vertical line character
        vert_line_char.setSize(fontsize, fontsize)   # Set temp size so that we can get width of vertical line
        vert_line_width = vert_line_char.width

        n1 = i + 3          # Index of LINESTART keyword
        c2 = eqnlist[n1]    # LINESTART keyword
        n2 = c2.match       # Index of LINEEND keyword
        y1 = py - fontsize
        x1 = px + vert_line_width
        total_height = 0

        while(1):
            #Get size of line body
            (left, right, top, bottom) = self.layoutEquationPart(eqnlist, n1+1, n2, fontsize)

            height = bottom - top

            #Set min program line height, in case of only a space on line
            if height < fontsize:
                height = fontsize
                top = -fontsize
                bottom = 0
            height += vert_spacing
            total_height += height

            #Shift contents
            self.moveEquationPart(eqnlist[n1+1: n2], x1, y1-top)

            y1 = y1 + height

            if n2 == n-2:
                break

            n1 = n2 + 1                     # Index of LINESTART keyword
            c2 = eqnlist[n1]                # LINESTART keyword
            n2 = c2.match                   # Index of LINEEND keyword

        vert_line_char.setSize(total_height, fontsize)
        vert_line_char.setPosition(px, py-fontsize+total_height-vert_spacing*0.5)

        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleFileKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        vert_spacing = _SPACING_BETWEEN_PROGRAM_LINES * fontsize  # Spacing between lines

        image = eqnlist[i+1]   # Vertical line character
        image_width = image.width
        image_height = image.bottom - image.top

        #Get size of file name part
        n1 = i + 2          # Index of FILENAMESTART
        c1 = eqnlist[n1]    # FILENAMESTART keyword
        n2 = c1.match       # Index of FILENAMEEND keyword
        (left, right, top, bottom) = self.layoutEquationPart(eqnlist, n1+1, n2, fontsize)
        file_name_width = right - left

        #Move file name and image
        y1 = py + image_height - top + _FILENAME_VERT_SPACING * fontsize
        if file_name_width < image_width:
            image.setPosition(px, py)
            x1 = px + (image_width - file_name_width)/2
            self.moveEquationPart(eqnlist[n1+1: n2], x1, y1)
        else:
            x1 = px + (file_name_width - image_width)/2
            image.setPosition(x1, py)
            self.moveEquationPart(eqnlist[n1+1: n2], px, y1)

        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleLimitKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize
        n = c.match

        limsize = fontsize * _FONTSCALEFACTOR
        plussize = fontsize * _FONTSCALEFACTOR * _FONTSCALEFACTOR

        c1 = eqnlist[i+1]  # 'lim' character
        c1.setSize(fontsize)
        c2 = eqnlist[i+2]  # arrow character
        c2.setSize(limsize)
        c3 = eqnlist[i+3]  # +/- character
        c3.setSize(plussize)
        c4 = eqnlist[n-1]  # space
        c4.setSize(fontsize)
        c5 = eqnlist[i+4]   # BODYSTART keyword
        n5 = c5.match       # index of BODYEND
        c6 = eqnlist[n5+1]  # BODYSTART keyword
        n6 = c6.match       # Index of BODYEND keyword

        #Process limit variable and limit value
        (left, right, var_top, var_bottom) = self.layoutEquationPart(eqnlist, i+5, n5, limsize)
        var_width = right - left
        (left, right, val_top, val_bottom) = self.layoutEquationPart(eqnlist, n5+2, n6, limsize)
        value_width = right - left

        if var_top < val_top:
            top = var_top
        else:
            top = val_top

        #Position the variable, arrow, value and +/- sign relative to each other first

        #Position variable and arrow
        self.moveEquationPart(eqnlist[i+5: n5], px, py)
        arrow_x = px + var_width
        c2.setPosition(arrow_x, py)

        #Position limit value
        limit_var_x = arrow_x + c2.width
        self.moveEquationPart(eqnlist[n5+2: n6], limit_var_x, py)

        #Position +/- sign
        c3.setPosition(limit_var_x+value_width, py+val_top)

        #Now move the variable, arrow, value and sign vertically relative to 'lim'
        w1 = c1.width
        w2 = var_width + c2.width + value_width + c3.width
        w3 = var_width + c2.width + value_width

        if w2 > w1:
            c1.setPosition(px+(w3-w1)/2, py)
            self.moveEquationPart(eqnlist[i+2: n6], 0, py-top+fontsize*_LIMIT_VERT_SPACING)
            c4.setPosition(px+w2, py)
            px += (w2 + c4.width)
        else:
            c1.setPosition(px, py)
            self.moveEquationPart(eqnlist[i+2: n6], (w1-w3)/2, py-top+fontsize*_LIMIT_VERT_SPACING)
            c4.setPosition(px+w1, py)
            px += (w1 + c4.width)

        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleSubSupKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        c1 = eqnlist[i+1] # INDEXSTART keyword
        n1 = c1.match
        c2 = eqnlist[n1 + 1]  # POWERSTART keyword

        #Directly call INDEXSTART handler
        i1, px1, py1, top_of_previous_character = self.handleIndexKeyword(eqnlist, i+1, c1, px, py,  fontsize, top_of_previous_character)

        #Directly call POWERSTART handler
        i2, px2, py2, top_of_previous_character = self.handlePowerKeyword(eqnlist, n1+1, c2, px, py,  fontsize, top_of_previous_character)

        if px1 > px2:
            px = px1
        else:
            px = px2

        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleSubstitutionKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        subsize = fontsize * _FONTSCALEFACTOR

        n = c.match

        c1 = eqnlist[i+1]   # Left square bracket character
        c2 = eqnlist[i+2]   # BODYSTART keyword
        n2 = c2.match       # Index of BODYEND
        c3 = eqnlist[n2+1]  # Right square bracket
        c4 = eqnlist[n2+2]  # lhs of equal sign BODYSTART keyword
        n4 = c4.match       # lhs of equal sign index of BODYEND

        #Get size of substitution body
        body_left, body_right, body_top, body_bottom = self.layoutEquationPart(eqnlist, i+3, n2, fontsize)
        body_width = body_right - body_left
        body_height = body_bottom - body_top

        #Get size sunstitution
        left, right, top, bottom = self.layoutEquationPart(eqnlist, n2+3, n4, subsize)
        width = right - left

        #Size brackets
        extra_height = 2 * fontsize
        bracket_size = body_height + extra_height
        c1.setSize(bracket_size, fontsize)
        c3.setSize(bracket_size, fontsize)

        #Position left backet
        c1.setPosition(px, py+body_bottom+extra_height/2)
        px += c1.width

        #Position body
        self.moveEquationPart(eqnlist[i+3:n2], px, py)
        px += body_width

        #Position right backet
        c3.setPosition(px, py+body_bottom+extra_height/2)
        px += (c3.width + fontsize * _SUBSTITUTION_HORIZ_SPACING)

        shifty = py + body_bottom + extra_height/2 - top - fontsize
        self.moveEquationPart(eqnlist[n2+3:n4], px, shifty)

        px += width
        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character

    def handleFloorCeilKeyword(self, eqnlist, i, c, px, py,  fontsize, top_of_previous_character):
        #Save some data used for cursor positioning in keyword object
        c.cursorX = px
        c.cursorY = py
        c.cursorSize = fontsize

        n = c.match

        c1 = eqnlist[i+1]   # Left floor/ceil operator
        c2 = eqnlist[n-1]   # Right floor/ceil operator

        #Get size of substitution body
        body_left, body_right, body_top, body_bottom = self.layoutEquationPart(eqnlist, i+3, n-2, fontsize)
        body_width = body_right - body_left
        body_height = body_bottom - body_top
        if body_height < fontsize:
            body_height = fontsize

        #Size brackets
        extra_height = _ADDITIONAL_CEILING_HEIGHT * fontsize
        bracket_size = body_height + extra_height
        c1.setSize(bracket_size, fontsize)
        c2.setSize(bracket_size, fontsize)

        #Position left backet
        c1.setPosition(px, py+body_bottom+extra_height/2)
        px += c1.width

        #Position body
        self.moveEquationPart(eqnlist[i+3:n-2], px, py)
        px += body_width

        #Position right backet
        c2.setPosition(px, py+body_bottom+extra_height/2)
        px += c2.width

        i = n

        #Save some data used for cursor positioning in keyword object
        c3 = eqnlist[n]
        c3.cursorX = px
        c3.cursorY = py
        c3.cursorSize = fontsize

        return i, px, py, top_of_previous_character


