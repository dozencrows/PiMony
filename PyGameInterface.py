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
import I2C
import RPIO

from TouchScreenButton import TouchScreenButton
from Backlight import Backlight

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

BUTTON_TIMEOUT      = 0.3
I2C_DEBOUNCE_COUNT  = 3

SCREEN_SAVER_TIMEOUT	= 30.0
TIME_STEP		= 0.008

test_button_layout = [
#    dotdict({ 'x':0, 'y':0, 'width':2, 'height':1, 'text':"Power", 'code':"Phillips-HTS KEY_POWER KEY_POWER KEY_POWER;RM-ED050-12 KEY_POWER" }),
    dotdict({ 'x':0, 'y':0, 'width':2, 'height':1, 'text':"Power", 'code':"Phillips-HTS KEY_POWER;RM-ED050-12 KEY_POWER;Phillips-HTS KEY_POWER" }),
    dotdict({ 'x':0, 'y':1, 'width':1, 'height':1, 'text':"Vol +", 'code':"Phillips-HTS KEY_VOLUMEUP" }),
    dotdict({ 'x':0, 'y':2, 'width':1, 'height':1, 'text':"Vol -", 'code':"Phillips-HTS KEY_VOLUMEDOWN" }),
    dotdict({ 'x':1, 'y':1, 'width':1, 'height':1, 'text':"Chan +", 'code':"RM-ED050-12 KEY_CHANNELUP" }),
    dotdict({ 'x':1, 'y':2, 'width':1, 'height':1, 'text':"Chan -", 'code':"RM-ED050-12 KEY_CHANNELDOWN" }),
    dotdict({ 'x':0, 'y':3, 'width':1, 'height':1, 'text':"Surrnd", 'code':"Phillips-HTS KEY_CHANNELUP" }),
    dotdict({ 'x':1, 'y':3, 'width':1, 'height':1, 'text':"Enter", 'code':"RM-ED050-12 KEY_SELECT" }),
    dotdict({ 'x':0, 'y':4, 'width':1, 'height':1, 'text':"Info", 'code':"RM-ED050-12 KEY_INFO" }),
    dotdict({ 'x':1, 'y':4, 'width':1, 'height':1, 'text':"Back", 'code':"RM-ED050-15 KEY_BACK" }),
    dotdict({ 'x':0, 'y':5, 'width':2, 'height':1, 'text':"Mute", 'code':"Phillips-HTS KEY_MUTE" }),
]

gpio_buttons = [
    dotdict({ 'gpio': 15, 'code':"RM-ED050-12 KEY_UP" }),
    dotdict({ 'gpio': 16, 'code':"RM-ED050-12 KEY_DOWN" }),
    dotdict({ 'gpio': 13, 'code':"RM-ED050-15 KEY_DIRECTORY" }),
]

i2c_buttons = [
    dotdict({ 'mask': 0x004, 'code':"RM-ED050-12 KEY_1"}),
    dotdict({ 'mask': 0x040, 'code':"RM-ED050-12 KEY_2"}),
    dotdict({ 'mask': 0x400, 'code':"RM-ED050-12 KEY_3"}),

    dotdict({ 'mask': 0x002, 'code':"RM-ED050-12 KEY_4"}),
    dotdict({ 'mask': 0x020, 'code':"RM-ED050-12 KEY_5"}),
    dotdict({ 'mask': 0x200, 'code':"RM-ED050-12 KEY_6"}),

    dotdict({ 'mask': 0x001, 'code':"RM-ED050-12 KEY_7"}),
    dotdict({ 'mask': 0x010, 'code':"RM-ED050-12 KEY_8"}),
    dotdict({ 'mask': 0x100, 'code':"RM-ED050-12 KEY_9"}),

    dotdict({ 'mask': 0x080, 'code':"RM-ED050-12 KEY_0"}),
]

def signal_handler(signal, frame):
    quit_event = pygame.event.Event(pygame.QUIT)
    pygame.event.post(quit_event)

