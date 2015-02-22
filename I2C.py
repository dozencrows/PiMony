#=======================================================================
# Copyright Nicholas Tuckett 2015.
# Distributed under the MIT License.
# (See accompanying file license.txt or copy at
#  http://opensource.org/licenses/MIT)
#=======================================================================

import smbus

I2C_BUS =           1
I2C_ADDR =          0x20
MCP23017_IODIRA =   0x00
MCP23017_IODIRB =   0x01
MCP23017_IPOLA =    0x02
MCP23017_IPOLB =    0x03
MCP23017_GPPUA =    0x0c
MCP23017_GPPUD =    0x0c
MCP23017_GPIOA =    0x12
MCP23017_GPIOB =    0x13

GPIOA_SETUP_MASK =  0x0f
GPIOA_POLL_COL1 =   0xc0
GPIOA_POLL_COL2 =   0xa0
GPIOA_POLL_COL3 =   0x60

bus = None

def init():
    global bus;
    bus = smbus.SMBus(I2C_BUS)
    
    bus.write_byte_data(I2C_ADDR, MCP23017_IODIRA, GPIOA_SETUP_MASK)
    bus.write_byte_data(I2C_ADDR, MCP23017_GPPUA, GPIOA_SETUP_MASK)
    bus.write_byte_data(I2C_ADDR, MCP23017_IPOLA, GPIOA_SETUP_MASK)

def poll_keys():
    bus.write_byte_data(I2C_ADDR, MCP23017_GPIOA, GPIOA_POLL_COL1)
    column_data = bus.read_byte_data(I2C_ADDR, MCP23017_GPIOA) & 0x0f

    bus.write_byte_data(I2C_ADDR, MCP23017_GPIOA, GPIOA_POLL_COL2)
    column_data = column_data | (bus.read_byte_data(I2C_ADDR, MCP23017_GPIOA) & 0x0f) << 4

    bus.write_byte_data(I2C_ADDR, MCP23017_GPIOA, GPIOA_POLL_COL3)
    column_data = column_data | (bus.read_byte_data(I2C_ADDR, MCP23017_GPIOA) & 0x0f) << 8
    
    return column_data

def deinit():
    pass
