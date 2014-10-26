#
# Style data:
#    text_colour
#    background_colour
#    border_colour
#    highlight_colour
#    font

import pygame.draw

import Style

class TouchScreenButton(object):
    def __init__(self, x, y, width, height, prompt, code, style):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.prompt = prompt
        self.code = code
        self.style = style
        self.rect = (self.x, self.y, self.width, self.height)
        self.highlighted = False
        self.text_surface = self.style[Style.FONT].render(self.prompt, False, self.style[Style.TEXT_COLOUR]) 
        
    def render(self, surface):
        if self.highlighted:
            surface.fill(self.style[Style.HIGHLIGHT_COLOUR], self.rect)
        else:
            surface.fill(self.style[Style.BACKGROUND_COLOUR], self.rect)
            
        pygame.draw.rect(surface, self.style[Style.BORDER_COLOUR], self.rect, self.style[Style.BORDER_WIDTH])
        text_width, text_height = self.text_surface.get_size()
        surface.blit(self.text_surface, (self.x + (self.width - text_width) / 2, self.y + (self.height - text_height) / 2))
        
    def highlight(self, highlight):
        self.highlighted = highlight
        
    def hit_test(self, point):
        relative_x = point[0] - self.x
        if relative_x >= 0 and relative_x < self.width:
            relative_y = point[1] - self.y
            return relative_y >= 0 and relative_y < self.height
        return False
