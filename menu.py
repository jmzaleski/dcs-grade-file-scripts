'''
Created on Jul 14, 2016

@author: mzaleski
'''
class MatzMenu(object):
    '''
    print a cheesy little menu. returns -1 if interrupt or goofy key entered.
    '''

    def __init__(self, menu_lines, prompt):
        '''
        Constructor
        '''
        self.menu_lines = menu_lines
        self.prompt = prompt
        
    # print a cheesy little menu. If there is just one element in menu_lines, then return 0
# TODO: be nice to allow user to choose first char of line too.
    def menu(self):
        if len(self.menu_lines) == 1:
            return 0
        n = 0    
        for a_matched_line in self.menu_lines :
            print("%d %s" % (n, a_matched_line))
            n += 1
        try:
            str_selection = input(self.prompt)  # this one for console.
            #str_selection = input(self.prompt)     # pycharm debugger likes this better.
            #print (">>", str_selection, "<<")
            if len(str_selection) == 0:
                return 0 #just enter selects zero'th menu item
            else:
                return int(str_selection)
        except KeyboardInterrupt:
            #here if user types control-C (or whatever terminal key interrupts)
            return -1
        except:
            print("interrupt.. prob invalid selection:", str_selection)
            return -1
    
