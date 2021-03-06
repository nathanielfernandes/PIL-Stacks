from textwrap import TextWrapper
from abc import abstractmethod
from typing import List, Dict, Union, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageEnhance
from copy import copy


class Layer:
    def __init__(
        self,
        name: str,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        rotation: int = 0,
        filters: Dict = {
            "sharpness": 1.0,
            "contrast": 1.0,
            "color": 1.0,
            "brightness": 1.0,
        },
        _type: str = "layer",
        constant: Union[str, Image.Image] = None,
    ) -> None:
        self.name = name.replace(" ", "_")
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rotation = rotation
        self.filters = filters
        self.type = _type

        if isinstance(constant, str) and _type == "image":
            constant = Layer.open_image(constant)

        self.constant = constant

    @abstractmethod
    def draw(self, base: Image.Image, content: Union[str, Image.Image]) -> None:
        """Override this"""
        raise NotImplementedError()

    @staticmethod
    def pack_filters(
        sharpness: float = 1.0,
        contrast: float = 1.0,
        color: float = 1.0,
        brightness: float = 1.0,
    ):
        return {
            "sharpness": sharpness,
            "contrast": contrast,
            "color": color,
            "brightness": brightness,
        }

    @staticmethod
    def open_image(path: str) -> Image.Image:
        image = Image.open(path)
        if image.format == "GIF":
            image.seek(0)
        image = image.convert("RGBA")

        return image

    @staticmethod
    def apply_filters(
        image: Image.Image,
        filters: Dict = {
            "sharpness": 1.0,
            "contrast": 1.0,
            "color": 1.0,
            "brightness": 1.0,
        },
    ) -> Image.Image:
        M = Layer(name="", filters=filters)

        return M.__apply_filters__(image)

    def __apply_filters__(self, image: Image.Image) -> Image.Image:
        if self.type != "text" and max([self.filters[f] != 1.0 for f in self.filters]):
            sharpness = self.filters.get("sharpness")
            contrast = self.filters.get("contrast")
            color = self.filters.get("color")
            brightness = self.filters.get("brightness")

            image = image.convert("RGB")

            if sharpness and sharpness >= 0.0 and sharpness != 1.0:
                image = ImageEnhance.Sharpness(image).enhance(sharpness)
            if contrast and contrast >= 0.0 and contrast != 1.0:
                image = ImageEnhance.Contrast(image).enhance(contrast)
            if color and color >= 0.0 and color != 1.0:
                image = ImageEnhance.Color(image).enhance(color)
            if brightness and brightness >= 0.0 and brightness != 1.0:
                image = ImageEnhance.Brightness(image).enhance(brightness)

            image = image.convert("RGBA")

        return image

    @staticmethod
    def paste_image(
        base: Image.Image,
        image: Image.Image,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        rotation: int = 0,
        filters: Dict = {
            "sharpness": 1.0,
            "contrast": 1.0,
            "color": 1.0,
            "brightness": 1.0,
        },
    ) -> None:
        M = Layer(
            name="",
            x=x,
            y=y,
            width=width,
            height=height,
            rotation=rotation,
            filters=filters,
        )
        M.__paste_image__(base, image)

    # @staticmethod
    def __paste_image__(self, base: Image.Image, image: Image.Image) -> None:
        image = self.__apply_filters__(image)

        w = self.width if self.width is not None else image.size[0]
        h = self.height if self.height is not None else image.size[1]

        image = image.resize((w, h))

        if self.rotation != 0:
            image = image.rotate(self.rotation * -1, expand=1).resize((w, h))

        base.paste(image, (self.x, self.y), image)

    def __editorpreview__(self, content: Union[str, Image.Image]):
        if content is None:
            content = self.constant.copy()

        if isinstance(content, str):
            if self.type == "text":
                content = self.create_text(content)
            else:
                content = Layer.open_image(content)

        content = self.__apply_filters__(content)

        return content.tobytes(), content.size, content.mode

    def __getbakedlayer__(
        self,
        base: Union[str, Image.Image, Tuple[int, int]],
        content: Union[str, Image.Image] = None,
    ) -> Image.Image:
        if isinstance(base, str):
            image = Layer.open_image(base)
        elif isinstance(base, tuple):
            image = Color.create_blank(width=base[0], height=base[1])
        else:
            image = base

        if content is None:
            content = copy(self.constant)

        self.draw(base=image, content=content)
        return image

    def __asdict__(self) -> dict:
        _dict = copy(self.__dict__)
        if _dict["type"] == "text":
            _dict["font"] = {
                "name": _dict["font"].path,
                "size": _dict["font"].size,
            }
        if _dict["constant"] is not None:
            _dict["constant"] = f"{_dict['name']}_CONSTANT.png"

        return _dict


