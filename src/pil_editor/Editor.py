import tkinter
import pygame
from pygame.mouse import get_pos
from pygame.transform import scale
import os


RESIZE_CIRCLE_RADIUS = 10
WINDOW_SIZE = (1600, 900)
####################################################
# helper methods and classes

pygame.init()

#Directory constants
ASSETS_DIRECTORY = "Assets" #currently uses relative directory, change if neccessary
EDITOR_ICON_PATH = os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","AddObjectButton","add_1.png")
EDITOR_ICON = pygame.image.load(EDITOR_ICON_PATH)

#preloading fonts with varying sizes
font = pygame.font.Font(os.path.join(ASSETS_DIRECTORY,'base_font.ttf'), 16)
font_L = pygame.font.Font(os.path.join(ASSETS_DIRECTORY,'base_font.ttf'), 20)
font_XL = pygame.font.Font(os.path.join(ASSETS_DIRECTORY,'base_font.ttf'), 30)

from tkinter import * 
from tkinter import simpledialog
root=Tk() 
root.withdraw()
root.iconphoto(True, tkinter.PhotoImage(file=EDITOR_ICON_PATH))

def AskForValue(title, question):
    return simpledialog.askstring(title, question,
                                parent=root)

class FilterPopup(simpledialog.Dialog):

    def body(self, master):
        self.master = master
        self.sharpness = self.CreateSlider("Sharpness", 0)
        self.contrast = self.CreateSlider("Contrast", 1)
        self.color = self.CreateSlider("Color", 2)
        self.brightness = self.CreateSlider("Brightness", 3)
        return self

    def CreateSlider(self, name, column):
        Label(self.master, text=name).grid(row=0, column=column)
        val = StringVar(name=name)                    # an MVC-trick an indirect value-holder
        
        SCALE = Scale( self.master,
                        variable   = val,    # MVC-Model-Part value holder
                        from_      = 0,       # MVC-Model-Part value-min-limit
                        to         =  100.0,       # MVC-Model-Part value-max-limit
                        length     = 200,         # MVC-Visual-Part layout geometry [px]
                        digits     =   5,         # MVC-Visual-Part presentation trick
                        resolution =   0.01     # MVC-Controller-Part stepping
                        )
        SCALE.setvar(name, 1)
        ENTRY = Entry(self.master, textvariable=val)
        ENTRY.grid(row=3, column=column)
        SCALE.grid(row=2,column=column)
        return SCALE   

    def apply(self):
        self.sharpness = self.sharpness.get()
        self.contrast = self.contrast.get()
        self.color = self.color.get()
        self.brightness = self.brightness.get()

    class Values:
        def __init__(self, sharpness, contrast, color, brightness) -> None:
            self.sharpness = sharpness
            self.contrast = contrast
            self.color = color
            self.brightness = brightness

        def __repr__(self) -> str:
            return str([self.sharpness, self.contrast, self.color, self.brightness])

    def GetValues(self):
        return self.Values(self.sharpness,self.contrast,self.color,self.brightness)

def aspect_scale(img,bx,by):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio.
    **FROM** : http://www.pygame.org/pcr/transform_scale/"""
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    
    sx = int(sx)
    sy = int(sy)

    return pygame.transform.scale(img, (sx,sy))

class Color():
    BLACK  = ( 0, 0, 0)
    WHITE  = ( 255, 255, 255)

    RED    = ( 255, 0, 0)
    GREEN  = ( 0, 255, 0)
    BLUE   = ( 0, 0, 255)

    YELLOW = ( 204, 255, 51 )
    PURPLE = ( 153, 0, 204  )
    BROWN  = ( 153, 102, 51 )
    PINK   = ( 255, 0, 102  )
    LIME   = ( 108, 218, 0  )
####################################################


