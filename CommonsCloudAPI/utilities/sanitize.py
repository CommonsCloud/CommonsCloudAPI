"""
For CommonsCloud copyright information please see the LICENSE document
(the "License") included with this software package. This file may not
be used in any manner except in compliance with the License

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


"""
Import Python Dependencies
"""
import html5lib
from html5lib import treebuilders, treewalkers, serializer, sanitizer


"""
A Custom HTML Sanitizer for the CommonsCloud based on the fantastic
HTML5LIB Sanitizer

We've pulled out the various settings, so that they are easy to update
in the future. At the time of this writing, these are really no more than
a copied version of the core Sanitizer, but like we said, in the future
we can come back and tweak this as necessary much more quickly.

@requires
  import html5lib
  from html5lib import treebuilders, treewalkers, serializer, sanitizer

@param (list) acceptable_elements
@param (list) mathml_elements
@param (list) svg_elements
@param (list) acceptable_attributes
@param (list) mathml_attributes
@param (list) svg_attributes
@param (list) attr_val_is_uri
@param (list) svg_attr_val_allows_ref
@param (list) svg_allow_local_href
@param (list) acceptable_css_properties
@param (list) acceptable_css_keywords
@param (list) acceptable_svg_properties
@param (list) acceptable_protocols

@method disallowed_token
    What to do with disallowed tokens .. in our case we're just removing them from
    the string completely.

