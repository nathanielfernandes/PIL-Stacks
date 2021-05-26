import tkinter
import pygame
from pygame.mouse import get_pos
from pygame.transform import scale
import os
from src.pil_stacks.PIL_Stacks import Stack
from src.pil_stacks.Layers import Text, Img
from src.pil_stacks.Layers import Color as ColorLayer
from PIL import ImageFont, Image

from tkinter import (
    BooleanVar,
    Checkbutton,
    simpledialog,
    Tk,
    Label,
    Entry,
    Scale,
    StringVar,
    OptionMenu,
    colorchooser,
)
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo, showerror

RESIZE_CIRCLE_RADIUS = 6
WINDOW_SIZE = (1600, 900)
####################################################
# helper methods and classes


# Directory constants
ASSETS_DIRECTORY = (
    "src/pil_stacks/Assets"  # currently uses relative directory, change if neccessary
)
FONT_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "base_font.ttf")
EDITOR_ICON_PATH = os.path.join(
    ASSETS_DIRECTORY, "Layout", "Tools", "AddObjectButton", "add_1.png"
)
EDITOR_ICON = pygame.image.load(EDITOR_ICON_PATH)


root = Tk()
root.withdraw()
root.iconphoto(True, tkinter.PhotoImage(file=EDITOR_ICON_PATH))


pygame.init()

# preloading fonts with varying sizes
font = pygame.font.Font(FONT_DIRECTORY, 16)
font_L = pygame.font.Font(FONT_DIRECTORY, 20)
font_XL = pygame.font.Font(FONT_DIRECTORY, 30)


def AskForValue(title, question, initialvalue = ""):
    return simpledialog.askstring(title, question, parent=root, initialvalue=initialvalue)


def AskForNewLayer(editing_existing=False, existing_obj=None):
    return NewLayerPopup(root,editing_existing, existing_obj).GetValues()


class NewLayerPopup(simpledialog.Dialog):
    def __init__(self, parent, editing_existing=False, existing_obj=None) -> None:
        self.editing_existing = editing_existing
        self.existing_obj : Object = existing_obj
        super().__init__(parent, title="New Layer")

    def body(self, master):
        self._master = master

        self.preview = None
        self.type = StringVar(name="type")
        self.type.set("Image")
        if not self.editing_existing:   
            Label(self._master, text="Type: ").grid(column=0)
            OptionMenu(master, self.type, "Image", "Text", "Color").grid(
                column=0
            )
        self.name = StringVar(name="name")
        self.name.set("")

        self.font_size = StringVar(master, name="font_size", value="10")
        self.font = StringVar(master, name="font", value="default")

        Label(
            self._master, text="   Input Layer Name:"
        ).grid(column=0)
        Entry(master, textvariable=self.name).grid(column=0, pady=6)

        tkinter.Button(
            master=master, text="Layer Settings", command=self.LayerSettings
        ).grid(column=0, padx=4)

        self.is_constant = BooleanVar(name="is_constant")
        

        if self.editing_existing:
            type_ = {
                        Object.TYPE_NONE:  "None",
                        Object.TYPE_IMAGE: "Image",
                        Object.TYPE_TEXT:  "Text",
                        Object.TYPE_COLOR: "Color",
                    }[self.existing_obj.type]
            self.type.set(type_)
            self.name.set(self.existing_obj.id)
            if type_ == "Text":
                font_ = self.existing_obj.font.path
                if font_.lower() == "src/pil_stacks/Assets/base_font.ttf": font_ = "default"
                self.font.set(font_)
                self.font_size.set(str(self.existing_obj.font.size))
            self.is_constant.set(self.existing_obj.is_constant)
            if type_ == Object.TYPE_IMAGE:
                self.preview = self.existing_obj.__image__
            elif type_ == Object.TYPE_TEXT:
                self.preview = self.existing_obj.text
                print(self.preview)
            elif type_ == Object.TYPE_COLOR:
                self.preview = self.existing_obj.color
        return self


    def LayerSettings(self) -> None:
        class LayerSettings(simpledialog.Dialog):
            def __init__(self, parent) -> None:
                super().__init__(parent, title="Layer Settings")
            def body(self_, master) -> None:
                Label(master=master, text="constant: ").grid(row=0, column=0, padx=4)
                Checkbutton(master=master, variable=self.is_constant).grid(row=0,column=1)

                if self.type.get() == "Text":
                    Label(master=master, text="Font: ").grid(row=1, column=0, padx=4)
                    Entry(master=master, textvariable=self.font).grid(row=1,column=1)
                    Label(master=master, text="Font size: ").grid(row=2, column=0, padx=4)
                    Entry(master=master, textvariable=self.font_size).grid(row=2,column=1)
                tkinter.Button(master=master, text="Set Preview", command=self.SetPreview).grid(column=1)

        LayerSettings(self._master)

    def SetPreview(self) -> None:
        try:
            type = self.type.get()
        except:
            return
        if type == "Image":
            file_dir: str = askopenfilename()
            if (
                file_dir != None
                and file_dir.rstrip() != ""
                and (file_dir.endswith(".png") or file_dir.endswith(".jpg"))
            ):
                self.preview = pygame.image.load(file_dir)
        elif type == "Text":
            initial = ""
            if isinstance(self.preview, str):
                initial = self.preview
            self.preview = AskForValue("Text preview", "Enter Text: ", initial)
        elif type == "Color":
            self.preview = colorchooser.askcolor(title="Select Color")[0]

    def GetValues(self):
        class values:
            def __init__(
                self, type, name, preview_value, is_constant, font=None
            ) -> None:
                self.type = type
                self.name = name
                self.preview = preview_value
                self.is_constant = is_constant
                self.font = font

            def __repr__(self) -> str:
                return (
                    "type: "
                    + self.type.get()
                    + " - name: "
                    + self.name.get()
                    + " - preview: "
                    + self.preview
                )
        font_size = None
        font = None
        type_ = None
        try:
            type_ = self.type.get()
        except:
            return
        if  type_== "Text":
            try:
                font_size = int(self.font_size.get())
            except:
                showerror(message=f"Cannot convert {self.font_size.get()} into an integer")
                return None
            try:
                font = self.font.get()
                if font.lower() == "default": font = "src/pil_stacks/Assets/base_font.ttf"
                font : ImageFont.FreeTypeFont = ImageFont.truetype(font, font_size)
            except:
                showerror(message=f"Cannot find font {self.font.get()}")
                return None
        return values(
            self.type.get(),
            self.name.get(),
            self.preview,
            self.is_constant.get(),
            font,
        )