class Camera():
    def __init__(self) -> None:
        self.x : float = 0
        self.y : float = 0
        self.zoom : float = 1.0

        self.Show_rects = True
        self.Show_names = False

    def Update(self) -> None:
        pass

    def FixCameraOffset(self) -> None:
        return
        self.x =  WINDOW_SIZE[0] / 4 * (self.zoom - 1)
        self.y =  WINDOW_SIZE[1] / 4 * (self.zoom - 1)

    def ZoomIn(self) -> None:
        if self.zoom >= 2:
            return
        self.zoom += 0.05
        self.FixCameraOffset()


    def ZoomOut(self) -> None:
        if self.zoom <= 0.5:
            return
        self.zoom -= 0.05
        self.FixCameraOffset()

    def WorldToCameraCoordinates(self, x, y) -> tuple:
        return ((x- self.x) * camera.zoom, (y- self.y) * camera.zoom )

    def CameraToWorldCoordinates(self, x, y) -> tuple:
        return ((x + self.x) / camera.zoom, (y + self.y) / camera.zoom)

    def WorldToCameraSize(self, width, height) -> tuple:
        return (width * self.zoom, height * self.zoom)

    def CameraToWorldSize(self, width, height) -> tuple:
        return (width / self.zoom, height / self.zoom)

#Global Camera 
camera = Camera()

class Mouse():
    def __init__(self) -> None:
        self.x : float = 0
        self.y : float = 0
        self.dragging : bool = False
        self.holding = None
        self.selected = None

        self.dragging_x = 0
        self.dragging_y = 0
        self.offset_x = 0
        self.offset_y = 0

        self.resizing = False

    def Update(self, Editor) -> None:
        self.x, self.y = get_pos()
        if self.dragging:
            camera.x = -(self.x - self.dragging_x)
            camera.y = -(self.y - self.dragging_y)
            Editor.UpdateRects()
            return
        if self.holding != None:
            if self.resizing:
                obj = self.holding.object
                hd_coords = obj.GetScreenCoordinates()
                ms_coords = self.get_pos()
                new_size = camera.CameraToWorldSize((ms_coords[0] - hd_coords[0]), (ms_coords[1] - hd_coords[1]))
                obj.SetSize(*new_size)
            else:
                obj = self.holding.object
                obj.SetPosition(*camera.CameraToWorldCoordinates(self.x - self.offset_x, self.y - self.offset_y))

    def SetClicked(self, layer, holding=True) -> None:
        self.ResetSelected()
        self.selected = layer
        layer.rect_color = Color.RED
        layer.update_rect()
        layer.SetState(Button.State.CLICKED)
        layer.object.rect_color = Color.RED
        layer.object.update_rect()
        if holding:
            self.holding = layer
            obj_coords = layer.object.GetScreenCoordinates()
            offsets = (mouse.GetX() - obj_coords[0], mouse.GetY() - obj_coords[1])
            self.offset_x = offsets[0]
            self.offset_y = offsets[1]

    def Drag(self) -> None:
        self.dragging = True 
        self.dragging_x = self.x + camera.x
        self.dragging_y = self.y + camera.y  

    def Reset(self) -> None:
        self.holding = None
        self.resizing = False
        self.dragging = False

    def ResetSelected(self) -> None:
        if self.selected != None:
            #Actual object
            obj = self.selected.object
            obj.rect_color = Color.WHITE
            obj.update_rect()

            #Layer
            obj = self.selected
            obj.SetState(Button.State.DEFAULT)
            obj.rect_color = Color.BLACK
            obj.update_rect()
            self.selected = None

    def GetX(self) -> float:
        return self.x

    def GetY(self) -> float:
        return self.y

    def get_pos(self) -> tuple:
        return (self.x, self.y)
        

#Global Mouse 
mouse = Mouse()


