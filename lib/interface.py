############################################################################################################
#
#   This taylors the interface to our usecase here a bit.
#       ~ Alex de Mulder
#
############################################################################################################

from basicGUI import *

class interface(basicGUI):
    
    def initGUI(self):
        basicGUI.initGUI(self,600)
        self.player_id = "interface"
    
    def loadSystemImages(self):
        pass
    
    def run(self):
        self.running = True

        #initialization
        self.menu_selection = ""
        self.category_field = ""
        self.selected_category = ''
        self.selected_species = ''
        self.font_size = 3

        # scrollbar
        self.last_scroll_time = 0
        self.max_scroll_distance = 0

        showScreenSpace_on = False
        #for refreshrate
        t_start = time.time() #@UnusedVariable

        pygame.event.set_blocked(MOUSEMOTION)
        self.resetFields()
        start_time = time.time() #@UnusedVariable

        self.system_images_loaded = True

        while self.running:
            t0 = time.time() #@UnusedVariable
            self.screenspace = {}
            self.collision_objects = []
            if self.running:
                if not self.system_images_loaded:
                    # this is for threaded loading functionality
                    self.checkEvents()
                else:
                    self.createGUIElements();

                    self.checkPressedKeys()
                    pygame.time.wait(100) #saves cpu time

                    if self.showScreenSpace_on:
                        self.showScreenSpace()
                    if self.alignmentTools_on:
                        self.showAlignmentTools()
                    #=========================== REFRESH RATE ====================================
                    # frametime = time.time() - t0
                    # self.writetext(self.refreshrate_deck(frametime) + " Hz",3,self.x - 70,3,False,False,color=(255,0,0))
                    #=============================================================================

                    pygame.display.flip()#refresh the screen

                    #this checks the events of the program
                    self.checkEvents()

        pygame.quit()

    def createGUIElements(self):
        pass
    
if __name__ == '__main__':
    a = interface()
    a.initGUI()
    a.run()