class FilterPopup(simpledialog.Dialog):
    def __init__(self, parent, previous_filters=None) -> None:
        if previous_filters == None:
            previous_filters = FilterPopup.Values()
        self.previous_filters = previous_filters
        super().__init__(parent, title="Filters")

    def body(self, master):
        self._master = master
        self.sharpness = self.CreateSlider("Sharpness", 0)
        self.sharpness.set(self.previous_filters.sharpness)
        self.contrast = self.CreateSlider("Contrast", 1)
        self.contrast.set(self.previous_filters.contrast)
        self.color = self.CreateSlider("Color", 2)
        self.color.set(self.previous_filters.color)
        self.brightness = self.CreateSlider("Brightness", 3)
        self.brightness.set(self.previous_filters.brightness)
        return self

    def CreateSlider(self, name, column):
        Label(self._master, text=name).grid(row=0, column=column)
        val = StringVar(name=name)  # an MVC-trick an indirect value-holder

        SCALE = Scale(
            self._master,
            variable=val,  # MVC-Model-Part value holder
            from_=1,  # MVC-Model-Part value-min-limit
            to=100.0,  # MVC-Model-Part value-max-limit
            length=200,  # MVC-Visual-Part layout geometry [px]
            digits=5,  # MVC-Visual-Part presentation trick
            resolution=0.01,  # MVC-Controller-Part stepping
        )
        SCALE.setvar(name, 1)
        ENTRY = Entry(self._master, textvariable=val)
        ENTRY.grid(row=3, column=column)
        SCALE.grid(row=2, column=column)
        return val

    class Values:
        def __init__(self, sharpness=1, contrast=1, color=1, brightness=1) -> None:
            self.sharpness = float(sharpness)
            self.contrast = float(contrast)
            self.color = float(color)
            self.brightness = float(brightness)

        def __repr__(self) -> str:
            return str([self.sharpness, self.contrast, self.color, self.brightness])

        def ToDict(self) -> dict:
            return {
                "sharpness": self.sharpness,
                "contrast": self.contrast,
                "color": self.color,
                "brightness": self.brightness,
            }

    def GetValues(self):
        return self.Values(
            self.sharpness.get(),
            self.contrast.get(),
            self.color.get(),
            self.brightness.get(),
        )


def aspect_scale(img, bx, by):
    """Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio.
    **FROM** : http://www.pygame.org/pcr/transform_scale/"""
    ix, iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx / float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by / float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx / float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    sx = int(sx)
    sy = int(sy)

    return pygame.transform.scale(img, (sx, sy))


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    YELLOW = (204, 255, 51)
    PURPLE = (153, 0, 204)
    BROWN = (153, 102, 51)
    PINK = (255, 0, 102)
    LIME = (108, 218, 0)


####################################################


class Camera:
    def __init__(self) -> None:
        self.x: float = 0
        self.y: float = 0
        self.zoom: float = 1.0

        self.Show_rects = True
        self.Show_names = False

    def Update(self) -> None:
        pass

    def FixCameraOffset(self) -> None:
        return
        self.x = WINDOW_SIZE[0] / 4 * (self.zoom - 1)
        self.y = WINDOW_SIZE[1] / 4 * (self.zoom - 1)

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
        return ((x - self.x) * camera.zoom, (y - self.y) * camera.zoom)

    def CameraToWorldCoordinates(self, x, y) -> tuple:
        return ((x + self.x) / camera.zoom, (y + self.y) / camera.zoom)

    def WorldToCameraSize(self, width, height) -> tuple:
        return (width * self.zoom, height * self.zoom)

    def CameraToWorldSize(self, width, height) -> tuple:
        return (width / self.zoom, height / self.zoom)


# Global Camera
camera = Camera()


