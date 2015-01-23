############################################################################################################
#
#   This is a very old interface I made when I just started out in python. It has been rewritten
#   for my thesis and edited for the kinect Pong game I did during my internship
#
#   It allows easy usage of images, text, shapes and callbacks.
#       ~ Alex de Mulder
#
############################################################################################################


import pygame, time, math, random, os
from pygame.locals import *
TEXT_DEFAULT_COLOR = (200,200,200)

function_notifications = []
tictac_time = 0

def tic():
    global tictac_time
    tictac_time = time.time()

def tac(comment = "tictac time"):
    global tictac_time
    time_passed = time.time() - tictac_time
    print comment, " took: ", time_passed, "seconds."
    tictac_time = 0

def getBox(x,y,(r,g,b,a),color_factor = 1,alpha_override = -1):
    box = pygame.Surface((x,y),pygame.SRCALPHA, 32)
    if alpha_override == -1:
        box.set_alpha(a*color_factor)
    else:
        box.set_alpha(alpha_override)

    box.fill((r*color_factor,g*color_factor,b*color_factor))
    return box

def getTransparentBox(x,y):
    box = pygame.Surface((x,y),pygame.SRCALPHA, 32)
    box = box.convert_alpha()
    return box

def getBorderedBox(x,y,(r,g,b,a),(border_r,border_g,border_b,border_a),width,color_factor = 1):
    box = pygame.Surface((x,y))
    box.set_alpha(a*color_factor)
    box.fill((r*color_factor,g*color_factor,b*color_factor))

    border = pygame.Surface((x+2*width,y+2*width))
    border.set_alpha(border_a)
    border.fill((border_r,border_g,border_b))

    border_surface = pygame.Surface((x+2*width,y+2*width),pygame.SRCALPHA, 32)
    border_surface = border_surface.convert_alpha()

    border_surface.blit(border,(0,0))
    border_surface.blit(box,(width,width))
    return border_surface

def siground(float_value, decimals, plain=False): #round to significant numbers
    formating_string = '%.'+str(decimals)+'g'
    if plain:
        return '%s' % float(formating_string % getFloat(float_value))
    else:
        return '%s' % (formating_string % getFloat(float_value))

def getFloat(value):
    value_string = str(value)
    value_final = ""
    if 'e' in value_string.lower():
        value_array = value_string.lower().split('e')
        try:
            value_final = float(value_array[0])*math.pow(10,int(value_array[1]))
        except ValueError:
            value_final = 0
            if value_string != "":
                function_notifications.append("Illegal number detected!")
    else:
        try:
            value_final = float(value_string)
        except ValueError:
            value_final = 0
            if value_string != "":
                function_notifications.append("Illegal number detected!")
    return value_final



class basicGUI(object):
    
    def initGUI(self,x=800,y=600,fullscreen=False):      
        self.x = x
        self.y = y
                  
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        self.font = []
        self.frametimes_deck = []
        self.notification_center = []
        self.notification_time_start = 0
        
        self.system_images = {}
        
        self.system_images_loaded = False         
        self.showScreenSpace_on = False
        self.showCollisionSpace_on = False
        self.alignmentTools_on = False
        self.mouse_pressed_xy = [0,0]
        
        if not fullscreen:
            self.screen = pygame.display.set_mode((self.x,self.y))
        else:
            self.screen = pygame.display.set_mode((self.x,self.y),pygame.FULLSCREEN)
        
        self.loadSystemImages()
        
        pygame.display.set_caption('OTA Select tool')
