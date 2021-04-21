import json, os, shutil
from typing import List, Dict, Union, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageSequence, ImageEnhance
from Layers import Media, Text, Img
from zipfile import ZipFile
from io import BytesIO


class Template:
    def import_template(self, template: Union[str]) -> None:
        name = os.path.basename(template)
        path = template.replace(name, "")

        if template.endswith(".zip"):
            path = template.replace(".zip", "") + "/"
            self.path = path

            try:
                os.mkdir(path)
            except FileExistsError:
                pass

            with ZipFile(template, "r") as zipObj:
                files = zipObj.namelist()
                zipObj.extractall(path)
                for fileName in files:
                    if fileName.endswith(".json"):
                        template = path + fileName
                        break

        with open(template) as json_file:
            data = json.load(json_file)

        self.filters = data["POSTFILTERS"]

        baseimage = data.get("BASEIMAGE")
        if baseimage != None:
            self.image = Media.open_image(path + baseimage)

        for layer_name in data["LAYERORDER"]:
            layer = data["LAYERS"][layer_name]
            l_type = layer.pop("type")
            if l_type == "text":
                font = ImageFont.truetype(layer["font"]["name"], layer["font"]["size"])
                layer["font"] = font
                del layer["filters"]
                layer["color"] = tuple(layer["color"])
                self.add_layer(Text(**layer))
            else:
                if layer["constant"] != None:
                    layer["constant"] = path + layer["constant"]

                self.add_layer(Img(**layer))

        shutil.rmtree(self.path)

    def export_template(self) -> None:
        files = []
        _dicts = {}
        for layer in self.layers:
            layerData = layer.asdict()

            if layer.constant != None:
                baked = layer.__getbakedlayer__(base=self.image.size)

                savename = f"{layer.name}_CONSTANT.png"
                baked.save(savename)
                files.append(savename)

                const = layerData["constant"]
                layerData = Media(name=layer.name, _type="image").asdict()
                layerData["constant"] = const

            _dicts[layer.name] = layerData

        data = {"LAYERS": _dicts}
        data["POSTFILTERS"] = self.filters
        data["LAYERORDER"] = self.get_layer_names()

        if self.constant_base:
            basename = f"{self.name}_BASEIMAGE.png"
            self.image.save(basename)
            files.append(basename)
            data["BASEIMAGE"] = basename

        jsonName = f"{self.name}_TEMPLATE.json"
        with open(jsonName, "w") as outfile:
            json.dump(data, outfile)
            files.append(jsonName)

        if len(files) > 1:
            with ZipFile(f"{self.name}_TEMPLATE.zip", "w") as zipObj:
                for file in files:
                    zipObj.write(file)
                    os.remove(file)