class Mouse:
    def __init__(self) -> None:
        self.x: float = 0
        self.y: float = 0
        self.dragging: bool = False
        self.holding = None
        self.selected = None

        self.dragging_x = 0
        self.dragging_y = 0
        self.offset_x = 0
        self.offset_y = 0
        self.last_click_x = 0
        self.last_click_y = 0

        self.rotating = False
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
                new_size = camera.CameraToWorldSize(
                    (ms_coords[0] - hd_coords[0]), (ms_coords[1] - hd_coords[1])
                )
                obj.SetSize(*new_size)
            elif self.rotating:
                val = self.x - self.last_click_x
                val = min(359, val) if val > 0 else max(-359, val)
                self.holding.object.rotation = val
            else:
                obj = self.holding.object
                obj.SetPosition(
                    *camera.CameraToWorldCoordinates(
                        self.x - self.offset_x, self.y - self.offset_y
                    )
                )

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
        if self.holding != None:
            self.holding.object.show_rotation_degrees = False
            self.holding.object.PreviewFilters()
            self.holding.object.update_rect()
        self.holding = None
        self.rotating = False
        self.resizing = False
        self.dragging = False

    def ResetSelected(self) -> None:
        if self.selected != None:
            # Actual object
            obj = self.selected.object
            obj.rect_color = Color.WHITE
            obj.update_rect()

            # Layer
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


# Global Mouse
mouse = Mouse()