class Object():
    _id_count_ = 0
    def __init__(self, x=0, y=0, img=None, width=None, height=None, show_rect=True, collidable=True, resizable=True, keep_aspect_ratio=True) -> None:
        self.x : float = x
        self.y : float = y
        self.width : int = width
        self.height : int = height
        self.__image__ = None
        self.show_rect : bool = show_rect
        self.collidable : bool = collidable
        self.hidden = False
        self.resizable : bool = resizable
        self.keep_aspect_ratio = keep_aspect_ratio

        self.id = Object._id_count_
        Object._id_count_ += 1

        if img != None and isinstance(img, str):
            img = pygame.image.load(img)
        self.image = img
        if self.image != None:
            if self.height != None and self.width != None:
                self.image = aspect_scale(self.image, self.width,self.height)
            else : 
                self.width = self.image.get_width()
                self.height = self.image.get_height()

            self.__image__ = self.image.copy()
            self.image = self.image.convert_alpha()

        self.rect : pygame.Rect = pygame.Rect(1,1,1,1)
        self.rect_color = Color.WHITE
        self.update_rect()

    def SetName(self, name):
        self.id = name
        return self

    def SetWidth(self, width) -> None:
        self.width = max(0,width)
        self.update_rect()

    def SetHeight(self, height) -> None:
        self.height = max(0,height)
        self.update_rect()

    def SetSize(self, width, height) -> None:
        self.width = max(0,width)
        self.height = max(0,height)
        self.update_rect()

    def SetPosition(self, x, y) -> None:
        self.x = x
        self.y = y 
        self.update_rect()

    def CheckCollision(self) -> bool:
        if self.resizable:
            if self.GetResizeCircle().collidepoint(*mouse.get_pos()):
                mouse.resizing = True
                return True
        if self.rect.collidepoint(*mouse.get_pos()):
            mouse.resizing = False
            return True
        return False

    def Colliding(self, editor, layer) -> None:
        if self.collidable == False: return
        mouse.SetClicked(layer)

    def Draw(self, screen) -> None:
        if self.hidden: return
        if self.image != None:
            screen.blit(self.image, self.GetScreenCoordinates())
        if self.show_rect and camera.Show_rects: 
            pygame.draw.rect(screen, self.rect_color, self.rect, width=3)
            pygame.draw.circle(screen, Color.RED, self.BottomRight(), camera.zoom * RESIZE_CIRCLE_RADIUS, width=0)
            
        if self.show_rect and camera.Show_names:
            if len(str(self.id)) > 16:
                name = font.render(str(self.id)[:(16 - len(str(self.id)))] + "...", 1, Color.BLACK)
            else :
                name = font.render(str(self.id), 1, Color.BLACK)
            name_coords = self.GetScreenCoordinates()
            name_coords = (name_coords[0] + self.GetScreenSize()[0]/2 - 5 * len(str(self.id)), name_coords[1] + self.GetScreenSize()[1]/2.5)
            screen.blit(name, name_coords)

    def update_rect(self) -> None:
        self.rect.update(*self.GetScreenCoordinates() , *self.GetScreenSize())
        if self.image != None:
            if self.keep_aspect_ratio:
                self.image = aspect_scale(self.__image__.convert_alpha(),*self.GetScreenSize())
            else :
                size = self.GetScreenSize()
                size = (int(size[0]), int(size[1]))
                self.image = scale(self.__image__.convert_alpha(),size)

    def GetScreenCoordinates(self) -> tuple:
        return camera.WorldToCameraCoordinates(self.x, self.y)

    def GetResizeCircle(self):
        coords = self.BottomRight()
        return pygame.Rect(coords[0] - camera.zoom * RESIZE_CIRCLE_RADIUS, coords[1] - camera.zoom * RESIZE_CIRCLE_RADIUS, camera.zoom * RESIZE_CIRCLE_RADIUS * 2, camera.zoom * RESIZE_CIRCLE_RADIUS * 2)

    def BottomRight(self) -> tuple:
        size = (self.width, self.height)
        return camera.WorldToCameraCoordinates(self.x + size[0], self.y + size[1])

    def GetScreenSize(self) -> tuple:
        return camera.WorldToCameraSize(self.width, self.height)

    def __repr__(self) -> str:
        if self.hidden:
            return f"name: {self.id} x: {self.x:.0f} y: {self.y:.0f} [HIDDEN]"
        return f"name: {self.id} x: {self.x:.0f} y: {self.y:.0f}"

