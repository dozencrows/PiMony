'''
Created on 25 May 2014

@author: ntuckett
'''

import pygame
import pygame.font
import os
import time
import imp
import sys, signal
import IR

from TouchScreenButton import TouchScreenButton
import Style

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    def __getattr__(self, attr):
        return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

SCREEN_WIDTH    = 240
SCREEN_HEIGHT   = 320
BUTTON_MARGIN   = 1
BUTTON_COLUMNS  = 2
BUTTON_ROWS     = 6

BUTTON_X_OFFSET         = BUTTON_MARGIN
BUTTON_Y_OFFSET         = BUTTON_MARGIN
BUTTON_COLUMN_WIDTH     = (SCREEN_WIDTH / BUTTON_COLUMNS)
BUTTON_ROW_HEIGHT       = (SCREEN_HEIGHT / BUTTON_ROWS)

BOUNCE_LIMIT    = 3 

test_button_layout = [
    dotdict({ 'x':0, 'y':0, 'width':2, 'height':1, 'text':"Power", 'code':"RM-ED050-12 KEY_POWER;Phillips-HTS KEY_POWER" }),
    dotdict({ 'x':0, 'y':1, 'width':1, 'height':1, 'text':"Vol +", 'code':"Phillips-HTS KEY_VOLUMEUP" }),
    dotdict({ 'x':0, 'y':2, 'width':1, 'height':1, 'text':"Vol -", 'code':"Phillips-HTS KEY_VOLUMEDOWN" }),
    dotdict({ 'x':1, 'y':1, 'width':1, 'height':1, 'text':"Chan +", 'code':"RM-ED050-12 KEY_CHANNELUP" }),
    dotdict({ 'x':1, 'y':2, 'width':1, 'height':1, 'text':"Chan -", 'code':"RM-ED050-12 KEY_CHANNELDOWN" })
]

def signal_handler(signal, frame):
    print 'Signal: {}'.format(signal)
    quit_event = pygame.event.Event(pygame.QUIT)
    pygame.event.post(quit_event)

class PyGameInterface(object):
    def __init__(self):
        pygame.font.init()
        #self.font = pygame.font.Font("LiberationSansNarrow-Bold.ttf", 14)
        #self.font_large = pygame.font.Font("LiberationSansNarrow-Bold.ttf", 16)
        self.font = pygame.font.Font("Impact.ttf", 16)
        self.font_large = pygame.font.Font("Impact.ttf", 18)

    def use_window(self):
        os.environ['SDL_VIDEODRIVER'] = 'x11'
        pygame.display.init()
        self.screen = pygame.display.set_mode((240,320))

    def use_framebuffer(self):
        os.environ['SDL_VIDEODRIVER'] = 'fbcon'
        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        
        pygame.display.init()
        self.screen = pygame.display.set_mode((240,320), pygame.FULLSCREEN, 16)
        pygame.mouse.set_visible(False)
    
    def layout_buttons(self, layout):
        self.buttons = []
        for button_def in layout:
            x = button_def.x * BUTTON_COLUMN_WIDTH + BUTTON_X_OFFSET
            y = button_def.y * BUTTON_ROW_HEIGHT + BUTTON_Y_OFFSET
            w = BUTTON_COLUMN_WIDTH * button_def.width - (2 * BUTTON_MARGIN)
            h = BUTTON_ROW_HEIGHT * button_def.height - (2 * BUTTON_MARGIN)
            if button_def.width > 1 or button_def.height > 1:
                style = self.button_style_large
            else:
                style = self.button_style
                
            self.buttons.append(TouchScreenButton(x, y, w, h, button_def.text, button_def.code, style))
    
    def render_current_button(self):
        self.display_dirty = True
        self.dirty_rect.union_ip(self.current_button)
        self.current_button.render(self.screen)
        
    def run(self):
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        
        IR.init()
        
        running = True
        
        self.button_style = { Style.FONT: self.font, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                              Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255),   Style.HIGHLIGHT_COLOUR: (0, 255, 0) }
        self.button_style_large = { Style.FONT: self.font_large, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                                    Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255), Style.HIGHLIGHT_COLOUR: (0, 255, 0) }

        self.layout_buttons(test_button_layout)
        
        self.screen.fill((0, 0, 0))
        for button in self.buttons:
            button.render(self.screen)
        pygame.display.flip()
        
        self.display_dirty = False
        self.current_button = None
        self.loop_count = 0
        self.dirty_rect = pygame.Rect(0, 0, 0, 0)

        while running:
            self.loop_count += 1
            if self.display_dirty:
                pygame.display.update(self.dirty_rect)
                self.display_dirty = False
                self.dirty_rect.inflate_ip(-self.dirty_rect.w, -self.dirty_rect.h)

            # Can't use pygame.event.wait() as this blocks signals
            time.sleep(0.008)
            event = pygame.event.poll()
            
            while event.type != pygame.NOEVENT:
                if event.type == pygame.MOUSEBUTTONDOWN and self.current_button == None:
                    #print self.loop_count,":",event
                    for button in self.buttons:
                        if button.hit_test(event.pos):
                            self.current_button = button
                            button.highlight(True)
                            self.render_current_button()
                            self.send_ir(self.current_button.code)
                            break
                        
                if event.type == pygame.MOUSEMOTION and self.current_button:
                    if not self.current_button.hit_test(event.pos):
                        #print self.loop_count,":",event
                        self.current_button.highlight(False)
                        self.render_current_button()
                        self.current_button = None
                    
                if event.type == pygame.MOUSEBUTTONUP:
                    #print self.loop_count,":",event
                    if self.current_button:
                        self.current_button.highlight(False)
                        self.render_current_button()
                        self.current_button = None
                
                if event.type == pygame.QUIT:
                    running = False
                
                event = pygame.event.poll()
        
        IR.deinit()

    def send_ir(self, code):
        parts = code.split(';')
        for part in parts:
            IR.send_once(part)