class Object:
    _id_count_ = 0
    TYPE_NONE = (
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "NoneLayer", "layer_0.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "NoneLayer", "layer_1.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "NoneLayer", "layer_2.png"
            )
        ),
    )
    TYPE_IMAGE = (
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "ImageLayer", "layer_image_0.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "ImageLayer", "layer_image_1.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "ImageLayer", "layer_image_2.png"
            )
        ),
    )
    TYPE_TEXT = (
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "TextLayer", "layer_text_0.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "TextLayer", "layer_text_1.png"
            )
        ),
        pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Layer", "TextLayer", "layer_text_2.png"
            )
        ),
    )
    TYPE_COLOR = TYPE_NONE

    def __init__(
        self,
        x=0,
        y=0,
        img=None,
        width=None,
        height=None,
        show_rect=True,
        collidable=True,
        resizable=True,
        keep_aspect_ratio=True,
        type=-1,
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.rotation = 0
        self.type = type
        self.width: int = width
        self.height: int = height
        self.__image__ = None
        self.show_rect: bool = show_rect
        self.show_rotation_degrees: bool = False
        self.collidable: bool = collidable
        self.hidden = False
        self.resizable: bool = resizable
        self.keep_aspect_ratio = keep_aspect_ratio

        if type == Object.TYPE_TEXT:
            self.text = ""
            self.font = None
        elif self.type == Object.TYPE_COLOR:
            self.color = None

        self.is_constant = False
        self.filters = FilterPopup.Values()

        self.id = Object._id_count_
        Object._id_count_ += 1

        if img != None and isinstance(img, str):
            img = pygame.image.load(img)
        self.image = img
        if self.image != None:
            if self.height != None and self.width != None:
                self.image = aspect_scale(self.image, self.width, self.height)
            else:
                self.width = self.image.get_width()
                self.height = self.image.get_height()

            self.__image__ = self.image.copy()
            self.image = self.image.convert_alpha()

        self.__original_image__ = None

        self.rect: pygame.Rect = pygame.Rect(1, 1, 1, 1)
        self.rect_color = Color.WHITE
        self.update_rect()

    def PreviewFilters(self) -> None:
        if self.image != None and self.__original_image__ != None:
            filters = self.filters.ToDict()
            filters["brightness"] = (filters["brightness"] + 99) / 100
            tmp = Img(
                "tmp",
                *self.GetScreenCoordinates(),
                *self.GetScreenSize(),
                self.rotation,
                filters,
            )
            _bytes, _size, _mode = tmp.__editorpreview__(
                content=Image.frombytes(
                    "RGBA",
                    self.__original_image__.get_size(),
                    pygame.image.tostring(self.__original_image__, "RGBA"),
                    "raw",
                )
            )
            self.__image__ = pygame.image.fromstring(_bytes, _size, "RGBA")
            self.apply_rotation()

    def SetName(self, name):
        self.id = name
        return self

    def SetWidth(self, width) -> None:
        self.width = max(0, width)
        self.update_rect()

    def SetHeight(self, height) -> None:
        self.height = max(0, height)
        self.update_rect()

    def SetSize(self, width, height) -> None:
        self.width = max(0, width)
        self.height = max(0, height)
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
            if self.GetRotationCircle().collidepoint(*mouse.get_pos()):
                mouse.rotating = True
                self.show_rotation_degrees = True
                return True
        self.show_rotation_degrees = False
        if self.rect.collidepoint(*mouse.get_pos()):
            mouse.resizing = False
            return True
        return False

    def apply_rotation(self) -> None:
        if self.__original_image__ != None:
            self.__image__ = pygame.transform.rotate(
                self.__image__, self.rotation * -1
            ).convert_alpha()
            self.image = self.__image__
            self.update_rect()

    def Colliding(self, editor, layer) -> None:
        if self.collidable == False:
            return
        mouse.SetClicked(layer)

    def Draw(self, screen) -> None:
        if self.hidden:
            return
        if self.image != None:
            screen.blit(self.image, self.GetScreenCoordinates())
        if self.show_rect and camera.Show_rects:
            pygame.draw.rect(screen, self.rect_color, self.rect, width=3)
            pygame.draw.circle(
                screen,
                Color.RED,
                self.BottomRight(),
                camera.zoom * RESIZE_CIRCLE_RADIUS,
                width=0,
            )
            pygame.draw.circle(
                screen,
                Color.BLUE,
                self.TopMid(),
                camera.zoom * RESIZE_CIRCLE_RADIUS,
                width=0,
            )
            if self.show_rotation_degrees:
                Text = font_XL.render(str(self.rotation), 1, Color.BLUE)
                txt_coords = self.TopMid()
                screen.blit(Text, (txt_coords[0] - 8, txt_coords[1] - 35))

        if self.show_rect and camera.Show_names:
            if len(str(self.id)) > 16:
                name = font.render(
                    str(self.id)[: (16 - len(str(self.id)))] + "...", 1, Color.BLACK
                )
            else:
                name = font.render(str(self.id), 1, Color.BLACK)
            name_coords = self.GetScreenCoordinates()
            name_coords = (
                name_coords[0] + self.GetScreenSize()[0] / 2 - 5 * len(str(self.id)),
                name_coords[1] + self.GetScreenSize()[1] / 2.5,
            )
            screen.blit(name, name_coords)

    def update_rect(self) -> None:
        self.rect.update(*self.GetScreenCoordinates(), *self.GetScreenSize())
        
        if self.type == Object.TYPE_TEXT and self.text != None and self.font != None:
            from src.pil_stacks.Layers import Text
            tmp = Text(
                "tmp",
                self.font,
                (0,0,0),
                "left",
                *self.GetScreenCoordinates(),
                *self.GetScreenSize(),
                self.rotation,
            )
            _bytes, _size, _mode = tmp.__editorpreview__(
                content=self.text
            )
            self.__image__ = self.image = pygame.image.fromstring(_bytes, _size, "RGBA") 
        if (
            self.type == Object.TYPE_COLOR
            and self.color != None
            and self.__image__ == None
        ):
            self.__original_image__ = pygame.Surface(self.GetScreenSize())
            pygame.draw.rect(
                self.__original_image__,
                self.color,
                pygame.Rect(0, 0, *self.GetScreenSize()),
            )
            self.__image__ = self.image = self.__original_image__.copy()
        elif self.image != None:
            if self.keep_aspect_ratio:
                self.image = aspect_scale(
                    self.__image__.convert_alpha(), *self.GetScreenSize()
                )
            else:
                size = self.GetScreenSize()
                size = (int(size[0]), int(size[1]))
                self.image = scale(self.__image__.convert_alpha(), size)

    def GetScreenCoordinates(self) -> tuple:
        return camera.WorldToCameraCoordinates(self.x, self.y)

    def GetResizeCircle(self):
        coords = self.BottomRight()
        return pygame.Rect(
            coords[0] - camera.zoom * RESIZE_CIRCLE_RADIUS,
            coords[1] - camera.zoom * RESIZE_CIRCLE_RADIUS,
            camera.zoom * RESIZE_CIRCLE_RADIUS * 2,
            camera.zoom * RESIZE_CIRCLE_RADIUS * 2,
        )

    def GetRotationCircle(self):
        coords = self.TopMid()
        return pygame.Rect(
            coords[0] - camera.zoom * RESIZE_CIRCLE_RADIUS,
            coords[1] - camera.zoom * RESIZE_CIRCLE_RADIUS,
            camera.zoom * RESIZE_CIRCLE_RADIUS * 2,
            camera.zoom * RESIZE_CIRCLE_RADIUS * 2,
        )

    def BottomRight(self) -> tuple:
        size = (self.width, self.height)
        return camera.WorldToCameraCoordinates(self.x + size[0], self.y + size[1])

    def TopMid(self) -> tuple:
        size = (self.width, self.height)
        return camera.WorldToCameraCoordinates(self.x + (size[0] / 2), self.y)

    def GetScreenSize(self) -> tuple:
        return camera.WorldToCameraSize(self.width, self.height)

    def __repr__(self) -> str:
        if self.hidden:
            return f"name: {self.id} x: {self.x:.0f} y: {self.y:.0f} [HIDDEN]"
        return f"name: {self.id} x: {self.x:.0f} y: {self.y:.0f}"


class UI_Element(Object):
    def __init__(self, color=Color.WHITE, fill_width=1, **kwargs) -> None:
        self.color = color
        self.fill_width = fill_width
        super().__init__(**kwargs)

    def GetScreenCoordinates(self) -> tuple:
        return (self.x, self.y)

    def Draw(self, screen) -> None:
        if self.hidden:
            return
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
        self.rect.update(*self.GetScreenCoordinates(), *self.GetScreenSize())
        if self.image != None or self.__image__ != None:
            if self.keep_aspect_ratio:
                self.image = aspect_scale(
                    self.__image__.convert_alpha(), *self.GetScreenSize()
                )
            else:
                size = self.GetScreenSize()
                size = (int(size[0]), int(size[1]))
                self.image = scale(self.__image__.convert_alpha(), size)


class Button(UI_Element):
    class State:
        DEFAULT = 0
        HOVER = 1
        CLICKED = 2

    def __init__(self, **kwargs) -> None:
        self.state = Button.State.DEFAULT
        self.timer = 0
        self._tooltip_ = None
        self._tooltipOutline_ = None
        self.Description = "Default button"
        super().__init__(**kwargs)

    def IncrementTimer(self, editor) -> None:
        if editor.clock.get_fps() == 0:
            return
        self.timer += 1 / editor.clock.get_fps()
        if self.timer > 1 and self._tooltip_ == None:
            self._tooltip_ = UI_Element(
                x=self.x + 65,
                y=self.y,
                color=(95, 95, 95),
                fill_width=0,
                width=100,
                height=100,
            )
            self._tooltipOutline_ = UI_Element(
                x=self.x + 63,
                y=self.y - 2,
                color=Color.BLACK,
                fill_width=2,
                width=102,
                height=102,
            )
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
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "AddObjectButton", "add_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "AddObjectButton", "add_1.png"
            )
        )
        self.clicked = None  # pygame.image.load(os.path.join(ASSETS_DIRECTORY, "Layout", "Tools","AddObjectButton","add_2.png"))
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        values = AskForNewLayer()
        if values == None: return
        name = values.name
        type = values.type
        if values == None or name == None or len(name.rstrip()) == 0 or not editor.layers.IsUnique(name):
            self.SetState(Button.State.DEFAULT)
            self.update_rect()
            if values == None:
                showerror("Error", "layer was unable to initialize properly!")
                return
            showerror("Error", "the name must not be empty or already exist!")
            return
        _type = {
            "None": Object.TYPE_NONE,
            "Image": Object.TYPE_IMAGE,
            "Text": Object.TYPE_TEXT,
            "Color": Object.TYPE_COLOR,
        }[type]
        width = 200
        height = 200
        if _type == Object.TYPE_IMAGE and values.preview != None:
            width, height = values.preview.get_size()
        obj = Object(
            650, 350, width=width, height=height, keep_aspect_ratio=False, type=_type
        )
        obj.id = name
        if obj.type == Object.TYPE_IMAGE and values.preview != None:
            obj.__image__ = obj.image = values.preview
            obj.__original_image__ = values.preview.copy()
        elif obj.type == Object.TYPE_TEXT:
            obj.text = values.preview
            obj.font = values.font
        elif obj.type == Object.TYPE_COLOR:
            obj.color = values.preview
        obj.update_rect()
        obj.is_constant = values.is_constant
        editor.layers.append(obj, obj.type)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()


class ShowRectButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "OutlineButton", "outline_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "OutlineButton", "outline_1.png"
            )
        )
        self.clicked = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "OutlineButton", "outline_2.png"
            )
        )
        super().__init__(img=self.clicked, **kwargs)
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
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "ShowNameButton", "names_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "ShowNameButton", "names_1.png"
            )
        )
        self.clicked = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "ShowNameButton", "names_2.png"
            )
        )
        super().__init__(img=self.default, **kwargs)
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
        self.default = pygame.image.load(
            os.path.join(ASSETS_DIRECTORY, "Layout", "Tools", "UpButton", "up_0.png")
        )
        self.hover = pygame.image.load(
            os.path.join(ASSETS_DIRECTORY, "Layout", "Tools", "UpButton", "up_1.png")
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            if len(editor.layers.layers) == 1:
                return

            layers: list = editor.layers.layers

            index = layers.index(mouse.selected)
            if index == 0:
                return
            layers.insert(index - 1, layers.pop(index))
            editor.layers.update()


# a whole new class is probably not neccessary
class MoveDownButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "DownButton", "Down_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "DownButton", "Down_1.png"
            )
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            layers: list = editor.layers.layers
            if len(layers) == 1:
                return

            index = layers.index(mouse.selected)
            if index == len(layers) - 1:
                return
            layers.insert(index + 1, layers.pop(index))
            editor.layers.update()


class EditButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "EditButton", "edit_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "EditButton", "edit_1.png"
            )
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        self.update_rect()
        if mouse.selected == None:
            self.update_rect()
            return

        values = AskForNewLayer(editing_existing=True, existing_obj=mouse.selected.object)
        if values == None: return
        name = values.name
        if values == None or name == None or len(name.rstrip()) == 0 or not editor.layers.IsUnique(name, ignore=[mouse.selected.id]):
            self.SetState(Button.State.DEFAULT)
            self.update_rect()
            if values == None:
                showerror("Error", "layer was unable to initialize properly!")
                return
            showerror("Error", "the name must not be empty or already exist!")
            return
        mouse.selected.id = name
        mouse.selected.object.id = name
        obj : Object = mouse.selected.object
        if obj.type == Object.TYPE_IMAGE and values.preview != None:
            obj.__image__ = obj.image = values.preview
            obj.__original_image__ = values.preview.copy()
        elif obj.type == Object.TYPE_TEXT:
            obj.text = values.preview
            obj.font = values.font
        elif obj.type == Object.TYPE_COLOR:
            obj.color = values.preview
            obj.__image__ = None
        elif obj.type == Object.TYPE_IMAGE:
            if values.preview != None: 
                obj.__image__ = values.preview
                obj.SetSize(*values.preview.get_size())
        obj.is_constant = values.is_constant
        mouse.selected.update_rect()
        obj.update_rect()
        self.SetState(Button.State.DEFAULT)
        self.update_rect()


class FilterButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "FilterButton", "filters_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "FilterButton", "filters_1.png"
            )
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        if mouse.selected:
            vals = FilterPopup(
                root, previous_filters=mouse.selected.object.filters
            ).GetValues()
            mouse.selected.object.filters = vals
            mouse.selected.object.PreviewFilters()


class SetBackgroundButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY,
                "Layout",
                "Tools",
                "SetBackgroundButton",
                "preview_0.png",
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY,
                "Layout",
                "Tools",
                "SetBackgroundButton",
                "preview_1.png",
            )
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        file_dir = askopenfilename()
        if (
            file_dir != None
            and file_dir.rstrip() != ""
            and (file_dir.endswith(".png") or file_dir.endswith(".jpg"))
        ):
            editor.SetBackground(pygame.image.load(file_dir))
            showinfo("Successful", "New background image loaded!")
        else:
            showerror("Error", "invalid image file")


class SaveTemplateButton(Button):
    def __init__(self, **kwargs) -> None:
        self.default = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "SaveButton", "save_0.png"
            )
        )
        self.hover = pygame.image.load(
            os.path.join(
                ASSETS_DIRECTORY, "Layout", "Tools", "SaveButton", "save_1.png"
            )
        )
        self.clicked = None
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

    def Colliding(self, editor) -> None:
        editor.ToStack().export_template()
        showinfo("successful", "saved template. ")


class LayerContainer(UI_Element):
    def __init__(self, color=Color.WHITE, fill_width=1, **kwargs) -> None:
        super().__init__(color=color, fill_width=fill_width, **kwargs)
        self.show_rect = False
        self.layers = []
        self.buttons = []
        self.editor = None

    def IsUnique(self, name: str, ignore=[]) -> bool:
        layer: Layer
        for layer in self.layers:
            if name in ignore: continue
            if layer.object.id.lower() == name.lower():
                return False
        return True

    def Draw(self, screen) -> None:
        if self.hidden:
            return
        super().Draw(screen)

        layer: Layer
        for layer in self.layers:
            layer.Draw(screen)

    def __len__(self) -> int:
        return len(self.layers)

    def GetLayerCount(self) -> int:
        return self.__len__()

    def append(self, obj, type) -> None:
        offset_x = (self.width - 330) / 2
        offset_y = 40
        spacing_y = 13.75
        layer = Layer(
            color=Color.BLACK,
            fill_width=1,
            type=type,
            show_rect=False,
            x=self.x + offset_x,
            y=self.y
            + 31 * self.GetLayerCount()
            + spacing_y * (self.GetLayerCount() + 1)
            + offset_y,
            width=400 * 0.83,
            height=50 * 0.83,
            keep_aspect_ratio=False,
        )
        layer.ShowButton = __Layer_Show_Button__(
            x=layer.x - 3, y=layer.y, width=50 * 0.83, height=50 * 0.83, show_rect=False
        )
        layer.ShowButton.layer = layer
        self.buttons.append(layer.ShowButton)

        layer.object = obj
        layer.SetName(obj.id)
        self.layers.append(layer)

    def update(self):
        """(->)"""
        layer: Layer
        offset_x = (self.width - 330) / 2
        offset_y = 40
        spacing_y = 13.75
        for index, layer in enumerate(self.layers):
            x = self.x + offset_x
            y = self.y + 31 * index + spacing_y * (index + 1) + offset_y
            layer.SetPosition(x, y)
            layer.ShowButton.SetPosition(x - 3, y)
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
    __DEFAULT__ = pygame.image.load(
        os.path.join(ASSETS_DIRECTORY, "Layout", "Layer", "eye_0.png")
    )
    __HOVER__ = pygame.image.load(
        os.path.join(ASSETS_DIRECTORY, "Layout", "Layer", "eye_1.png")
    )
    __CLICKED__ = pygame.image.load(
        os.path.join(ASSETS_DIRECTORY, "Layout", "Layer", "eye_2.png")
    )

    def __init__(self, **kwargs) -> None:
        self.default = __Layer_Show_Button__.__DEFAULT__
        self.hover = __Layer_Show_Button__.__HOVER__
        self.clicked = __Layer_Show_Button__.__CLICKED__
        super().__init__(img=self.default, **kwargs)
        self.SetState(Button.State.DEFAULT)
        self.update_rect()
        self.layer = None

    def Colliding(self, editor) -> None:
        state = self.layer.object.hidden
        self.layer.object.hidden = not state
        if state:
            self.SetState(Button.State.DEFAULT)
        else:
            self.SetState(Button.State.CLICKED)
            self.layer.SetState(Button.State.DEFAULT)