#         icon = pygame.image.load('system_resources\\icon.png')
#         pygame.display.set_icon(icon) #load icon
        
        self.selected_item_id = ''
        self.selected_table = "none"
        self.time_clicked = 0
        
        self.shift_on,self.control_on,self.alt_on = False,False,False
        
        fontname = "system_resources/fonts/verdana.ttf"
        self.font.append(pygame.font.SysFont(fontname,9)) #0
        self.font.append(pygame.font.SysFont(fontname,12))#1
        self.font.append(pygame.font.SysFont(fontname,14))#2
        self.font.append(pygame.font.SysFont(fontname,16))#3
        self.font.append(pygame.font.SysFont(fontname,18))#4
        self.font.append(pygame.font.SysFont(fontname,20))#5
        self.font.append(pygame.font.SysFont(fontname,22))#6
        self.font.append(pygame.font.SysFont(fontname,25))#7
        self.font.append(pygame.font.SysFont(fontname,35))#8
        self.font.append(pygame.font.SysFont(fontname,75))#9
        
        #initialization
        self.interface = ""
        self.menu_selection = ""
        self.font_size = 3
        
        # scrollbar
        self.last_scroll_time = 0
        self.max_scroll_distance = 0
        
        #key presses
        self.pressed_threshold = 0.4
        self.repeat_threshold = 0.1
        
        self.resetFields()
        
    def splitToLines(self,string,max_length,max_lines):
        new_string = ''
        string = str(string)
        lines = []
        if len(string) >= max_length:
            word_array = string.split(' ')
            for index,word in enumerate(word_array):
                if word == '\n':
                    lines.append(new_string.strip()) 
                    new_string = ''
                else:
                    new_string = new_string + " " + word
                    if len(lines) < max_lines:
                        if index+1 < len(word_array):
                            if (len(new_string)+1+len(word_array[index+1])) >= max_length:
                                lines.append(new_string.strip())
                                new_string = ''
                        else:
                            lines.append(new_string.strip()) 
                    else:
                        lines[max_lines-1] = lines[max_lines-1] + "..."
                        break
        else:
            lines.append(string)
      
        return lines 
     
    def writetext(self,input_text,size,xpos,ypos,centerx=False,centery=True,color=TEXT_DEFAULT_COLOR,max_length=1000, max_lines=2, blitTo=""):
        lines = self.splitToLines(input_text,max_length,max_lines)
        line_height = (9,12,14,16,18,20,22,25,35,75,9,12,14,16,18,20,22,25,35,75)
        for text in lines:
            text = self.font[size].render(text,1,color)
            if centerx and centery:
                text_pos = text.get_rect(centerx=xpos,centery=ypos)
            elif centerx:
                text_pos = text.get_rect(centerx=xpos,y=ypos)
            elif centery:
                text_pos = text.get_rect(x=xpos,centery=ypos)
            else:
                text_pos = text.get_rect(x=xpos,y=ypos)
            if blitTo == "":
                self.screen.blit(text,text_pos)
            else:
                blitTo.blit(text,text_pos)
            ypos = ypos+(line_height[size]+4)
        return len(lines) + 1

    def loadSystemImages(self):
        pass
    
    def showImage(self,title,(xpos,ypos),click_id="",click_border=2,custom_screenspace=((0,0),(0,0)),clearScreenspaceBehind=False,blitTo="",blitToPos=[0,0]):
        if blitTo != "":
            blitTo.blit(self.system_images[title],(xpos,ypos))
        else:
            self.screen.blit(self.system_images[title],(xpos,ypos))
            
        if clearScreenspaceBehind:
            (width,height) = self.system_images[title].get_size()
            self.clearScreenspaceInArea(xpos,ypos,width,height)
            
        if click_id != "" and custom_screenspace == ((0,0),(0,0)):
            (width,height) = self.system_images[title].get_size() 
            blitX = blitToPos[0]
            blitY = blitToPos[1]
            
            if blitTo != "":
                self.screenspace[click_id] = ((blitX+xpos-click_border,blitY+ypos-click_border),(blitX+xpos+width+click_border,blitY+ypos+height+click_border))
            else:
                self.screenspace[click_id] = ((xpos-click_border,ypos-click_border),(xpos+width+click_border,ypos+height+click_border))
        elif click_id != "":
            self.screenspace[click_id] = custom_screenspace
    
    def clearScreenspaceInArea(self,xpos,ypos,width,height):
        new_screenspace = {} 
        for screenspace_title,space in self.screenspace.iteritems():
            if (xpos <= space[0][0] <= xpos+width or \
                xpos <= space[1][0] <= xpos+width) and \
                 (ypos <= space[0][1] <= ypos+height or \
                 ypos <= space[1][1] <= ypos+height):
                pass
            else:
                new_screenspace[screenspace_title] = space
        self.screenspace = new_screenspace
        
    def resetFields(self):
    #===The variables are defined at GUI level because they will not be saved if they are reinitiated each frame    
        
    # misc
        self.active_field = ""
        self.pressed_keys = []
        
        #settings for gestures
        self.direction = 1
        self.mouse_pressed = 0
        
        #settings for the scrollbar:
        self.grabScrollControl = False
        self.grabScrollControl_index = 0
        self.grabScrollControl_direction = 'v'
        self.previous_selected_control = ''
        self.previous_scroll_point = (0,0)
        self.y_scroll_0 = 0
        self.y_scroll_1 = 0
        self.y_scroll_2 = 0
        self.y_scroll_3 = 0
        self.y_scroll_4 = 0
        
        self.x_scroll_0 = 0
        self.x_scroll_1 = 0
        self.x_scroll_2 = 0
        self.x_scroll_3 = 0
        self.x_scroll_4 = 0
        
        #settings for the blinker
        self.text_blinker_x = 0
        self.text_blinker_size = 0
        self.time_last_blink = -1
        self.blinker_subindex = 1000
        self.subindex_active_field = ""
        self.blinker_text_fontsize = 0
        self.blink_on_time = 0.4
        self.blink_off_time = 0.3
        
        #settings for holding buttons
        self.backspace_pressed = False
        self.delete_pressed = False
        self.left_arrow_pressed = False
        self.right_arrow_pressed = False
        self.pressed_timer = 0
        self.pressed_repeat_speed = 0.1
        
        #confirm delete
        self.confirm_delete_id = -1
        self.confirm_delete = False
        self.clicked_delete_button = False
        
    def refreshrate_deck(self,frametime): #calculate refreshrate
        if len(self.frametimes_deck) < 20:
            self.frametimes_deck.append(frametime)
        else:
            self.frametimes_deck.pop(0)
            self.frametimes_deck.append(frametime)
        average_frametime = sum(self.frametimes_deck)/len(self.frametimes_deck)
        return str(round(1/(average_frametime+1e-4),1))
        
    def showScreenSpace(self):
        for key,space in self.screenspace.iteritems(): #@UnusedVariable
            pygame.draw.rect(self.screen,(int(random.random()*255),int(random.random()*255),int(random.random()*255)),pygame.Rect(space[0][0],space[0][1],space[1][0]-space[0][0],space[1][1]-space[0][1]))
            self.writetext(key, 0, space[0][0], space[0][1], False, False, (random.random()*255,255,random.random()*255), max_length=40, max_lines=1)
    
    def showAlignmentTools(self):
        horizontal_line = getBox(2000,1,(0,255,0,150))
        vertical_line = getBox(1,2000,(255,0,0,150))
        self.screen.blit(horizontal_line,(0,self.mouse_pressed_xy[1]))
        self.screen.blit(horizontal_line,(0,self.mouse_pressed_xy[1]-5))
        self.screen.blit(horizontal_line,(0,self.mouse_pressed_xy[1]+5))
        self.screen.blit(vertical_line,(self.mouse_pressed_xy[0],0))
        self.screen.blit(vertical_line,(self.mouse_pressed_xy[0]+5,0))
        self.screen.blit(vertical_line,(self.mouse_pressed_xy[0]-5,0))
                          
    def blinker(self,blinker_x,blinker_y,font_size,blinker_size=2,x_offset=4,y_offset=2):  
        if font_size < 2:
            x_offset = 1
        
        text_size = 0
        if self.active_field != "":
            exec("text_size = self.font[font_size].size(self."+self.active_field+")[0]")
        self.blinker_text_fontsize = font_size
        self.text_blinker_size = text_size
        self.text_blinker_x = blinker_x+x_offset
        
        if self.subindex_active_field != self.active_field:
            self.getBlinkerSubindex()
        
        if self.blinker_subindex != -1:
            if self.active_field != "":
                exec("text_size = self.font[font_size].size(self."+self.active_field+"[:" + str(self.blinker_subindex) + "])[0]")
        else:
            if self.active_field != "":
                length_field = 0
                exec("length_field = len(self."+self.active_field+")")
                self.blinker_subindex = length_field
        
        if (time.time() - self.time_last_blink) > self.blink_on_time or (time.time() - self.time_last_blink) < self.blink_off_time:
            if self.active_field != "":
                self.writetext('|', blinker_size, blinker_x+text_size-x_offset, blinker_y-y_offset, False, True, color=(20,20,20))
                if (time.time() - self.time_last_blink) > self.blink_on_time:
                    self.time_last_blink = time.time()
                    
    def getBlinkerSubindex(self):
        total = self.text_blinker_size
        selected = self.mouse_pressed - self.text_blinker_x
        self.subindex_active_field = self.active_field
        if total != 0:
            length_field = 0
            exec("length_field = len(self."+self.active_field+")")

            if self.mouse_pressed == 0:
                selected = self.x
            
            guessed_index = 0
            if selected >= total:
                guessed_index = length_field
            
            approx_size = 0
            for i in range(length_field):
                exec("approx_size = self.font[self.blinker_text_fontsize].size(self."+self.active_field+"[:"+str(i)+"])[0]")
                if selected <= approx_size:
                    guessed_index = i
                    break
            if approx_size < selected:
                guessed_index = length_field
                
            if guessed_index > length_field:
                self.blinker_subindex = length_field
            elif guessed_index < 0:
                self.blinker_subindex = 0
            else:
                self.blinker_subindex = guessed_index
            
        else:
            self.blinker_subindex = 0
           
    def initiateScrollbar(self,max_scroll_distance,xpos=-1,ypos=180,max_travel_distance=-1,horizontal=False,index=0):
        # set default values
        if xpos == -1 and not horizontal:
            xpos = self.xpos - 100
        elif xpos == -1:
            xpos = 100
            
        max_scroll_distance = int(max_scroll_distance)
        
        # set default values
        if max_travel_distance == -1 and not horizontal:
            max_pos = self.y - 100
            max_travel_distance = max_pos - ypos
        elif max_travel_distance == -1:
            max_pos = self.x - 100
            max_travel_distance = max_pos - xpos
        elif horizontal:
            max_pos = xpos + max_travel_distance
        else:
            max_pos = ypos + max_travel_distance
        
        # get direction
        if horizontal:
            direction = 'x'
        else:
            direction = 'y'
            
        # get distance 
        scrolled_distance = 0
        exec("scrolled_distance = self." + direction + "_scroll_" + str(index))
        
        scroll_offset = 0
        # move if grabbed, else get pos from distance
        if self.grabScrollControl and self.grabScrollControl_index == index and self.grabScrollControl_direction == direction:
            if horizontal:
                scroll_control_position = max(xpos,min(pygame.mouse.get_pos()[0],max_pos))
                scroll_offset = -max_scroll_distance * (scroll_control_position-xpos)/float(max_travel_distance)
            else:
                scroll_control_position = max(ypos,min(pygame.mouse.get_pos()[1],max_pos))
                scroll_offset = -max_scroll_distance * (scroll_control_position-ypos)/float(max_travel_distance)
            
            if  scroll_offset < -max_scroll_distance:
                scroll_offset = -max_scroll_distance
            
            exec("self." + direction + "_scroll_" + str(index) + " = scroll_offset")
        else:
            if horizontal:
                scroll_control_position = (scrolled_distance/(-max_scroll_distance))*(max_travel_distance) + xpos
            else:
                scroll_control_position = (scrolled_distance/(-max_scroll_distance))*(max_travel_distance) + ypos
        
        # draw scroll bar control
        if horizontal:
            self.screen.blit(self.system_images['horizontal_scrollbar_control'],(scroll_control_position,ypos))
            self.screenspace['scrollbar_control__' + str(index) + "__x__" + str(max_scroll_distance) + "__" + str(random.randint(0,9000))] = ((scroll_control_position-20,ypos-10),(scroll_control_position+60,ypos+20))
        else:
            self.screen.blit(self.system_images['scrollbar_control'],(xpos,scroll_control_position))
            self.screenspace['scrollbar_control__' + str(index) + "__y__" + str(max_scroll_distance) + "__" + str(random.randint(0,9000))] = ((xpos-10,scroll_control_position-20),(xpos+50,scroll_control_position+60))
              
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
                    if not self.menu_selection:
                        self.interface = ""
                        self.screen.fill((255,255,255))

                        self.writetext("No Errors.",3,self.x/2, self.y/2, True, True)
                    self.checkPressedKeys()

                    pygame.time.wait(50) #saves cpu time



                    if self.showScreenSpace_on:
                        self.showScreenSpace()
                    if self.alignmentTools_on:
                        self.showAlignmentTools()


                    #=========================== REFRESH RATE ====================================
                    frametime = time.time() - t0
                    self.writetext(self.refreshrate_deck(frametime) + " Hz",3,self.x - 70,3,False,False,color=(255,0,0))
                    #=============================================================================

                    pygame.display.flip()#refresh the screen

                    #this checks the events of the program
                    self.checkEvents()
                    
        pygame.quit()

    def scrollNearestScrollbar(self,direction,xpos,ypos):
        #scroll settings
        scroll_speed = 30
        scroll_acceleration = 20
        
        #variable initialization
        min_distance = 10000
        scroll_index = -1
        scroll_direction = 'v'
        selected_key = ""
        #finding nearest scrollbar
        for key,obj in self.screenspace.iteritems():
            if 'scrollbar_control__' in key:
                key_list = key.split("__")
                distance = math.sqrt(math.pow(xpos-obj[0][0],2) + math.pow(ypos-obj[0][1],2))
                if min_distance > distance:
                    min_distance = distance
                    scroll_direction = key_list[2]
                    scroll_index = int(key_list[1])
                    scroll_limit = int(getFloat(key_list[3]))
                    selected_key = key
        if selected_key != "":
            #once a scrollbar is selected, it will remain to be selected until the mouse moves out of the threshold area         
            threshold = 10 #area to move before the selected control is resetted
            if selected_key != self.previous_selected_control:
                if abs(self.previous_scroll_point[0]-xpos) < threshold and abs(self.previous_scroll_point[1]-ypos) < threshold:
                    #ignore changes.
                    key_list = self.previous_selected_control.split("__")
                    scroll_direction = key_list[2]
                    scroll_index = int(key_list[1])
                    scroll_limit = int(key_list[3])
                    selected_key = self.previous_selected_control
                    
            #get the current scroll offset
            scroll_offset = 0
            exec("scroll_offset = self." + scroll_direction + "_scroll_" + str(scroll_index))
            
            # apply the scrolling step, bounded by limits
            if direction == 'up':
                scroll_offset += (scroll_speed + (0.5/(time.time() - self.last_scroll_time + 0.01))*scroll_acceleration)
                if scroll_offset > 0:
                    scroll_offset = 0
            else:
                scroll_offset -= (scroll_speed + (0.5/(time.time() - self.last_scroll_time + 0.01))*scroll_acceleration)
                if scroll_offset < -scroll_limit:
                    scroll_offset = -scroll_limit 
            
            # push the new scroll offset to the gui level variable
            exec("self." + scroll_direction + "_scroll_" + str(scroll_index) + " = scroll_offset")
            
            # store which scrollbar was selected
            self.previous_selected_control = selected_key
            self.previous_scroll_point = (xpos,ypos)
            
            # reset the time for the acceleration
            self.last_scroll_time = time.time()
         
    def saveScreenshot(self):
        import datetime
        a = datetime.datetime.now()
        timestamp = str(a.replace(microsecond=0)).replace(":",".")
        if self.menu_selection == "":
            menu_selected = "main"
        else:
            menu_selected = self.menu_selection
        pygame.image.save(self.screen,"screenshots/" + menu_selected + " at " + timestamp + ".png")
        self.notification_center.append("screenshot saved!")    

    def printChar(self,character):
        if self.active_field != "":
            exec("self."+self.active_field+" = self."+self.active_field+"[:"+str(self.blinker_subindex)+"] + '"+character+"' + self."+self.active_field+"["+str(self.blinker_subindex)+":]")
            self.blinker_subindex += 1
    
    def removeChar(self,forward):
        if forward:
            exec("self."+self.active_field+" = self."+self.active_field+"[:"+str(self.blinker_subindex)+"] + self."+self.active_field+"["+str(self.blinker_subindex+1)+":]")
        else:
            if self.blinker_subindex != 0:
                exec("self."+self.active_field+" = self."+self.active_field+"[:"+str(self.blinker_subindex-1)+"] + self."+self.active_field+"["+str(self.blinker_subindex)+":]")
                self.blinker_subindex -= 1
                if self.blinker_subindex < 0:
                    self.blinker_subindex = 0
    
    def mouseClicked(self,x,y):
        pass
    
    def checkPressedKeys(self):
        for key,pressed_time,action_time in self.pressed_keys:
            if time.time() - pressed_time > self.pressed_threshold:
                if time.time() - action_time > self.repeat_threshold:
                    action_time = time.time()
                    self.handleKeyDown(key)
                
    def checkEvents(self): #all the keystrokes and clicks are handled here
        for event in pygame.event.get():
            if event.type == QUIT: #quit
                self.running = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.shift_on:
                        print (event.pos[0],event.pos[1])
                    self.mouse_pressed = event.pos[0]
                    self.mouse_pressed_xy = [event.pos[0],event.pos[1]]
                    self.handleClickEvent(event.pos[0],event.pos[1])
                    if self.active_field != "":
                        self.subindex_active_field = ""
                        
                    self.mouseClicked(event.pos[0],event.pos[1])
                elif event.button == 3:
                    if self.selected_item_id:
                        self.handleEvent('back')
                elif event.button == 4:
                    self.scrollNearestScrollbar('up',event.pos[0],event.pos[1])
                elif event.button == 5:
                    self.scrollNearestScrollbar('down',event.pos[0],event.pos[1])
                self.mouse_pos = (event.pos[0],event.pos[1])
                
            elif event.type == KEYDOWN: #keys pressed
                self.pressed_keys.append([event.key, time.time(), time.time()])
                self.handleKeyDown(event.key)
                
            elif event.type == KEYUP:           #keys pressed
                for i,key in enumerate(self.pressed_keys):
                    if key[0] == event.key:
                        self.pressed_keys.pop(i)
                        break
                
                if event.key == 304 or event.key == 303: #shift
                    self.shift_on = False
                    self.handleEvent("released_shift")
                elif event.key == 306:          #control
                    self.control_on = False
                elif event.key == 308:          #alt
                    self.alt_on = False 
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.grabScrollControl = False
                    if self.mouse_pressed != 0:
                        if abs(event.pos[0] - self.mouse_pressed) > 4: #threshold for drag
                            if event.pos[0] < self.mouse_pressed:
                                self.direction = -1
                            else:
                                self.direction = 1
                            self.mouse_pressed = 0
                        else:
                            self.mouse_pressed = 0
                                       
    def rightArrowKeyPressed(self):
        pass
    
    def leftArrowKeyPressed(self):
        pass
    
    def upArrowKeyPressed(self):
        pass
    
    def downArrowKeyPressed(self):
        pass
    
    def handleKeyDown(self,key):
        if key == 27: #escape
            if self.menu_selection != "":
                self.interface.back()
            else:
                self.handleEvent("quit")
        elif key == 308: #alt
            self.alt_on = True 
        elif key == 306: #left control
            self.control_on = True
        elif key == 305: #right control
            self.control_on = True
        elif key == 304 or key == 303: #shift
            self.shift_on = True
        elif key == 285: #F4
            if self.alt_on:
                self.running = False
                
                
                
        elif key == 276: #left arrow
            if self.active_field != "":
                self.blinker_subindex -= 1
                if self.blinker_subindex < 0:
                    self.blinker_subindex = 0
                    
            self.leftArrowKeyPressed()
        elif key == 275: #right arrow
            if self.active_field != "":
                self.blinker_subindex += 1
            self.rightArrowKeyPressed()
        elif key == 273: #up arrow
            self.upArrowKeyPressed()
        elif key == 274: #down arrow
            self.downArrowKeyPressed()
         
            
            
        elif key == 278: #home
            self.blinker_subindex = 0
        elif key == 279: #end
            self.mouse_pressed = 1900
            self.getBlinkerSubindex()
        elif self.shift_on and (48 <= key <= 57): #numbers
            symbols_array = ['!','@','#','$','%','^','&','*','(',')']
            character = symbols_array[key - 49]
            self.printChar(character)
        elif 48 <= key <= 57:     #numbers
            character = str(key - 48)
            self.printChar(character)
        elif 256 <= key <= 265:   #keypad
            character = str(key - 256)
            self.printChar(character)
        elif self.shift_on and key == 45:         #underscore
            character = chr(95)
            self.printChar(character)
        elif key == 45 or key == 269:       #min
            character = '-'
            self.printChar(character)
        elif key == 266:                          #keypad-dot
            character = '.'
            self.printChar(character)
        elif key == 8:            #backspace
            if self.active_field != "":
                self.backspace_pressed = True
                self.removeChar(forward=False)
                self.pressed_timer = time.time()
        elif key == 127: #delete
            if self.active_field != "":
                self.delete_pressed = True
                self.removeChar(forward=True)
                self.pressed_timer = time.time()
        elif (self.shift_on and key == 61) or key == 270:
            character = str("+")
            self.printChar(character)
        elif (32 <= key <= 122) and (key != 47) and (key != 92) and (key != 41) and (key != 58) and (key != 63) or (key == 62) and (key != 60) and (key != 34): #caps, letters, space'
            if self.control_on and key == 115: #cntrl S --> screenspace
                if self.showScreenSpace_on:
                    self.showScreenSpace_on = False
                else:
                    self.showScreenSpace_on = True
            if self.control_on and key == 97: #cntrl a --> alignmentTools_on
                if self.alignmentTools_on:
                    self.alignmentTools_on = False
                else:
                    self.alignmentTools_on = True
            elif self.control_on and key == 103:
                self.saveScreenshot()
            elif self.active_field != "":
                if self.control_on and key == 118: #cntrl v --> paste
                    pass
                    # r = Tkinter.Tk()
                    # r.withdraw()
                    # character = r.clipboard_get()
                    # self.printChar(character)
                    # r.destroy()
                elif self.shift_on and (97 <= key <= 122): #caps
                    character = chr(key - 32)
                    self.printChar(character)
                else:
                    character = chr(key)
                    self.printChar(character)
        elif key == 9:            #tab
            if self.menu_selection != "":
                self.interface.selectNextField()  
        elif key == 13 or key == 271: #enter or keypad enter
            if self.menu_selection != "":
                self.interface.pressedReturn()
    
    def handleClickEvent(self,click_x,click_y): #finds in which screenspace you clicked
        hits = []
        self.clicked_delete_button = False
        for key,obj in self.screenspace.iteritems():
            if obj[0][0] <= click_x <= obj[1][0] and obj[0][1] <= click_y <= obj[1][1]:
                hits.append(key)
        if hits:
            self.handleEvent(hits[0]) 
        
        if not self.clicked_delete_button:
            self.confirm_delete = False           
        
    def handleEvent(self,key): #this handles all the click events...
        global db         
        key_list = key.split("__")
        if 'quit' in key:
            self.running = False
        elif 'MAIN_MENU_ITEM__' in key:
            self.databaseCleanup()
            self.resetFields()
            self.menu_selection = key_list[1]
            self.y_scroll = 0
            self.new_menu_selection = True
        else:
            if self.interface != "":
                self.interface.handleEvents(key) 

    def selectNextField(self):
        pass
    
    
if __name__ == '__main__':
    a = basicGUI()
    a.initGUI()
    a.run()