class UI_Element(Object):

    def __init__(self, color = Color.WHITE, fill_width = 1, **kwargs) -> None:
        self.color = color
        self.fill_width = fill_width
        super().__init__(**kwargs)

    def GetScreenCoordinates(self) -> tuple:
            return (self.x, self.y)

    def Draw(self, screen) -> None:
        if self.hidden: return
        if self.image != None:
            screen.blit(self.image, self.GetScreenCoordinates())
        if self.show_rect: 
            pygame.draw.rect(screen, self.color, self.rect, width=self.fill_width)

    def BottomRight(self) -> tuple:
        size = (self.width, self.height)
        return (self.x + size[0], self.y + size[1])

    def GetScreenSize(self) -> tuple:
        return (self.width, self.height)

    def Colliding(self, editor) -> None:
        pass

    def update_rect(self) -> None:
        self.rect.update(*self.GetScreenCoordinates() , *self.GetScreenSize())
        if self.image != None or self.__image__ != None:
            if self.keep_aspect_ratio:
                self.image = aspect_scale(self.__image__.convert_alpha(),*self.GetScreenSize())
            else :
                size = self.GetScreenSize()
                size = (int(size[0]), int(size[1]))
                self.image = scale(self.__image__.convert_alpha(),size)

class Button(UI_Element):
    class State:
        DEFAULT = 0
        HOVER = 1
        CLICKED = 2

    def __init__(self,**kwargs) -> None:
        self.state = Button.State.DEFAULT
        self.timer = 0
        self._tooltip_ = None
        self._tooltipOutline_ = None
        self.Description = "Default button"
        super().__init__(**kwargs)

    def IncrementTimer(self, editor) -> None:
        if editor.clock.get_fps() == 0:
            return
        self.timer += (1/editor.clock.get_fps())
        if self.timer > 1 and self._tooltip_ == None:
            self._tooltip_ = UI_Element(x=self.x  + 65,y=self.y,color=(95,95,95),fill_width=0,width=100,height=100)
            self._tooltipOutline_ = UI_Element(x=self.x  + 63,y=self.y - 2,color=Color.BLACK,fill_width=2,width=102,height=102)
            editor.ui.append(self._tooltip_)
            editor.ui.append(self._tooltipOutline_)
            self.ResetTimer(editor)

    def ResetTimer(self, editor) -> None:
        self.timer = 0

    def update_rect(self) -> None:
        if self.state == Button.State.DEFAULT:
            self.__image__ = self.default
        if self.state == Button.State.HOVER:
            self.__image__ = self.hover
        if self.state == Button.State.CLICKED:
            self.__image__ = self.clicked            
        return super().update_rect()

    def SetState(self, state) -> None:
        self.state = state
        self.update_rect()

class AddObjectButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","AddObjectButton","add_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","AddObjectButton","add_1.png"))
        self.clicked = None #pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","AddObjectButton","add_2.png"))
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        name = AskForValue("Layer Name", "Input Layer Name: (no underscores '_')         ")
        if name == None or len(name.rstrip()) == 0 or not editor.layers.IsUnique(name):
            self.SetState(Button.State.DEFAULT)
            self.update_rect()
            return
        obj = Object(650,350,width=200,height=200)
        obj.id = name
        editor.layers.append(obj)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

class ShowRectButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","OutlineButton","outline_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","OutlineButton","outline_1.png"))
        self.clicked = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","OutlineButton","outline_2.png"))
        super().__init__(img=self.clicked,**kwargs)
        self.SetState(Button.State.CLICKED)
        self.update_rect()

    def Colliding(self, editor) -> None:
        camera.Show_rects = not camera.Show_rects
        if camera.Show_rects and self.state != Button.State.CLICKED:
            self.SetState(Button.State.CLICKED)
        if not camera.Show_rects and self.state != Button.State.DEFAULT:
            self.SetState(Button.State.DEFAULT)
        self.update_rect()
    

class ShowNameButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_1.png"))
        self.clicked = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_2.png"))
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        camera.Show_names = not camera.Show_names
        if camera.Show_names and self.state != Button.State.CLICKED:
            self.SetState(Button.State.CLICKED)
        if not camera.Show_names and self.state != Button.State.DEFAULT:
            self.SetState(Button.State.DEFAULT)
        self.update_rect()

class MoveUpButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","UpButton","up_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","UpButton","up_1.png"))
        self.clicked = None #pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_2.png"))
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            if len(editor.layers.layers) == 1: return

            layers : list = editor.layers.layers

            index = layers.index(mouse.selected)
            if index == 0: return
            layers.insert(index - 1, layers.pop(index))
            editor.layers.update()

#a whole new class is probably not neccessary
class MoveDownButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","DownButton","Down_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","DownButton","Down_1.png"))
        self.clicked = None #pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_2.png"))
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            layers : list = editor.layers.layers
            if len(layers) == 1: return

            index = layers.index(mouse.selected)
            if index == len(layers) - 1: return
            layers.insert(index + 1, layers.pop(index))
            editor.layers.update()

class EditButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","EditButton","edit_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","EditButton","edit_1.png"))
        self.clicked = None #pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_2.png"))
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        self.update_rect()

class FilterButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","FilterButton","filters_0.png"))
        self.hover = pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","FilterButton","filters_1.png"))
        self.clicked = None #pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","ShowNameButton","names_2.png"))
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            FilterPopup(root)

class LayerContainer(UI_Element):
    def __init__(self, color=Color.WHITE, fill_width=1, **kwargs) -> None:
        super().__init__(color=color, fill_width=fill_width, **kwargs)
        self.show_rect=False
        self.layers = []
        self.buttons = []
        self.editor = None

    def IsUnique(self, name : str) -> bool:
        layer : Layer
        for layer in self.layers:
            if layer.object.id.lower() == name.lower():
                return False
        return True
   
    def Draw(self, screen) -> None:
        if self.hidden: return
        super().Draw(screen)

        layer : Layer
        for layer in self.layers:
            layer.Draw(screen)
    
    def __len__(self) -> int:
        return len(self.layers)

    def GetLayerCount(self) -> int:
        return self.__len__()

    def append(self, obj) -> None:
        offset_x = (self.width - 330)/2
        offset_y = 40
        spacing_y = 13.75
        layer = Layer(color=Color.BLACK, fill_width=1, show_rect=False, x=self.x + offset_x,y=self.y + 31 * self.GetLayerCount() + spacing_y * (self.GetLayerCount()+1) + offset_y,width=400 * 0.83,height=50 * 0.83, keep_aspect_ratio=False)
        layer.ShowButton = __Layer_Show_Button__(x=layer.x - 3,y=layer.y, width=50 * 0.84, height=50 * 0.84, show_rect=False)
        layer.ShowButton.layer = layer
        self.buttons.append(layer.ShowButton)
        layer.object = obj
        layer.SetName(obj.id)
        self.layers.append(layer)

    def update(self):
        """(->)"""
        layer : Layer
        offset_x = (self.width - 330)/2
        offset_y = 40
        spacing_y = 13.75
        for index, layer in enumerate(self.layers):
            x=self.x + offset_x
            y=self.y + 31 * index + spacing_y * (index+1) + offset_y
            layer.SetPosition(x,y)
            layer.ShowButton.SetPosition(x-3,y)
            layer.update_rect()
            layer.ShowButton.update_rect()
        return self

    def remove(self, layer):
        """(->)"""
        if layer in self.layers:
            if mouse.selected == layer:
                mouse.ResetSelected()
            self.layers.remove(layer)
        return self

    def removeObject(self, obj):
        """(->)"""
        for layer in self.layers:
            if layer.object == obj:
                self.layers.remove(layer)
                break
        return self

    def __getitem__(self, key):
        return self.layers[key]

    def __iter__(self):
        return iter(self.layers)