class Layer(Button):
    def __init__(
        self, color=Color.BLACK, fill_width=1, type=Object.TYPE_NONE, **kwargs
    ) -> None:
        self.default, self.hover, self.clicked = type
        super().__init__(color=color, fill_width=fill_width, **kwargs)
        self.rect_color = color
        self.object: Object = None
        self.SetState(Button.State.DEFAULT)
        self.update_rect()

        self.ShowButton: __Layer_Show_Button__ = None
        self.ValueButton = None

    def Colliding(self, editor) -> None:
        if self.collidable == False or self.object.hidden:
            return
        mouse.SetClicked(self, holding=False)

    def Draw(self, screen) -> None:
        if self.hidden:
            return
        super().Draw(screen=screen)
        self.ShowButton.Draw(screen=screen)

        if self.show_rect:
            pygame.draw.rect(screen, self.rect_color, self.rect, width=self.fill_width)
        name = font_L.render(str(self.id), 1, Color.WHITE)
        name_coords = self.GetScreenCoordinates()
        if len(str(self.id)) > 16:
            name = font_L.render(
                str(self.id)[: (16 - len(str(self.id)))] + "...", 1, Color.WHITE
            )
        name_coords = (
            name_coords[0] + 55,
            name_coords[1] + self.GetScreenSize()[1] / 5,
        )
        screen.blit(name, name_coords)

    def __repr__(self) -> str:
        return self.object.__repr__()


