"""
@Name: gvrhtmlparser
@Description: An html parser built specifically for GVR reports.
@Creator: Jesse Thomas
"""
from html.parser import HTMLParser

class HtmlParser(HTMLParser):
    """
    @Name: HtmlParser
    @Description: An inherited class that uses specific core functionality
            from the CORE module HTMLParser.
    @inherits: HTMLParser
    """

    def __init__(self, file_name):
        """
        @Name: __init__
        @Description: The constructor to the HtmlParser class.
        @params:
            >file_name: (String) The absolute path to the html file to be
                    parsed.
        @Creator: Jesse Thomas
        """
        HTMLParser.__init__(self)
        self.table_data = None
        self.data_list = []
        self.short_list = []
        html_count = 0
        self.start_tag = 0
        self.th = 0
        self.hr = 0
        file_handle = open(file_name, 'r')
        self.feed(file_handle.read())
        file_handle.close()
        self.data_list = tuple(self.data_list)


    def handle_starttag(self, tag, attrs):
        """
        @Name: handle_starttag
        @Description: An overidden method from HTMLParser to read and handle
                specific start tags. In this case, TR (table row)
                !!!WARNING!!! This function was not meant to be used outside
                of this module. When __init__ calls feed() this function
                overrides the original which did nothing.
        @params:
            >tag: (String) The start tag to be parsed.
            >attrs: (String) The attributes within the tag.
        @return:
            >tag: (String) The start tag that was parsed.
        @Creator: Jesse Thomas
        """
        if tag == 'hr':
            self.hr += 1
            if self.table_data is not None:
                self.short_list.append(self.table_data)
                self.table_data = None
        if tag == 'tr':
            self.start_tag += 1
            if self.th > 0:
                if len(self.short_list) >= 1:
                    if self.table_data is not None:
                        self.short_list.append(self.table_data)
                        self.table_data = None
                    self.data_list.append(tuple(self.short_list))
                    del self.short_list[:]
                    self.th = 0
        if tag == 'th':
            self.th += 1
            if self.hr > 0:
                if len(self.short_list) >= 1:
                    self.data_list.append(tuple(self.short_list))
                    del self.short_list[:]
                    self.hr = 0
            if self.table_data is not None:
                self.short_list.append(self.table_data)
                self.table_data = None
        return tag

    #Wrote the same thing here that I did for start tag. Read the warning, above, that's why this is empty now. A lot of pain.
    def handle_endtag(self, tag):
        """
        @Name: handle_endtag
        @Description: An overridden method from HTMLParser to read and handle
                specific end tags. In this case TR (table row) and TD (table
                data).
                !!! WARNING!!! This function was not meant to be used outside
                of this module. When __init__ calls feed() this function
                overrides the original which did nothing.
        @params:
            >tag: (String) The end tag to be parsed.
        @return:
            >tag: (String) The end tag that was parsed.
        @Creator: Jesse Thomas
        """
        if tag == 'td' and self.start_tag <= 2:
            if self.table_data is not None:
                self.short_list.append(self.table_data)
                self.table_data = None
        if tag == 'tr':
            self.start_tag -= 1
            if len(self.short_list) >= 1 and self.start_tag <= 1:
                #WARNING Before you try and turn this tuple into a list. Please uncomment the print statement below the del statement so you can see why I turned
                #the list into a tuple. It was the only thing I knew to do O_O ~Jesse Thomas
                self.data_list.append(tuple(self.short_list))
                del self.short_list[:]
##                print self.data_list
        return tag

    def handle_data(self, data):
        """
        @Name: handle_data
        @Description: An overridden method from HTMLParser to read and handle
                specific data between specific start and end tags. In this case,
                b (bold) and font.
                !!!WARNING!!! This function was not meant to be used outside
                of this module. When __init__ calls feed() this function
                overrides the original which did nothing.
        @params:
            >data: (String) The data to be parsed.
        @Creator: Jesse Thomas
        """
        #This will remove any leading and trailing whitespace, as well as the escape char '\n'
        if self.lasttag == 'b' or self.lasttag == 'font' or self.lasttag == 'td' or self.lasttag == 'hr' or \
            self.lasttag == 'th':
            data = data.replace('\n', '').strip()
            if str(data) is not '':
                if self.table_data is None:
                    self.table_data = data
                else:
                    self.table_data = "%s %s" %(self.table_data, data)

# if __name__ == "__main__":
    # parser = HtmlParser(r'C:\EPSFiles\HC\HealthCheck_20190822.html')
    # for ele in parser.data_list:
    #     print ele
    #     if 'Debit' in ele:
    #         print ele