class Text(Layer):
    def __init__(
        self,
        name: str,
        font: ImageFont.FreeTypeFont,
        color: Tuple[int, int, int] = (0, 0, 0),
        align: str = "left",
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        rotation: int = 0,
        constant: Union[str, Image.Image] = None,
    ) -> None:
        super().__init__(
            name, x, y, width, height, rotation, _type="Text", constant=constant
        )

        self.type = "text"
        self.font = font
        self.color = color
        self.align = align

    @staticmethod
    def wrap(text: str, width: int) -> str:
        word_list = TextWrapper(width=width).wrap(text=text)
        text_new = ""
        for ii in word_list[:-1]:
            text_new += ii + "\n"
        text_new += word_list[-1]

        return text_new

    def create_text(self, content: str) -> None:
        placeholder_draw = ImageDraw.Draw(Image.new("RGBA", (0, 0), (0, 0, 0, 0)))

        w, h = self.font.getsize_multiline("A\ng")
        content = Text.wrap(content, self.width // w)

        text_size = placeholder_draw.textsize(content, self.font)

        txtImage = Image.new("RGBA", (text_size), (0, 0, 0, 0))

        draw = ImageDraw.Draw(txtImage)
        draw.text(
            xy=(0, 0),
            text=content,
            fill=self.color,
            font=self.font,
            align=self.align,
        )

        return txtImage.crop((0, 0, self.width, self.height))

    def draw(self, base: Image.Image, content: str = None) -> None:
        if content is None:
            content = self.constant

        self.__paste_image__(base=base, image=self.create_text(content))


class Img(Layer):
    def __init__(
        self,
        name: str,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        rotation: int = 0,
        filters: Dict = {
            "sharpness": 1.0,
            "contrast": 1.0,
            "color": 1.0,
            "brightness": 1.0,
        },
        constant: Union[str, Image.Image] = None,
    ) -> None:
        super().__init__(
            name, x, y, width, height, rotation, filters, "image", constant=constant
        )

    def draw(self, base: Image.Image, content: Union[str, Image.Image] = None) -> None:
        if content is not None:
            if isinstance(content, str):
                content = Layer.open_image(content)
        else:
            content = self.constant.copy()

        self.__paste_image__(base, content)


class Color(Layer):
    def __init__(
        self,
        name: str,
        x: int = 0,
        y: int = 0,
        width: int = None,
        height: int = None,
        rotation: int = 0,
        constant: Tuple[int, int, int, int] = None,
    ) -> None:
        super().__init__(
            name,
            x,
            y,
            width,
            height,
            rotation,
            _type="color",
            constant=constant,
        )

    @staticmethod
    def fixcolor(color: Tuple) -> Tuple[int, int, int, int]:
        l = len(color)
        while l < 4:
            color += (0,) if l != 3 else (255,)
            l += 1
        return color

    @staticmethod
    def create_color(
        width: int = 0,
        height: int = 0,
        color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    ) -> Image.Image:
        return Image.new("RGBA", (width, height), Color.fixcolor(color))

    @staticmethod
    def create_blank(width: int = 0, height: int = 0) -> Image.Image:
        return Image.new("RGBA", (width, height), (0, 0, 0, 0))

    def draw(
        self, base: Image.Image, content: Tuple[int, int, int, int] = None
    ) -> None:
        if content is None:
            content = self.constant
        self.__paste_image__(
            base=base,
            image=Color.create_color(
                width=self.width, height=self.height, color=content
            ),
        )
