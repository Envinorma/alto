# -*- coding: utf-8 -*-

"""Top-level package for Alto."""

__author__ = "Rémi Delbouys"
__email__ = "remi.delbouys@laposte.net"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.3"


def get_module_version():
    return __version__


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

_MAX_PRINT_CHILDREN = 50
_Namespace = "{http://www.loc.gov/standards/alto/ns-v3#}"


class _Tags:
    DESCRIPTION = f"{_Namespace}Description"
    LAYOUT = f"{_Namespace}Layout"
    PAGE = f"{_Namespace}Page"
    TEXT_BLOCK = f"{_Namespace}TextBlock"
    TEXT_LINE = f"{_Namespace}TextLine"
    String = f"{_Namespace}String"
    SP = f"{_Namespace}SP"
    SOURCE_IMAGE_INFORMATION = f"{_Namespace}sourceImageInformation"
    COMPOSED_BLOCK = f"{_Namespace}ComposedBlock"
    PRINTSPACE = f"{_Namespace}PrintSpace"
    FILENAME = f"{_Namespace}fileName"


class _Attrs:
    ID = "ID"
    HEIGHT = "HEIGHT"
    WIDTH = "WIDTH"
    HPOS = "HPOS"
    VPOS = "VPOS"
    FONTSIZE = "FONTSIZE"
    CONTENT = "CONTENT"
    WC = "WC"
    PC = "PC"
    PHYSICAL_IMG_NR = "PHYSICAL_IMG_NR"
    PRINTED_IMG_NR = "PRINTED_IMG_NR"
    FONTSIZE = "FONTSIZE"


T2 = TypeVar("T2")


def _check_type(candidate: Any, type_: Type[T2]) -> T2:
    if not isinstance(candidate, type_):
        raise ValueError(f"Expecting type {type_}, got {type(candidate)}")
    return candidate


def _assert_str(candidate: Any) -> str:
    return _check_type(candidate, str)


def _extract_unique_child_name_to_child(element: Element) -> Dict[str, Element]:
    res: Dict[str, Element] = {}
    for child in element:
        if child.tag in res:
            raise ValueError(f"Non unique child tag name: {child} in element {element.tag}")
        res[child.tag] = child
    return res


def _get_tag(element_tag_name: str, children: Dict[str, Element], tag_name: str) -> Element:
    if tag_name not in children:
        raise ValueError(
            f"Error when parsing XML: expecting tag {element_tag_name} to have child {tag_name}. "
            f"Available children: {list(children.keys())[:_MAX_PRINT_CHILDREN]}"
        )
    return children[tag_name]


T = TypeVar("T", bound=Union[int, str, float])


def _get_attr(element: Element, attr_name: str, type_: Type[T]) -> T:
    attrs = cast(Dict, element.attrib)
    if attr_name not in attrs:
        raise ValueError(
            f"Error when parsing XML: expecting tag {element.tag} to have attribute {attr_name}. "
            f"Available attributes: {list(attrs.keys())[:_MAX_PRINT_CHILDREN]}"
        )
    value = attrs[attr_name]
    try:
        res = type_(value)
        return res  # type: ignore
    except TypeError:
        raise ValueError(
            f"Error when parsing XML: expecting tag attribute {attr_name} of tag {element.tag} "
            f"to have type {type_}, got {type(value)}."
        )


def _assert_name_is(name: str, expected: str) -> None:
    if name != expected:
        raise ValueError(f"Error when parsing XML: Expecting tag name {expected}, got tag name {name}")


@dataclass
class Description:
    file_name: Optional[str]

    @classmethod
    def from_xml(cls, element: Element) -> "Description":
        children = _extract_unique_child_name_to_child(element)
        source = _get_tag(element.tag, children, _Tags.SOURCE_IMAGE_INFORMATION)
        file_name = _get_tag(source.tag, _extract_unique_child_name_to_child(source), _Tags.FILENAME)
        return cls(file_name.text)


@dataclass
class Alternative:
    content: str

    @classmethod
    def from_xml(cls, element: Element) -> "Alternative":
        return cls(content=_assert_str(element.text))


@dataclass
class String:
    id: str
    height: float
    width: float
    hpos: float
    vpos: float
    content: str
    confidence: float
    alternatives: List[Alternative]

    @classmethod
    def from_xml(cls, element: Element) -> "String":
        return cls(
            id=_get_attr(element, _Attrs.ID, str),
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
            content=_get_attr(element, _Attrs.CONTENT, str),
            confidence=_get_attr(element, _Attrs.WC, float),
            alternatives=[Alternative.from_xml(child) for child in element],
        )


@dataclass
class SP:
    width: float
    hpos: float
    vpos: float

    @classmethod
    def from_xml(cls, element: Element) -> "SP":
        return cls(
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
        )


def _load_string_or_sp(element: Element) -> Union[String, SP]:
    if element.tag == _Tags.String:
        return String.from_xml(element)
    if element.tag == _Tags.SP:
        return SP.from_xml(element)
    raise ValueError(f"Error in when parsing XML: expecting tag {_Tags.String} or {_Tags.SP}, got {element.tag}")


@dataclass
class TextLine:
    id: str
    height: float
    width: float
    hpos: float
    vpos: float
    strings: List[Union[String, SP]]

    @classmethod
    def from_xml(cls, element: Element) -> "TextLine":
        _assert_name_is(element.tag, _Tags.TEXT_LINE)
        return cls(
            id=_get_attr(element, _Attrs.ID, str),
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
            strings=[_load_string_or_sp(child) for child in element],
        )

    def __hash__(self) -> int:
        return hash(
            (
                self.height,
                self.width,
                self.hpos,
                self.height,
                tuple(self.extract_strings()),
            )
        )

    def extract_strings(self) -> List[str]:
        return [str_.content for str_ in self.strings if isinstance(str_, String)]


