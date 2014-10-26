'''
Created on 25 May 2014

@author: ntuckett
'''

import pygame
import pygame.font
import os
import time
import imp

from TouchScreenButton import TouchScreenButton
import Style

SCREEN_WIDTH    = 240
SCREEN_HEIGHT   = 320
BUTTON_MARGIN   = 1
BUTTON_COLUMNS  = 2
BUTTON_ROWS     = 6

BUTTON_X_OFFSET         = BUTTON_MARGIN
BUTTON_Y_OFFSET         = BUTTON_MARGIN
BUTTON_COLUMN_WIDTH     = (SCREEN_WIDTH / BUTTON_COLUMNS)
BUTTON_ROW_HEIGHT       = (SCREEN_HEIGHT / BUTTON_ROWS) 
BUTTON_WIDTH            = BUTTON_COLUMN_WIDTH - (2 * BUTTON_MARGIN)
BUTTON_HEIGHT           = BUTTON_ROW_HEIGHT - (2 * BUTTON_MARGIN)
BUTTON_DOUBLE_WIDTH     = (BUTTON_COLUMN_WIDTH * 2) - (2 * BUTTON_MARGIN)
BUTTON_DOUBLE_HEIGHT    = (BUTTON_ROW_HEIGHT * 2) - (2 * BUTTON_MARGIN)

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
    
    def run(self):
        running = True
        
        self.button_style = { Style.FONT: self.font, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                              Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255),   Style.HIGHLIGHT_COLOUR: (0, 255, 0) }
        self.button_style_large = { Style.FONT: self.font_large, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                                    Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255), Style.HIGHLIGHT_COLOUR: (0, 255, 0) }

        self.buttons = [TouchScreenButton(x * BUTTON_COLUMN_WIDTH + BUTTON_X_OFFSET, 
                                          y * BUTTON_ROW_HEIGHT + BUTTON_Y_OFFSET,
                                          BUTTON_WIDTH, 
                                          BUTTON_HEIGHT,
                                          "Button %d-%d" % (x, y),
                                          "B%d%d" % (x, y),
                                          self.button_style
                                          ) for y in range(0, 2) for x in range(0, BUTTON_COLUMNS) ]

        self.buttons.extend([TouchScreenButton(x * BUTTON_COLUMN_WIDTH + BUTTON_X_OFFSET, 
                                          y * BUTTON_ROW_HEIGHT + BUTTON_Y_OFFSET,
                                          BUTTON_DOUBLE_WIDTH, 
                                          BUTTON_HEIGHT,
                                          "Button %d-%d" % (x, y),
                                          "B%d%d" % (x, y),
                                          self.button_style_large
                                          ) for y in range(2, 4) for x in range(0, BUTTON_COLUMNS, BUTTON_COLUMNS) ])

        self.buttons.extend([TouchScreenButton(x * BUTTON_COLUMN_WIDTH + BUTTON_X_OFFSET, 
                                          y * BUTTON_ROW_HEIGHT + BUTTON_Y_OFFSET,
                                          BUTTON_WIDTH, 
                                          BUTTON_DOUBLE_HEIGHT,
                                          "Button %d-%d" % (x, y),
                                          "B%d%d" % (x, y),
                                          self.button_style
                                          ) for y in range(4, 6, 2) for x in range(0, BUTTON_COLUMNS) ])
        
        self.screen.fill((0, 0, 0))
        for button in self.buttons:
            button.render(self.screen)
            
        self.display_dirty = True
        self.current_button = None

        while running:
            if self.display_dirty:
                pygame.display.flip()
                self.display_dirty = False

            event = pygame.event.wait()
            while event.type != pygame.NOEVENT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print event
                    for button in self.buttons:
                        if button.hit_test(event.pos):
                            self.current_button = button
                            button.highlight(True)
                            self.display_dirty = True
                            self.current_button.render(self.screen)
                            break
                        
                if event.type == pygame.MOUSEMOTION and self.current_button:
                    self.current_button.highlight(self.current_button.hit_test(event.pos))
                    self.display_dirty = True
                    self.current_button.render(self.screen)
                    
                if event.type == pygame.MOUSEBUTTONUP and self.current_button:
                    self.current_button.highlight(False)
                    self.display_dirty = True
                    self.current_button.render(self.screen)
                    self.current_button = None
                
                if event.type == pygame.QUIT:
                    running = False
                
                event = pygame.event.poll()