"""
class CommonsHTMLSanitizer(sanitizer.HTMLSanitizer):

  """
  Sanitization of XHTML+MathML+SVG and of inline style attributes.
  """
  acceptable_elements = ['a', 'abbr', 'acronym', 'address', 'area',
                         'article', 'aside', 'audio', 'b', 'big', 'blockquote', 'br', 'button',
                         'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup',
                         'command', 'datagrid', 'datalist', 'dd', 'del', 'details', 'dfn',
                         'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'event-source', 'fieldset',
                         'figcaption', 'figure', 'footer', 'font', 'form', 'header', 'h1',
                         'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input', 'ins',
                         'keygen', 'kbd', 'label', 'legend', 'li', 'm', 'map', 'menu', 'meter',
                         'multicol', 'nav', 'nextid', 'ol', 'output', 'optgroup', 'option',
                         'p', 'pre', 'progress', 'q', 's', 'samp', 'section', 'select',
                         'small', 'sound', 'source', 'spacer', 'span', 'strike', 'strong',
                         'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'time', 'tfoot',
                         'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'video']

  mathml_elements = ['maction', 'math', 'merror', 'mfrac', 'mi',
                     'mmultiscripts', 'mn', 'mo', 'mover', 'mpadded', 'mphantom',
                     'mprescripts', 'mroot', 'mrow', 'mspace', 'msqrt', 'mstyle', 'msub',
                     'msubsup', 'msup', 'mtable', 'mtd', 'mtext', 'mtr', 'munder',
                     'munderover', 'none']

  svg_elements = ['a', 'animate', 'animateColor', 'animateMotion',
                  'animateTransform', 'clipPath', 'circle', 'defs', 'desc', 'ellipse',
                  'font-face', 'font-face-name', 'font-face-src', 'g', 'glyph', 'hkern',
                  'linearGradient', 'line', 'marker', 'metadata', 'missing-glyph',
                  'mpath', 'path', 'polygon', 'polyline', 'radialGradient', 'rect',
                  'set', 'stop', 'svg', 'switch', 'text', 'title', 'tspan', 'use']

  acceptable_attributes = ['abbr', 'accept', 'accept-charset', 'accesskey',
                           'action', 'align', 'alt', 'autocomplete', 'autofocus', 'axis',
                           'background', 'balance', 'bgcolor', 'bgproperties', 'border',
                           'bordercolor', 'bordercolordark', 'bordercolorlight', 'bottompadding',
                           'cellpadding', 'cellspacing', 'ch', 'challenge', 'char', 'charoff',
                           'choff', 'charset', 'checked', 'cite', 'class', 'clear', 'color',
                           'cols', 'colspan', 'compact', 'contenteditable', 'controls', 'coords',
                           'data', 'datafld', 'datapagesize', 'datasrc', 'datetime', 'default',
                           'delay', 'dir', 'disabled', 'draggable', 'dynsrc', 'enctype', 'end',
                           'face', 'for', 'form', 'frame', 'galleryimg', 'gutter', 'headers',
                           'height', 'hidefocus', 'hidden', 'high', 'href', 'hreflang', 'hspace',
                           'icon', 'id', 'inputmode', 'ismap', 'keytype', 'label', 'leftspacing',
                           'lang', 'list', 'longdesc', 'loop', 'loopcount', 'loopend',
                           'loopstart', 'low', 'lowsrc', 'max', 'maxlength', 'media', 'method',
                           'min', 'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'open',
                           'optimum', 'pattern', 'ping', 'point-size', 'poster', 'pqg', 'preload',
                           'prompt', 'radiogroup', 'readonly', 'rel', 'repeat-max', 'repeat-min',
                           'replace', 'required', 'rev', 'rightspacing', 'rows', 'rowspan',
                           'rules', 'scope', 'selected', 'shape', 'size', 'span', 'src', 'start',
                           'step', 'style', 'summary', 'suppress', 'tabindex', 'target',
                           'template', 'title', 'toppadding', 'type', 'unselectable', 'usemap',
                           'urn', 'valign', 'value', 'variable', 'volume', 'vspace', 'vrml',
                           'width', 'wrap', 'xml:lang']

  mathml_attributes = ['actiontype', 'align', 'columnalign', 'columnalign',
                       'columnalign', 'columnlines', 'columnspacing', 'columnspan', 'depth',
                       'display', 'displaystyle', 'equalcolumns', 'equalrows', 'fence',
                       'fontstyle', 'fontweight', 'frame', 'height', 'linethickness', 'lspace',
                       'mathbackground', 'mathcolor', 'mathvariant', 'mathvariant', 'maxsize',
                       'minsize', 'other', 'rowalign', 'rowalign', 'rowalign', 'rowlines',
                       'rowspacing', 'rowspan', 'rspace', 'scriptlevel', 'selection',
                       'separator', 'stretchy', 'width', 'width', 'xlink:href', 'xlink:show',
                       'xlink:type', 'xmlns', 'xmlns:xlink']

  svg_attributes = ['accent-height', 'accumulate', 'additive', 'alphabetic',
                    'arabic-form', 'ascent', 'attributeName', 'attributeType',
                    'baseProfile', 'bbox', 'begin', 'by', 'calcMode', 'cap-height',
                    'class', 'clip-path', 'color', 'color-rendering', 'content', 'cx',
                    'cy', 'd', 'dx', 'dy', 'descent', 'display', 'dur', 'end', 'fill',
                    'fill-opacity', 'fill-rule', 'font-family', 'font-size',
                    'font-stretch', 'font-style', 'font-variant', 'font-weight', 'from',
                    'fx', 'fy', 'g1', 'g2', 'glyph-name', 'gradientUnits', 'hanging',
                    'height', 'horiz-adv-x', 'horiz-origin-x', 'id', 'ideographic', 'k',
                    'keyPoints', 'keySplines', 'keyTimes', 'lang', 'marker-end',
                    'marker-mid', 'marker-start', 'markerHeight', 'markerUnits',
                    'markerWidth', 'mathematical', 'max', 'min', 'name', 'offset',
                    'opacity', 'orient', 'origin', 'overline-position',
                    'overline-thickness', 'panose-1', 'path', 'pathLength', 'points',
                    'preserveAspectRatio', 'r', 'refX', 'refY', 'repeatCount',
                    'repeatDur', 'requiredExtensions', 'requiredFeatures', 'restart',
                    'rotate', 'rx', 'ry', 'slope', 'stemh', 'stemv', 'stop-color',
                    'stop-opacity', 'strikethrough-position', 'strikethrough-thickness',
                    'stroke', 'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap',
                    'stroke-linejoin', 'stroke-miterlimit', 'stroke-opacity',
                    'stroke-width', 'systemLanguage', 'target', 'text-anchor', 'to',
                    'transform', 'type', 'u1', 'u2', 'underline-position',
                    'underline-thickness', 'unicode', 'unicode-range', 'units-per-em',
                    'values', 'version', 'viewBox', 'visibility', 'width', 'widths', 'x',
                    'x-height', 'x1', 'x2', 'xlink:actuate', 'xlink:arcrole',
                    'xlink:href', 'xlink:role', 'xlink:show', 'xlink:title', 'xlink:type',
                    'xml:base', 'xml:lang', 'xml:space', 'xmlns', 'xmlns:xlink', 'y',
                    'y1', 'y2', 'zoomAndPan']

  attr_val_is_uri = ['href', 'src', 'cite', 'action', 'longdesc', 'poster',
                     'xlink:href', 'xml:base']

  svg_attr_val_allows_ref = ['clip-path', 'color-profile', 'cursor', 'fill',
                             'filter', 'marker', 'marker-start', 'marker-mid', 'marker-end',
                             'mask', 'stroke']

  svg_allow_local_href = ['altGlyph', 'animate', 'animateColor',
                          'animateMotion', 'animateTransform', 'cursor', 'feImage', 'filter',
                          'linearGradient', 'pattern', 'radialGradient', 'textpath', 'tref',
                          'set', 'use']

  acceptable_css_properties = ['azimuth', 'background-color',
                               'border-bottom-color', 'border-collapse', 'border-color',
                               'border-left-color', 'border-right-color', 'border-top-color', 'clear',
                               'color', 'cursor', 'direction', 'display', 'elevation', 'float', 'font',
                               'font-family', 'font-size', 'font-style', 'font-variant', 'font-weight',
                               'height', 'letter-spacing', 'line-height', 'overflow', 'pause',
                               'pause-after', 'pause-before', 'pitch', 'pitch-range', 'richness',
                               'speak', 'speak-header', 'speak-numeral', 'speak-punctuation',
                               'speech-rate', 'stress', 'text-align', 'text-decoration', 'text-indent',
                               'unicode-bidi', 'vertical-align', 'voice-family', 'volume',
                               'white-space', 'width']

  acceptable_css_keywords = ['auto', 'aqua', 'black', 'block', 'blue',
                             'bold', 'both', 'bottom', 'brown', 'center', 'collapse', 'dashed',
                             'dotted', 'fuchsia', 'gray', 'green', '!important', 'italic', 'left',
                             'lime', 'maroon', 'medium', 'none', 'navy', 'normal', 'nowrap', 'olive',
                             'pointer', 'purple', 'red', 'right', 'solid', 'silver', 'teal', 'top',
                             'transparent', 'underline', 'white', 'yellow']

  acceptable_svg_properties = ['fill', 'fill-opacity', 'fill-rule',
                               'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin',
                               'stroke-opacity']

  acceptable_protocols = ['ed2k', 'ftp', 'http', 'https', 'irc',
                          'mailto', 'news', 'gopher', 'nntp', 'telnet', 'webcal',
                          'xmpp', 'callto', 'feed', 'urn', 'aim', 'rsync', 'tag',
                          'ssh', 'sftp', 'rtsp', 'afs']

  # subclasses may define their own versions of these constants
  allowed_elements = acceptable_elements + mathml_elements + svg_elements
  allowed_attributes = acceptable_attributes + mathml_attributes + svg_attributes
  allowed_css_properties = acceptable_css_properties
  allowed_css_keywords = acceptable_css_keywords
  allowed_svg_properties = acceptable_svg_properties
  allowed_protocols = acceptable_protocols

  """
  Instead of sanitizing the disallowed tokens from our sting, let's just
  completely remove them for this particular case. We can remove this later
  if it proves confusing.
  """
  def disallowed_token(self, token, token_type):
    return ""


"""
A class that defines some helper functions for our new HTML santiziation, 
which just makes it easier to quickly sanitize a string within a block of
code elsewhere in the CommonsCloud

@

"""
class CommonsSanitize():

  """
  Initialize is empty for now

  @param (object) self

  @return (NoneType) None
      Nothing of course

  """
  def __init__(self):
    return None

  """
  Sanitize an HTML string, removing potentially harmful HTML from our inputs
  """
  def sanitize_string(self, user_input):
    p = html5lib.HTMLParser(tokenizer=CommonsHTMLSanitizer, tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parseFragment(user_input)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)

    s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False, quote_attr_values=True)
    return u"".join(s.serialize(stream))


  """
  Sanitize an Boolean string, removing potentially harmful Boolean from our inputs
  """
  def sanitize_boolean(self, user_input):
    pass


  """
  Sanitize an Array string, removing potentially harmful Boolean from our inputs
  """
  def sanitize_array(self, user_input):
    pass