class PyGameInterface(object):
    def __init__(self):
        pygame.font.init()
        #self.font = pygame.font.Font("LiberationSansNarrow-Bold.ttf", 14)
        #self.font_large = pygame.font.Font("LiberationSansNarrow-Bold.ttf", 16)
        self.font = pygame.font.Font("Impact.ttf", 16)
        self.font_large = pygame.font.Font("Impact.ttf", 18)
        RPIO.setmode(RPIO.BOARD)
        RPIO.setwarnings(False)
        RPIO.setup(8, RPIO.OUT)
        RPIO.output(8, False)
	self.backlight = Backlight()

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
        
    def release_current_button(self):
        self.current_button.highlight(False)
        self.render_current_button()
        self.current_button = None
        
    def update_display(self):
        if self.display_dirty:
            pygame.display.update(self.dirty_rect)
            self.display_dirty = False
            self.dirty_rect.inflate_ip(-self.dirty_rect.w, -self.dirty_rect.h)
            
    def gpio_button_callback(self, gpio, value):
        if value == 0:
            button = self.gpio_buttons[gpio]
            inject_event = pygame.event.Event(pygame.USEREVENT, {'code':button.code})
            pygame.event.post(inject_event)
        
    def init_gpio_buttons(self, buttons):
        self.gpio_buttons = {}
        for button in buttons:
            self.gpio_buttons[button.gpio] = button
            RPIO.add_interrupt_callback(button.gpio, self.gpio_button_callback, edge='both', pull_up_down=RPIO.PUD_UP, debounce_timeout_ms=150)

    def init_i2c_buttons(self, buttons):
        self.i2c_raw_data = 0
        self.i2c_buttons = []
        for button in buttons:
            self.i2c_buttons.append(dotdict({'definition':button, 'pending_state':False, 'debounce':0, 'state':False}))
    
    def poll_i2c_buttons(self):
        i2c_raw_data = I2C.poll_keys()
        if self.i2c_raw_data != i2c_raw_data:
            self.i2c_raw_data = i2c_raw_data
            
            for button in self.i2c_buttons:
                button_state = (i2c_raw_data & button.definition.mask) != 0
                if button_state != button.pending_state:
                    button.debounce = I2C_DEBOUNCE_COUNT
                    button.pending_state = button_state
                    
        for button in self.i2c_buttons:
            if button.pending_state != button.state:
                button.debounce -= 1
                if button.debounce <= 0:
                    button.state = button.pending_state
                    if button.state:
                        self.send_ir(button.definition.code)
        
    def run(self):
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGQUIT, signal_handler)
        
        IR.init()
        I2C.init()
        
        running = True
        
        self.button_style = { Style.FONT: self.font, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                              Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255),   Style.HIGHLIGHT_COLOUR: (0, 255, 0) }
        self.button_style_large = { Style.FONT: self.font_large, Style.BACKGROUND_COLOUR: (255,128,0), Style.BORDER_COLOUR: (255, 255, 255), 
                                    Style.BORDER_WIDTH: 1, Style.TEXT_COLOUR: (255, 255, 255), Style.HIGHLIGHT_COLOUR: (0, 255, 0) }

        self.layout_buttons(test_button_layout)
        self.init_gpio_buttons(gpio_buttons)
        self.init_i2c_buttons(i2c_buttons)
        
        self.screen.fill((0, 0, 0))
        for button in self.buttons:
            button.render(self.screen)
        pygame.display.flip()
	self.backlight.set(True)
        
        self.display_dirty = False
        self.current_button = None
        self.dirty_rect = pygame.Rect(0, 0, 0, 0)
	self.screen_saver = False
	self.screen_saver_count = SCREEN_SAVER_TIMEOUT

        RPIO.wait_for_interrupts(threaded=True)
        
        print "PiMony running..."

        while running:
            
            waiting_for_input = True
            
            while running and waiting_for_input:
                self.update_display()

                # Can't use pygame.event.wait() as this blocks signals
                time.sleep(TIME_STEP)
                self.poll_i2c_buttons()
                event = pygame.event.poll()
                
                while event.type != pygame.NOEVENT:
                    if event.type == pygame.MOUSEBUTTONDOWN and self.current_button == None:
                        if self.screen_saver:
                            self.disable_screen_saver()
                        else:
                            for button in self.buttons:
                                if button.hit_test(event.pos):
                                    self.current_button = button
                                    button.highlight(True)
                                    self.render_current_button()
                                    self.press_time = time.time()
                                    self.current_ir_code = self.current_button.code
                                    waiting_for_input = False
                                    pygame.event.clear()
                                    break
                            
                    if event.type == pygame.USEREVENT:
                        self.current_ir_code = event.code
                        waiting_for_input = False
                        pygame.event.clear()
                        break

                    if event.type == pygame.MOUSEBUTTONUP and self.current_button:
                        self.release_current_button()

                    if event.type == pygame.MOUSEMOTION and self.current_button:
                        if not self.current_button.hit_test(event.pos):
                            self.release_current_button()
                            
                    if event.type == pygame.QUIT:
                        running = False
                    
                    event = pygame.event.poll()
                    
                if self.current_button and time.time() - self.press_time > BUTTON_TIMEOUT:
                    self.release_current_button()

                self.screen_saver_count -= TIME_STEP

                if self.screen_saver_count <= 0 and not self.screen_saver:
                    self.enable_screen_saver()
                    
            if not waiting_for_input:
                self.update_display()
                pygame.event.set_blocked([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])
                self.send_ir(self.current_ir_code)
                time.sleep(0.1)
                pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION])
        
        I2C.deinit()
        IR.deinit()

    def send_ir(self, code):
        print "Sending:", code
        RPIO.output(8, True)
        parts = code.split(';')
        for part in parts:
            IR.send_once(part)
        RPIO.output(8, False)
	self.disable_screen_saver()

    def enable_screen_saver(self):
        self.screen_saver = True
        self.backlight.set(False)

    def disable_screen_saver(self):
        self.screen_saver_count = SCREEN_SAVER_TIMEOUT
        if self.screen_saver:
            self.screen_saver = False
            self.backlight.set(True)
