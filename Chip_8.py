import random
import pygame
import time

class Chip8:
    def __init__(self):
        self.opcode = 0
        self.memory = [0 for i in range(4096)]
        self.V = [0 for i in range(16)]
        self.I = 0
        self.pc = 0x200
        self.graphics = [0 for i in range(2048)]
        self.delayTimer = 0
        self.soundTimer = 0
        self.stack = [0 for i in range(16)]
        self.sp = 0
        self.key = [0 for i in range(16)]
        self.chip8_fontset = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, 
        0x20, 0x60, 0x20, 0x20, 0x70, 
        0xF0, 0x10, 0xF0, 0x80, 0xF0, 
        0xF0, 0x10, 0xF0, 0x10, 0xF0, 
        0x90, 0x90, 0xF0, 0x10, 0x10, 
        0xF0, 0x80, 0xF0, 0x10, 0xF0, 
        0xF0, 0x80, 0xF0, 0x90, 0xF0, 
        0xF0, 0x10, 0x20, 0x40, 0x40, 
        0xF0, 0x90, 0xF0, 0x90, 0xF0, 
        0xF0, 0x90, 0xF0, 0x10, 0xF0, 
        0xF0, 0x90, 0xF0, 0x90, 0x90, 
        0xE0, 0x90, 0xE0, 0x90, 0xE0, 
        0xF0, 0x80, 0x80, 0x80, 0xF0, 
        0xE0, 0x90, 0x90, 0x90, 0xE0, 
        0xF0, 0x80, 0xF0, 0x80, 0xF0,
        0xF0, 0x80, 0xF0, 0x80, 0x80  
        ]
        self.drawFlag = True

    def emulateCycle(self):

        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc+1]
        
        case = self.opcode & 0xF000

        if case == 0x0000 :
            subCase = self.opcode & 0x000F
            if subCase == 0x000: # 00E0 - Clear Screen
                for i in range(2048):
                    self.graphics[i] = 0
                self.pc+=2
            elif subCase == 0x000E : # 00EE - Return to subroutine
                self.sp -=1
                self.pc = self.stack[self.sp]
                self.pc+=2
            else:
                print('Invalid Instuction (1)')
        elif case == 0x1000: # Jump to address NNN
            self.pc = self.opcode & 0x0FFF
        elif case == 0x2000:
            self.stack[self.sp] = self.pc # Storing the current Address in Stack
            self.sp+=1 # Incrementing Stack pointer
            self.pc = self.opcode & 0x0FFF # Setting Program Counter at NNN
        elif case == 0x3000:
            if self.V[(self.opcode & 0x0F00) >> 8] == (self.opcode & 0x00FF): # Skip the next instruction if Vx == NN
                self.pc+=4
            else:
                self.pc+=2
        elif case == 0x4000: # Skip the next instruction if Vx != NN
            if self.V[(self.opcode & 0x0F00) >> 8] != (self.opcode & 0x00FF):
                self.pc+=4
            else:
                self.pc+=2
        elif case == 0x5000: #Skip the next instruction if Vx == Vy
            if self.V[(self.opcode & 0x0F00) >> 8] == self.V[(self.opcode & 0x00F0) >> 4]:
                self.pc+=4
            else:
                self.pc+=2
        elif case == 0x6000: # Set Vx to NN
            self.V[(self.opcode & 0x0F00) >> 8] = (self.opcode & 0x00FF);
            self.pc+=2
        elif case == 0x7000: # Add NN to Vx. Carry flag isnt changed
            self.V[(self.opcode & 0x0F00) >> 8] += (self.opcode & 0x00FF)
            self.pc += 2
        elif case == 0x8000:
            subCase = self.opcode & 0x000F
            if subCase == 0x0000: # Copy the value of Vy to Vx
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0001: # Store Vx | Vy to Vx
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] | self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0002: # Store Vx & Vy to Vx
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] & self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0003: # Store Vx ^ Vy to Vx
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] ^ self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0004: # Store Vx + Vy to Vx and set Vf to 1 if there is carry
                if self.V[(self.opcode & 0x00F0) >> 4] > (0xFF - self.V[(self.opcode & 0x0F00) >> 8]):
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] + self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0005: # Store Vx - Vy to Vx and set Vf to 1 if there isnt a borrow
                if self.V[(self.opcode & 0x00F0) >> 4] > self.V[(self.opcode & 0x0F00) >> 8]:
                    self.V[0xF] = 0
                else:
                    self.V[0xF] = 1
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] - self.V[(self.opcode & 0x00F0) >> 4]
                self.pc+=2
            elif subCase == 0x0006: # Store the least significat bit of VX in VF and then shift VX to the right by one bit
                self.V[0xF] = self.V[(self.opcode & 0x0F00) >> 8] & 0x1
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x0F00) >> 8] >> 1
                self.pc+=2
            elif subCase == 0x007: # Vx = Vy-Vx. Vf is set to 0 if there is a borrow
                if self.V[(self.opcode & 0x0F00) >> 8] > self.V[(self.opcode & 0x00F0) >> 4] :
                    self.V[0xF] = 0
                else:
                    self.V[0xF] = 1
                self.V[(self.opcode & 0x0F00) >> 8] = self.V[(self.opcode & 0x00F0) >> 4] - self.V[(self.opcode & 0x0F00) >> 8]
                self.pc+=2
            elif subCase == 0x000E: # Stores the most significant bit of Vx in Vf and then shift Vx to the left by one bit
                self.V[0xF] = self.V[(self.opcode & 0x0F00) >> 8] >> 7
                self.pc+=2
            else:
                print('Invalid Opcode (2)')
        
        elif case == 0x0009: # Skip the next instruction if Vx != Vy
            if self.V[(self.opcode & 0x0F00) >> 8] != self.V[(self.opcode & 0x000F0) >> 4]:
                self.pc+=4
            else:
                self.pc+=2
        elif case == 0xA000: # Store NNN to I
            self.I = self.opcode & 0x0FFF
            self.pc+=2
        elif case == 0xB000: # Jump to V0+NNN
            self.pc = (self.opcode & 0x0FFF) + self.V[0]
            self.pc += 2
        elif case == 0xC000: # Set Vx to the sum of bitwise and operation on a random number and NN
            self.V[(self.opcode & 0x0F00) >> 8] = (self.opcode & 0x00FF) & random.randint(0,255)
            self.pc+=2
        elif case == 0xD000: # Draw a sprite at the coordinate (Vx,Vy) which has a width of 8 pixel and height of N+1 pixel
            X = (self.V[(self.opcode & 0x0F00) >> 8])%64
            Y = (self.V[(self.opcode & 0x00F0) >> 4])%32
            height = (self.opcode & 0x000F)
            pixel = 0
            # print("(",X,",",Y,",",height,")")
            self.V[0xF] = 0

            for y in range(height):
                pixel = self.memory[self.I+y]
                for x in range(8):
                    if pixel & (0x80 >> x) != 0: # bin(0x80) = 10000000
                        if self.graphics[X + x + ((Y+y) * 64)] == 1:
                            self.V[0xF] = 1
                        self.graphics[X + x + ((Y+y) * 64)] ^= 1
                
            
            self.drawFlag = True
            self.pc+=2

        elif case == 0xE000:
            subCase = self.opcode & 0x00FF
            if subCase == 0x009E: # Skip the next instruction if the key stored in Vx is pressed
                if self.key[self.V[(self.opcode & 0x0F00) >> 8]] != 0:
                    self.pc+=4
                else:
                    self.pc+=2
            elif 0x00A1: # Skips the next instruction if key stored in Vx isnt pressed
                if self.key[self.V[(self.opcode & 0x0F00) >> 8]] == 0:
                    self.pc+=4
                else:
                    self.pc+=2
            else:
                print('Invalid Opcode(3)')
        elif case == 0xF000:
            subCase = self.opcode & 0x00FF
            if subCase == 0x0007: # Set the value of delay timer to Vx
                self.V[(self.opcode & 0x0F00) >> 8] = self.delayTimer
                self.pc+=2
            elif subCase == 0x000A: # A key press is awaited, and then stored in Vx.( All process halted till then).
                while(True):
                    for i in range(16):
                        if self.key[i] != 0:
                            self.V[(self.opcode & 0x0F00) >> 8] = i;
                            break
                
                self.pc+=2
            elif subCase == 0x0015: # Set delay Timer to Vx
                self.delayTimer = self.V[(self.opcode & 0x0F00) >> 8]
                self.pc+=2
            elif subCase == 0x0018: # Set sounbd Timer to Vx
                self.soundTimer = self.V[(self.opcode & 0x0F00) >> 8]
                self.pc+=2
            elif subCase == 0x001E: # Add Vx to I
                if self.I + self.V[(self.opcode & 0x0F00) >> 8] > 0xFFF:
                    self.V[0xF] = 1
                else:
                    self.V[0xF] = 0
                self.I += self.V[(self.opcode & 0x0F00) >> 8] 
                self.pc+=2
            elif subCase == 0x0029: # Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
                self.I = self.V[(self.opcode & 0x0F00) >> 8] * 0x5
                self.pc+=2
            elif subCase == 0x0033:
                self.memory[self.I] = self.V[(self.opcode & 0x0F00) >> 8]//100
                self.memory[self.I+1] = (self.V[(self.opcode & 0x0F00) >> 8]//10)%10
                self.memory[self.I+2] = (self.V[(self.opcode & 0x0F00) >> 8]%100)%10
                self.pc+=2
            elif subCase == 0x0055: # Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.
                for i in range(((self.opcode & 0x0F00) >> 8)+1):
                    self.memory[self.I+i] = self.V[i]
                self.I+=((self.opcode & 0x0F00) >> 8) + 1
                self.pc+=2
            elif subCase == 0x0065: # Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified
                for i in range(((self.opcode & 0x0F00) >> 8) + 1):
                    self.V[i] = self.memory[self.I+i]
                    self.I+=((self.opcode & 0x0F00) >> 8)+1
                    self.pc+=2
            else:
                print('Invalid Opcode (4)')
            
        else:
            print('Invalid Opcode (5)')
        
        if self.delayTimer > 0:
            self.delayTimer-=1
        
        if self.soundTimer > 0:
            if self.soundTimer == 1:
                print('BEEP')
            self.soundTimer-=1
        

chip8 = Chip8()
     
def loadApplication(fileName):

    try:
        with open(fileName,'rb') as file:
            byte = file.read(1)
            i = 0
            while byte:
                chip8.memory[512+i] = ord(byte)
                byte = file.read(1)
                i+=1
        print('Application loaded successfully!')
        print("Memory : ")
        print(chip8.memory)
    except Exception as e:
        print(e)



clock = pygame.time.Clock()
pygame.init()

win = pygame.display.set_mode((640,320))
win.fill((0,0,0))

def drawOnScreen():
    surf =  pygame.surface.Surface((64, 32))
    surf.fill((0,0,0))

    if chip8.drawFlag:
        for x in range(64):
            for y in range(32):
                if chip8.graphics[x+(y*64)] == 1:
                    surf.set_at((x,y),(255,255,255)) 
                else:
                    surf.set_at((x,y),(0,0,0))
        chip8.drawFlag = False
    pygame.transform.scale(surf, (640, 320), win)
    

loadApplication('invaders.c8')


while True:
    chip8.emulateCycle()
    drawOnScreen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                chip8.key[0] = 1
            elif event.key == pygame.K_2:
                chip8.key[1] = 1
            elif event.key == pygame.K_3:
                chip8.key[2] = 1
            elif event.key == pygame.K_4:
                chip8.key[3] = 1
            elif event.key == pygame.K_q:
                chip8.key[4] = 1
            elif event.key == pygame.K_w:
                chip8.key[5] = 1
            elif event.key == pygame.K_e:
                chip8.key[6] = 1
            elif event.key == pygame.K_r:
                chip8.key[7] = 1
            elif event.key == pygame.K_a:
                chip8.key[8] = 1
            elif event.key == pygame.K_s:
                chip8.key[9] = 1
            elif event.key == pygame.K_d:
                chip8.key[10] = 1
            elif event.key == pygame.K_f:
                chip8.key[11] = 1
            elif event.key == pygame.K_z:
                chip8.key[12] = 1
            elif event.key == pygame.K_x:
                chip8.key[13] = 1
            elif event.key == pygame.K_c:
                chip8.key[14] = 1
            elif event.key == pygame.K_v:
                chip8.key[15] = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_1:
                chip8.key[0] = 0
            elif event.key == pygame.K_2:
                chip8.key[1] = 0
            elif event.key == pygame.K_3:
                chip8.key[2] = 0
            elif event.key == pygame.K_4:
                chip8.key[3] = 0
            elif event.key == pygame.K_q:
                chip8.key[4] = 0
            elif event.key == pygame.K_w:
                chip8.key[5] = 0
            elif event.key == pygame.K_e:
                chip8.key[6] = 0
            elif event.key == pygame.K_r:
                chip8.key[7] = 0
            elif event.key == pygame.K_a:
                chip8.key[8] = 0
            elif event.key == pygame.K_s:
                chip8.key[9] = 0
            elif event.key == pygame.K_d:
                chip8.key[10] = 0
            elif event.key == pygame.K_f:
                chip8.key[11] = 0
            elif event.key == pygame.K_z:
                chip8.key[12] = 0
            elif event.key == pygame.K_x:
                chip8.key[13] = 0
            elif event.key == pygame.K_c:
                chip8.key[14] = 0
            elif event.key == pygame.K_v:
                chip8.key[15] = 0
        

    pygame.display.update()