class Editor:
    """An editor object which has a Launch() method to launch the editor window.\n Once Launch() is called a pygame instance will run and lock the rest of the code until the window is closed and a\n Additional options can be enabled by setting the properties to true before calling the Launch() method, such as [show_fps] and [__debug_info__]."""

    def __init__(self, name: str, Background: str, Background_as_constant=True) -> None:
        self.name = name
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_icon(EDITOR_ICON)
        pygame.display.set_caption("Template Editor")
        self.FPS = 1000  # change if neccessary, FPS doesn't seem to show if there is no fps cap. Setting it to 1000 ensures it will run fast but still properly display fps.
        self.show_fps = False
        self.__debug_info__ = False
        self.done = False
        self.clock = pygame.time.Clock()

        self.Background_as_constant = Background_as_constant

        bg_size = (WINDOW_SIZE[0] - 100, WINDOW_SIZE[1] - 100)
        self.__original_background__ = pygame.image.load(Background)
        self.background = Object(
            x=220,
            y=50,
            img=aspect_scale(self.__original_background__, *bg_size),
            show_rect=False,
        )

        self.layers = LayerContainer(
            x=1255,
            y=2,
            width=413 * 0.83,
            height=1080 * 0.83,
            keep_aspect_ratio=False,
            img=os.path.join(ASSETS_DIRECTORY, "Layout", "ui_right.png"),
        )  # Object(x=20,y=20,width=200,height=200,img="cat.jpg")
        self.tools = LayerContainer(
            x=2,
            y=2,
            width=80 * 0.83,
            height=1080 * 0.83,
            keep_aspect_ratio=False,
            img=os.path.join(ASSETS_DIRECTORY, "Layout", "ui_left.png"),
        )
        self.layers.editor = self
        self.ui = [
            SaveTemplateButton(
                x=6,
                y=78,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            SetBackgroundButton(
                x=6,
                y=123,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            AddObjectButton(
                x=6,
                y=180,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            ShowRectButton(
                x=6,
                y=240,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            ShowNameButton(
                x=6,
                y=285,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            EditButton(
                x=6,
                y=345,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            FilterButton(
                x=6,
                y=390,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            MoveUpButton(
                x=6,
                y=435,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            MoveDownButton(
                x=6,
                y=480,
                width=70 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
            ),
            UI_Element(
                x=14,
                y=12,
                width=50 * 0.84,
                height=50 * 0.84,
                keep_aspect_ratio=False,
                show_rect=False,
                img=os.path.join(ASSETS_DIRECTORY, "Layout", "Tools", "icon.png"),
            ),
            self.layers,
        ]
        # UI_Element(x=960,y=13,width=233,height=879,color=Color.BLACK, fill_width=8, collidable=False)]

    def Draw(self) -> None:
        self.background.Draw(self.screen)

        if self.show_fps:
            Text = font_XL.render(
                "[fps] " + str(int(self.clock.get_fps())), 1, Color.WHITE
            )
            self.screen.blit(Text, (80, 5))
        if self.__debug_info__:

            Text = font_XL.render("[Selected] " + str(mouse.selected), 1, Color.WHITE)
            self.screen.blit(Text, (80, 35))
            Text = font_XL.render(
                f"[Camera] x: {camera.x:.0f} y: {camera.y:.0f}", 1, Color.WHITE
            )
            self.screen.blit(Text, (80, 65))
            Text = font_XL.render(
                f"[Mouse] x: {mouse.x:.0f} y: {mouse.y:.0f}", 1, Color.WHITE
            )
            self.screen.blit(Text, (80, 95))

        obj: Layer
        for obj in self.layers[::-1]:
            obj.object.Draw(self.screen)

        self.tools.Draw(self.screen)

        for obj in self.ui:
            obj.Draw(self.screen)

        self.layers.Draw(self.screen)

    def CollisonCheck(self) -> None:
        objs: UI_Element
        for objs in self.layers.buttons + self.layers.layers:
            if objs.hidden:
                continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self)
                    return

        objs: UI_Element
        for objs in self.ui:
            if objs.hidden:
                continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self)
                    return

        layer: Layer
        tmp = self.layers.layers
        if mouse.selected != None:
            tmp = [mouse.selected] + tmp
        for layer in tmp:
            objs: Object = layer.object
            if objs.hidden:
                continue
            if objs.collidable:
                if objs.CheckCollision():
                    objs.Colliding(self, layer)
                    return

        mouse.ResetSelected()

    def ButtonHoverCheck(self) -> None:
        self.__hover_check__(self.ui)
        self.__hover_check__(self.layers.buttons + self.layers.layers)

    def __hover_check__(self, list) -> None:
        element: Button
        for element in list:
            if element.hidden:
                continue
            if isinstance(element, Button):
                if element.state == Button.State.HOVER:
                    element.SetState(Button.State.DEFAULT)
                if element.rect.collidepoint(*mouse.get_pos()):
                    element.IncrementTimer(self)
                    if element.state != Button.State.CLICKED:
                        element.SetState(Button.State.HOVER)
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

    def SetBackground(self, img) -> None:
        bg_size = (WINDOW_SIZE[0] - 100, WINDOW_SIZE[1] - 100)
        self.__original_background__ = img.convert_alpha()
        self.background = Object(
            x=220,
            y=50,
            img=aspect_scale(self.__original_background__, *bg_size),
            show_rect=False,
        )
        self.background.update_rect()

    def Launch(self) -> Stack:
        while not self.done:
            mouse.Update(self)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse.last_click_x, mouse.last_click_y = mouse.x, mouse.y
                    # 1 - left click, 2 - middle click, 3 - right click, 4 - scroll up , 5 - scroll down
                    if event.button == 1:
                        self.CollisonCheck()
                    elif event.button == 3:
                        mouse.Drag()
                    else:
                        mouse.Reset()
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse.Reset()
                elif event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_o]:
                        for layer in self.layers:
                            obj: Object = layer.object
                            print(
                                "id: ",
                                obj.id,
                                ": ",
                                obj.GetScreenCoordinates(),
                                " - ",
                                obj.GetScreenSize(),
                            )
                    elif keys[pygame.K_DELETE]:
                        if mouse.selected != None:
                            self.layers.remove(mouse.selected)
                            self.layers.update()

            self.ButtonHoverCheck()

            self.screen.fill((65, 65, 65))
            self.Draw()

            self.clock.tick(self.FPS)
            pygame.display.flip()
        pygame.display.quit()  # used instead of pygame.quit() as another pygame instance may need to be launched
        root.quit()
        return self.ToStack()

    def Close(self) -> None:
        """WILL **delete** itself and close pygame engine.\n only use if you are certain no more editors will be launched during the runtime"""
        pygame.quit()
        del self

    def ToStack(self) -> Stack:

        font = ImageFont.truetype(FONT_DIRECTORY, 16)
        font_L = ImageFont.truetype(FONT_DIRECTORY, 20)
        font_XL = ImageFont.truetype(FONT_DIRECTORY, 30)

        base_image = Image.frombytes(
            "RGBA",
            self.__original_background__.get_size(),
            pygame.image.tostring(self.__original_background__, "RGBA"),
            "raw",
        )
        scene = Stack(
            name=self.name, base=base_image, constant_base=self.Background_as_constant
        )
        original_bg = self.__original_background__
        aspect_scaled_bg = self.background.image
        scale_factor = (
            original_bg.get_size()[0] / aspect_scaled_bg.get_size()[0],
            original_bg.get_size()[1] / aspect_scaled_bg.get_size()[1],
        )

        layer: Layer
        for layer in self.layers.layers[::-1]:
            obj = layer.object
            obj_coords = obj.GetScreenCoordinates()
            bg_coords = self.background.GetScreenCoordinates()
            coords = (
                int((obj_coords[0] - bg_coords[0]) * scale_factor[0]),
                int((obj_coords[1] - bg_coords[1]) * scale_factor[1]),
            )

            obj_size = obj.GetScreenSize()
            size = (
                int(obj_size[0] * scale_factor[0]),
                int(obj_size[1] * scale_factor[1]),
            )

            constant = None

            if obj.is_constant == True:
                if obj.type == Object.TYPE_IMAGE:
                    constant = Image.frombytes(
                        "RGBA",
                        obj.__original_image__.get_size(),
                        pygame.image.tostring(obj.__original_image__, "RGBA"),
                        "raw",
                    )
                elif obj.type == Object.TYPE_TEXT:
                    constant = obj.text
                elif obj.type == Object.TYPE_COLOR:
                    constant = obj.color + (255,)

            if obj.type == Object.TYPE_IMAGE:
                scene.add_layer(
                    Img(
                        obj.id,
                        *coords,
                        *size,
                        rotation=obj.rotation,
                        filters=obj.filters.ToDict(),
                        constant=constant,
                    )
                )
            elif obj.type == Object.TYPE_TEXT:
                scene.add_layer(
                    Text(
                        name=obj.id,
                        font=obj.font,
                        color=(0, 0, 0),
                        x=coords[0],
                        y=coords[1],
                        width=size[0],
                        height=size[1],
                        rotation=obj.rotation,
                        constant=constant,
                    )
                )
            elif obj.type == Object.TYPE_COLOR:
                scene.add_layer(
                    ColorLayer(
                        name=obj.id,
                        x=coords[0],
                        y=coords[1],
                        width=size[0],
                        height=size[1],
                        rotation=obj.rotation,
                        constant=constant,
                    )
                )
        return scene
