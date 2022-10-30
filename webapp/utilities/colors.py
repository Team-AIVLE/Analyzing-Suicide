import seaborn as sns
import matplotlib.colors as mcolors

from typing import List

cmap = mcolors.get_named_colors_mapping()

COLOR_ADJUSTER = 50
colors = ['#F5A9A9', '#F5BCA9', '#F5D0A9', '#F3E2A9', '#F2F5A9',
          '#E1F5A9', '#D0F5A9', '#BCF5A9', '#A9F5A9', '#A9F5BC',
          '#A9F5D0', '#A9F5E1', '#A9F5F2', '#A9E2F3', '#A9D0F5',
          '#A9BCF5', '#A9A9F5', '#BCA9F5', '#D0A9F5', '#E2A9F3',
          '#F5A9F2', '#F5A9E1', '#F5A9D0', '#F5A9BC', '#E6E6E6']

def rgb_to_hex(r, g, b):
    r, g, b = int(r), int(g), int(b)
    return '#' + hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2)

def int_to_hex_str(value : int):
    return '{0:02x}'.format(value)
  
def get_colors(color_num : int, base_color : List[str]):
    base_color = [color if color.startswith('#') else cmap[color] for color in base_color]
    
    while len(base_color) < color_num:
        base_color += ["#%s" % int_to_hex_str(int(color[1:], 16) + COLOR_ADJUSTER).upper() for color in base_color[:color_num-len(base_color)]]
    return base_color


def get_palette(n_colors, palette='crest'):
    palette = sns.color_palette(palette, as_cmap=False, n_colors=n_colors)
    return list(palette.as_hex())
    