@dataclass
class TextBlock:
    id: Optional[str]
    height: float
    width: float
    hpos: float
    vpos: float
    text_lines: List[TextLine]

    @classmethod
    def from_xml(cls, element: Element) -> "TextBlock":
        _assert_name_is(element.tag, _Tags.TEXT_BLOCK)
        return cls(
            id=_get_attr(element, _Attrs.ID, str),
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
            text_lines=[TextLine.from_xml(child) for child in element],
        )

    def extract_string_lines(self) -> List[str]:
        return [" ".join(line.extract_strings()) for line in self.text_lines]


@dataclass
class ComposedBlock:
    id: str
    height: float
    width: float
    hpos: float
    vpos: float
    text_blocks: List[TextBlock]

    @classmethod
    def from_xml(cls, element: Element) -> "ComposedBlock":
        _assert_name_is(element.tag, _Tags.COMPOSED_BLOCK)
        return cls(
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
            id=_get_attr(element, _Attrs.ID, str),
            text_blocks=[TextBlock.from_xml(child) for child in element],
        )


@dataclass
class PrintSpace:
    height: float
    width: float
    hpos: float
    vpos: float
    pc: Optional[float]
    composed_blocks: List[ComposedBlock]

    @classmethod
    def from_xml(cls, element: Element) -> "PrintSpace":
        _assert_name_is(element.tag, _Tags.PRINTSPACE)
        return cls(
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            hpos=_get_attr(element, _Attrs.HPOS, float),
            vpos=_get_attr(element, _Attrs.VPOS, float),
            pc=_get_attr(element, _Attrs.PC, float) if _Attrs.PC in element.attrib else None,
            composed_blocks=[ComposedBlock.from_xml(child) for child in element],
        )


@dataclass
class Page:
    id: str
    height: float
    width: float
    physical_img_nr: int
    printed_img_nr: Optional[int]
    print_spaces: List[PrintSpace]

    @classmethod
    def from_xml(cls, element: Element) -> "Page":
        _assert_name_is(element.tag, _Tags.PAGE)
        return cls(
            id=_get_attr(element, _Attrs.ID, str),
            height=_get_attr(element, _Attrs.HEIGHT, float),
            width=_get_attr(element, _Attrs.WIDTH, float),
            physical_img_nr=_get_attr(element, _Attrs.PHYSICAL_IMG_NR, int),
            printed_img_nr=_get_attr(element, _Attrs.PRINTED_IMG_NR, int)
            if _Attrs.PRINTED_IMG_NR in element.attrib
            else None,
            print_spaces=[PrintSpace.from_xml(child) for child in element],
        )

    def extract_blocks(self) -> List[ComposedBlock]:
        return [block for ps in self.print_spaces for block in ps.composed_blocks]

    def extract_text_blocks(self) -> List[TextBlock]:
        return [tb for ps in self.print_spaces for block in ps.composed_blocks for tb in block.text_blocks]

    def extract_strings(self) -> List[String]:
        return [
            string
            for ps in self.print_spaces
            for block in ps.composed_blocks
            for tb in block.text_blocks
            for line in tb.text_lines
            for string in line.strings
            if isinstance(string, String)
        ]

    def extract_lines(self) -> List[TextLine]:
        return [
            line
            for ps in self.print_spaces
            for block in ps.composed_blocks
            for tb in block.text_blocks
            for line in tb.text_lines
        ]


@dataclass
class Layout:
    pages: List[Page]

    @classmethod
    def from_xml(cls, element: Element) -> "Layout":
        return cls(pages=[Page.from_xml(child) for child in element])


@dataclass
class Alto:
    """
    Alto dataclass for manipulating Tesseract output files.

    Parameters
    ----------
    description: Description
        The "description" tag of alto xml documents, containing metadata
    layout: Layout
        The "layout" tag of alto xml documents, containing parsed elements
    """

    description: Description
    layout: Layout

    @classmethod
    def from_xml(cls, element: Element) -> "Alto":
        children = _extract_unique_child_name_to_child(element)
        return cls(
            description=Description.from_xml(_get_tag(element.tag, children, _Tags.DESCRIPTION)),
            layout=Layout.from_xml(_get_tag(element.tag, children, _Tags.LAYOUT)),
        )

    @staticmethod
    def parse_file(filename: str) -> "Alto":
        """
        Alto constructor from xml file.

        Parameters
        ----------
        filename: str
            filename of the file to load
        """
        tree = ElementTree.parse(filename)
        return Alto.from_xml(tree.getroot())

    @staticmethod
    def parse(xml_str: str) -> "Alto":
        """
        Alto constructor from xml string.

        Parameters
        ----------
        xml_str: str
            xml alto string
        """

        tree = ElementTree.fromstring(xml_str)
        return Alto.from_xml(tree)

    def extract_words(self) -> List[str]:
        """
        Extracts all parsed words from alto objects regardless of their positions.

        Parameters
        ----------
        xml_str: str
            xml alto string
        """

        return [
            string.content
            for page in self.layout.pages
            for ps in page.print_spaces
            for block in ps.composed_blocks
            for tb in block.text_blocks
            for line in tb.text_lines
            for string in line.strings
            if isinstance(string, String)
        ]


def parse_file(filename: str) -> Alto:
    """
    Alto constructor from xml file.

    Parameters
    ----------
    filename: str
        filename of the file to load
    """
    return Alto.parse_file(filename)


def parse(xml_string: str) -> Alto:
    """
    Alto constructor from xml string.

    Parameters
    ----------
    xml_str: str
        xml alto string
    """
    return Alto.parse(xml_string)