class __Layer_Show_Button__(Button):
    __DEFAULT__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","eye_0.png"))
    __HOVER__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","eye_1.png"))
    __CLICKED__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","eye_2.png"))

    def __init__(self, **kwargs) -> None:
        self.default = __Layer_Show_Button__.__DEFAULT__
        self.hover = __Layer_Show_Button__.__HOVER__
        self.clicked = __Layer_Show_Button__.__CLICKED__
        super().__init__(img=self.default,**kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()
        self.layer = None

    def Colliding(self, editor) -> None:
        state = self.layer.object.hidden
        self.layer.object.hidden = not state
        if state:
            self.SetState(Button.State.DEFAULT)
        else :
            self.SetState(Button.State.CLICKED)
            self.layer.SetState(Button.State.DEFAULT)

class Layer(Button):
    __DEFAULT__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","layer_0.png"))
    __HOVER__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","layer_1.png"))
    __CLICKED__ = pygame.image.load(os.path.join(ASSETS_DIRECTORY,"Layout", "Layer","layer_2.png"))
    
    def __init__(self, color=Color.BLACK, fill_width=1, **kwargs) -> None:
        self.default = Layer.__DEFAULT__
        self.hover = Layer.__HOVER__
        self.clicked = Layer.__CLICKED__
        super().__init__(color=color, fill_width=fill_width, **kwargs)
        self.rect_color = color
        self.object : Object = None
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

        self.ShowButton : __Layer_Show_Button__ = None
        self.ValueButton = None

    def Colliding(self, editor) -> None:
        if self.collidable == False or self.object.hidden: return
        mouse.SetClicked(self, holding=False)
        
    def Draw(self, screen) -> None:
        if self.hidden: return
        super().Draw(screen=screen)
        self.ShowButton.Draw(screen=screen)

        if self.show_rect: 
            pygame.draw.rect(screen, self.rect_color, self.rect, width=self.fill_width)
        name = font_L.render(str(self.id), 1, Color.WHITE)
        name_coords = self.GetScreenCoordinates()
        if len(str(self.id)) > 16:
             name = font_L.render(str(self.id)[:(16 - len(str(self.id)))] + "...", 1, Color.WHITE)
        name_coords = (name_coords[0] + 55, name_coords[1] + self.GetScreenSize()[1]/5)
        screen.blit(name, name_coords)

    def __repr__(self) -> str:
        return self.object.__repr__()

class Editor():
    """An editor object which has a Launch() method to launch the editor window.\n Once Launch() is called a pygame instance will run and lock the rest of the code until the window is closed and a\n Additional options can be enabled by setting the properties to true before calling the Launch() method, such as [show_fps] and [__debug_info__]."""
    def __init__(self, Background : str = None) -> None:
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_icon(EDITOR_ICON)
        pygame.display.set_caption('Template Editor')
        self.FPS = 1000 # change if neccessary, FPS doesn't seem to show if there is no fps cap. Setting it to 1000 ensures it will run fast but still properly display fps.
        self.show_fps = False
        self.__debug_info__ = False
        self.done = False
        self.clock = pygame.time.Clock()
    
        bg_size =  (WINDOW_SIZE[0] - 100, WINDOW_SIZE[1] - 100)
        self.background =    Object(x=220,
                                    y=50,
                                    img=aspect_scale(pygame.image.load(Background), *bg_size),
                                    show_rect=False)

        self.layers = LayerContainer(x=1255,y=2,width=413*0.83,height=1080*0.83, keep_aspect_ratio=False, img=os.path.join(ASSETS_DIRECTORY,"Layout", "ui_right.png")) # Object(x=20,y=20,width=200,height=200,img="cat.jpg")
        self.tools  = LayerContainer(x=2,y=2,width=80*0.83,height=1080*0.83, keep_aspect_ratio=False, img=os.path.join(ASSETS_DIRECTORY,"Layout", "ui_left.png"))
        self.layers.editor = self
        self.ui = [AddObjectButton(x=6,y=180, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   ShowRectButton(x=6,y=240, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   ShowNameButton(x=6,y=285, width=70 * 0.84, height=50 * 0.84, keep_aspect_ratio=False, show_rect=False),
                   EditButton(x=6,y=345, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   FilterButton(x=6,y=390, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   MoveUpButton(x=6,y=435, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   MoveDownButton(x=6,y=480, width=70 * 0.84, height=50 * 0.84 ,keep_aspect_ratio=False, show_rect=False),
                   UI_Element(x=14,y=12, width=50 * 0.84, height=50 * 0.84, keep_aspect_ratio=False, show_rect=False, img=os.path.join(ASSETS_DIRECTORY,"Layout", "Tools", "icon.png")),
                   self.layers]
                   #UI_Element(x=960,y=13,width=233,height=879,color=Color.BLACK, fill_width=8, collidable=False)]

    def Draw(self) -> None:
        self.background.Draw(self.screen)

        if self.show_fps:
            Text = font_XL.render("[fps] "+str(int(self.clock.get_fps())), 1, Color.WHITE)
            self.screen.blit(Text, (80,5))
        if self.__debug_info__:

            Text = font_XL.render("[Selected] "+str(mouse.selected), 1, Color.WHITE)
            self.screen.blit(Text, (80,35))
            Text = font_XL.render(f"[Camera] x: {camera.x:.0f} y: {camera.y:.0f}", 1, Color.WHITE)
            self.screen.blit(Text, (80,65))
            Text = font_XL.render(f"[Mouse] x: {mouse.x:.0f} y: {mouse.y:.0f}", 1, Color.WHITE)
            self.screen.blit(Text, (80,95))

        obj : Layer
        for obj in self.layers[::-1]:
            obj.object.Draw(self.screen)

        self.tools.Draw(self.screen)

        for obj in self.ui:
            obj.Draw(self.screen)

        self.layers.Draw(self.screen)
        

    def CollisonCheck(self) -> None:
        objs : UI_Element
        for objs in self.layers.buttons + self.layers.layers:
            if objs.hidden: continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self)
                    return

        objs : UI_Element
        for objs in self.ui:
            if objs.hidden: continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self)
                    return

        layer : Layer
        tmp = self.layers.layers
        if mouse.selected != None:
            tmp = [mouse.selected] + tmp
        for layer in tmp:
            objs : Object = layer.object
            if objs.hidden: continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self, layer)
                    return    

        mouse.ResetSelected()

    def ButtonHoverCheck(self) -> None:
        self.__hover_check__(self.ui)
        self.__hover_check__(self.layers.buttons + self.layers.layers)

    def __hover_check__(self, list) -> None:
        element : Button
        for element in list:
            if element.hidden: continue
            if isinstance(element, Button):
                if element.state == Button.State.HOVER:
                    element.SetState(Button.State.DEFAULT)
                if element.rect.collidepoint(*mouse.get_pos()):
                    element.IncrementTimer(self)
                    if element.state != Button.State.CLICKED: element.SetState(Button.State.HOVER)
                    break
                elif element.timer != 0: 
                    element.ResetTimer(self)
                    if element._tooltip_:
                        self.ui.remove(element._tooltip_)
                        self.ui.remove(element._tooltipOutline_)
                        element._tooltip_ = element._tooltipOutline_ = None
                        

    def UpdateRects(self) -> None:
        self.background.update_rect()
        for objs in self.ui:
            objs.update_rect()

        for layer in self.layers:
            layer.object.update_rect()


    def Launch(self):
        while not self.done:
            mouse.Update(self)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #1 - left click, 2 - middle click, 3 - right click, 4 - scroll up , 5 - scroll down
                    if event.button == 1:
                        self.CollisonCheck()
                    if event.button == 3:
                        mouse.Drag()
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse.Reset()
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_o]:
                        for layer in self.layers:
                            obj : Object = layer.object
                            print("id: ",obj.id,": ",obj.GetScreenCoordinates(), " - ", obj.GetScreenSize())
                    elif keys[pygame.K_DELETE]:
                        if mouse.selected != None:
                            self.layers.remove(mouse.selected)
                            self.layers.update()

            self.ButtonHoverCheck()

            self.screen.fill((65,65,65))            
            self.Draw()

            self.clock.tick(self.FPS)
            pygame.display.flip()
        pygame.display.quit() #used instead of pygame.quit() as another pygame instance may need to be launched
        root.quit() 

