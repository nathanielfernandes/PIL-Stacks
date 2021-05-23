from src import *
import os


# meme = Stack(name="bob")
# meme.import_template("example_TEMPLATE.zip")


# kwargs = {
#     "top_text": "ayan is mega gay",
# }


# img = meme.generate(**kwargs)
# img.show()
a = Editor(name="example", Background="test.png")
# a.show_fps = True
# a.__debug_info__ = True

stack = a.Launch()
# stack.export_template() uncomment to test exporting
