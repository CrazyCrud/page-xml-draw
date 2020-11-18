from lib.parse import *
import numpy as np
import cv2

def get_element(parent, name):
  element = None

  for child in parent:
    if child.tag.endswith(name):
      element = child

  return element

def get_elements(parent, name):
  elements = []

  for child in parent:
    if child.tag.endswith(name):
      elements.append(child)

  return elements

def get_polygon(element):
    coords = get_element(element, "Coords")
    point_string = coords.attrib['points']

    polygon = []
    for point in point_string.split(" "):
        polygon.append([int(p) for p in point.split(",")])

    return np.array(polygon)

class Page:
    def __init__(self, root):
        self.pagefile = get_element(root, "Page")
        self.border = get_element(self.pagefile, "Border")
        self.regions = get_elements(self.pagefile, "TextRegion")
        self.lines = [get_elements(region, "TextLine") for region in self.regions]

def overlay_image(image, polygons, fill_color, outline_color, thickness, alpha):
  overlay = image.copy()

  if fill_color is not None:
    cv2.fillPoly(overlay, polygons, fill_color)

  if outline_color is not None:
    cv2.polylines(overlay, polygons, True, outline_color, thickness)

  return cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

if __name__ == "__main__":

  # returns parsed user selected parameters
  options = get_options()

  # fetches XML file
  tree = ET.parse(str(options.input))
  root = tree.getroot()

  # fetches the PAGE's data
  page = Page(root)

  # fetches original image
  image_path = options.base_dir / page.pagefile.attrib['imageFilename']
  image = cv2.imread(str(image_path))

  # border
  if options.border is not None and page.border is not None:

    polygon = get_polygon(Page.border)

    image = overlay_image(image, [polygon], options.border.fill_color, options.border.outline_color, options.border.thickness, options.border.alpha)

  # text regions
  if options.text_regions is not None:

    polygons = []
    for region in page.regions:
      polygons.append(get_polygon(region))

    image = overlay_image(image, polygons, options.text_regions.fill_color, options.text_regions.outline_color, options.text_regions.thickness, options.text_regions.alpha)

  # text lines
  if options.text_lines is not None:

    polygons = []

    for line in page.lines:
        polygons.append(get_polygon(line))

    image = overlay_image(image, polygons, options.text_lines.fill_color, options.text_lines.outline_color, options.text_lines.thickness, options.text_lines.alpha)

  # final image
  cv2.imwrite(str(options.output), image)
