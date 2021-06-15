#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import List, Union
from xml.etree import ElementTree

import pytest

from alto import (
    SP,
    Alternative,
    Alto,
    ComposedBlock,
    Description,
    Layout,
    Page,
    PrintSpace,
    String,
    TextBlock,
    TextLine,
    _assert_name_is,
    _check_type,
    _extract_unique_child_name_to_child,
    _get_attr,
    _get_tag,
    _load_string_or_sp,
)

namespaces = (
    '<alto xmlns="http://www.loc.gov/standards/alto/ns-v3#" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xsi:schemaLocation="http://www.loc.gov/standards/alto/ns-v3# '
    'http://www.loc.gov/alto/v3/alto-3-0.xsd">'
)


def _build_xml(xml_str: str) -> ElementTree.Element:
    return ElementTree.fromstring(f"{namespaces}{xml_str}</alto>")[0]


def _string(word: str = 'abc') -> String:
    return String(
        id="string_3", hpos=712, vpos=133, width=55, height=13, confidence=0.92, content=word, alternatives=[]
    )


def _text_line() -> TextLine:
    strings: List[Union[String, SP]] = [_string('abc'), SP(hpos=767, vpos=133, width=9), _string('def')]
    return TextLine(id="line_2", hpos=712, vpos=129, width=235, height=21, strings=strings)


def _text_block() -> TextBlock:
    return TextBlock("block_1", 53, 235, 712, 129, [_text_line(), _text_line()])


def _composed_blocks() -> ComposedBlock:
    return ComposedBlock("composed_block_1", 53, 235, 712, 129, [_text_block(), _text_block()])


def test_extract_unique_child_name_to_child():
    xml_str = '<Page WIDTH="1654" HEIGHT="2339" ID="page_0"></Page>'
    element = ElementTree.fromstring(xml_str)

    assert _extract_unique_child_name_to_child(element) == {}

    xml_str = '<Page WIDTH="1654" HEIGHT="2339" ID="page_0"><Description></Description></Page>'
    element = ElementTree.fromstring(xml_str)
    res = _extract_unique_child_name_to_child(element)
    assert len(res) == 1
    assert "Description" in res
    assert res["Description"].tag == "Description"
    assert res["Description"].attrib == {}

    xml_str = '<Page WIDTH="1654" HEIGHT="2339" ID="page_0"><Description a="1"></Description></Page>'
    element = ElementTree.fromstring(xml_str)
    res = _extract_unique_child_name_to_child(element)
    assert len(res) == 1
    assert "Description" in res
    assert res["Description"].tag == "Description"
    assert res["Description"].attrib == {"a": "1"}

    with pytest.raises(ValueError):
        xml_str = (
            '<Page WIDTH="1654" HEIGHT="2339" ID="page_0"><Description>'
            '</Description><Description></Description></Page>'
        )
        element = ElementTree.fromstring(xml_str)
        _extract_unique_child_name_to_child(element)


def test_get_tag():
    child_1 = ElementTree.Element("child_1")
    assert _get_tag("parent", {"child_1": child_1}, "child_1") == child_1

    with pytest.raises(ValueError):
        _get_tag("parent", {"child_1": child_1}, "child_2")
        _get_tag("parent", {}, "child_1")


def test_get_attr():
    xml_str = '<Page WIDTH="1654" HEIGHT="2339" ID="page_0"></Page>'
    element = ElementTree.fromstring(xml_str)
    assert _get_attr(element, "WIDTH", int) == 1654
    assert _get_attr(element, "WIDTH", float) == 1654.0
    assert _get_attr(element, "WIDTH", str) == "1654"
    assert _get_attr(element, "ID", str) == "page_0"
    assert _get_attr(element, "HEIGHT", str) == "2339"
    with pytest.raises(ValueError):
        assert _get_attr(element, "FOO", str)


def test_check_type():
    assert _check_type(1, int) == 1
    assert _check_type("1", str) == "1"
    with pytest.raises(ValueError):
        _check_type(1, str)
    with pytest.raises(ValueError):
        _check_type("1", int)


def test_assert_name_is():
    _assert_name_is("", "")
    _assert_name_is("1", "1")
    _assert_name_is("abc", "abc")
    with pytest.raises(ValueError):
        _assert_name_is("1", "3")
    with pytest.raises(ValueError):
        _assert_name_is("1", "")


def test_build_description():
    xml_str = """
        <Description>
            <MeasurementUnit>pixel</MeasurementUnit>
            <sourceImageInformation>
                <fileName></fileName>
            </sourceImageInformation>
            <OCRProcessing ID="OCR_0">
                <ocrProcessingStep>
                    <processingSoftware>
                        <softwareName>tesseract 4.1.1</softwareName>
                    </processingSoftware>
                </ocrProcessingStep>
            </OCRProcessing>
        </Description>
    """
    element = _build_xml(xml_str)
    assert Description.from_xml(element) == Description(None)

    xml_str = """
        <Description>
            <MeasurementUnit>pixel</MeasurementUnit>
            <sourceImageInformation>
                <fileName>abc</fileName>
            </sourceImageInformation>
            <OCRProcessing ID="OCR_0">
                <ocrProcessingStep>
                    <processingSoftware>
                        <softwareName>tesseract 4.1.1</softwareName>
                    </processingSoftware>
                </ocrProcessingStep>
            </OCRProcessing>
        </Description>
    """
    element = _build_xml(xml_str)
    assert Description.from_xml(element) == Description("abc")


def test_build_alternative():
    xml_str = """
        <Alternative>test</Alternative>
    """
    element = _build_xml(xml_str)
    assert Alternative.from_xml(element) == Alternative("test")


def test_build_string():
    xml_str = """<String ID="string_3" HPOS="712" VPOS="133" WIDTH="55" HEIGHT="13" WC="0.92" CONTENT="Liberté"/>"""
    element = _build_xml(xml_str)
    assert String.from_xml(element) == String(
        id="string_3",
        hpos=712,
        vpos=133,
        width=55,
        height=13,
        confidence=0.92,
        content="Liberté",
        alternatives=[],
    )

    xml_str = """
        <String ID="string_3" HPOS="712" VPOS="133" WIDTH="55" HEIGHT="13" WC="0.92" CONTENT="Liberté">
            <Alternative>alt</Alternative>
        </String>
    """
    element = _build_xml(xml_str)
    assert String.from_xml(element) == String(
        id="string_3",
        hpos=712,
        vpos=133,
        width=55,
        height=13,
        confidence=0.92,
        content="Liberté",
        alternatives=[Alternative("alt")],
    )


def test_build_sp():
    xml_str = """<SP WIDTH="9" VPOS="133" HPOS="767"/>"""
    element = _build_xml(xml_str)
    assert SP.from_xml(element) == SP(hpos=767, vpos=133, width=9)


def test_load_string_or_sp():
    xml_str = """<SP WIDTH="9" VPOS="133" HPOS="767"/>"""
    element = _build_xml(xml_str)
    assert _load_string_or_sp(element) == SP(hpos=767, vpos=133, width=9)

    xml_str = """<String ID="string_3" HPOS="712" VPOS="133" WIDTH="55" HEIGHT="13" WC="0.92" CONTENT="abc"/>"""
    element = _build_xml(xml_str)
    assert _load_string_or_sp(element) == String(
        id="string_3",
        hpos=712,
        vpos=133,
        width=55,
        height=13,
        confidence=0.92,
        content="abc",
        alternatives=[],
    )

    with pytest.raises(ValueError):
        xml_str = """<Alternative>test</Alternative>"""
        element = _build_xml(xml_str)
        _load_string_or_sp(element)


def test_build_text_line():
    xml_str = """
    <TextLine ID="line_2" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="21">
        <String ID="string_3" HPOS="712" VPOS="133" WIDTH="55" HEIGHT="13" WC="0.92" CONTENT="abc"/>
        <SP WIDTH="9" VPOS="133" HPOS="767"/>
    </TextLine>
    """
    element = _build_xml(xml_str)
    strings = [
        String(
            id="string_3",
            hpos=712,
            vpos=133,
            width=55,
            height=13,
            confidence=0.92,
            content="abc",
            alternatives=[],
        ),
        SP(hpos=767, vpos=133, width=9),
    ]
    assert TextLine.from_xml(element) == TextLine(
        id="line_2", hpos=712, vpos=129, width=235, height=21, strings=strings
    )

    xml_str = """
    <TextLine ID="line_2" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="21">
    </TextLine>
    """
    element = _build_xml(xml_str)
    assert TextLine.from_xml(element) == TextLine(id="line_2", hpos=712, vpos=129, width=235, height=21, strings=[])


def test_text_line_extract_words():
    assert _text_line().extract_words() == ['abc', 'def']
    assert TextLine(id="line_2", hpos=712, vpos=129, width=235, height=21, strings=[]).extract_words() == []


def test_build_text_block():
    element = _build_xml(
        """
        <TextBlock ID="block_1" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="53">
            <TextLine ID="line_2" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="21">
                <String ID="string_3" HPOS="712" VPOS="133" WIDTH="55" HEIGHT="13" WC="0.92" CONTENT="abc"/>
                <SP WIDTH="9" VPOS="133" HPOS="767"/>
            </TextLine>
        </TextBlock>
    """
    )
    strings = [
        String(
            id="string_3",
            hpos=712,
            vpos=133,
            width=55,
            height=13,
            confidence=0.92,
            content="abc",
            alternatives=[],
        ),
        SP(hpos=767, vpos=133, width=9),
    ]
    lines = [TextLine(id="line_2", hpos=712, vpos=129, width=235, height=21, strings=strings)]
    assert TextBlock.from_xml(element) == TextBlock("block_1", 53, 235, 712, 129, lines)


def test_text_block_extract_strings_lines():
    assert _text_block().extract_string_lines() == ['abc def', 'abc def']


def test_text_block_extract_words():
    assert _text_block().extract_words() == ['abc', 'def', 'abc', 'def']


def test_build_composed_block():
    element = _build_xml(
        """
        <ComposedBlock ID="cblock_1" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="53">
            <TextBlock ID="block_1" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="53">
            </TextBlock>
        </ComposedBlock>
        """
    )
    blocks = [TextBlock("block_1", 53, 235, 712, 129, [])]
    assert ComposedBlock.from_xml(element) == ComposedBlock("cblock_1", 53, 235, 712, 129, blocks)


def test_composed_block_extract_words():
    assert _composed_blocks().extract_words() == ['abc', 'def', 'abc', 'def', 'abc', 'def', 'abc', 'def']


def test_build_print_space():
    element = _build_xml(
        """
        <PrintSpace HPOS="0" VPOS="0" WIDTH="1654" HEIGHT="2339">
            <ComposedBlock ID="cblock_1" HPOS="712" VPOS="129" WIDTH="235" HEIGHT="53">
            </ComposedBlock>
        </PrintSpace>
        """
    )
    blocks = [ComposedBlock("cblock_1", 53, 235, 712, 129, [])]
    assert PrintSpace.from_xml(element) == PrintSpace(2339, 1654, 0, 0, None, blocks)


def test_build_page():
    element = _build_xml("""<Page WIDTH="1654" HEIGHT="2339" PHYSICAL_IMG_NR="0" ID="page_0"></Page>""")
    assert Page.from_xml(element) == Page("page_0", 2339, 1654, 0, None, [])


def test_page_extract_blocks():
    assert Page("page_0", 2339, 1654, 0, None, []).extract_blocks() == []
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [])]).extract_blocks() == []
    block = ComposedBlock("", 1, 1, 1, 1, [])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_blocks() == [block]


def test_page_extract_text_blocks():
    assert Page("page_0", 2339, 1654, 0, None, []).extract_text_blocks() == []
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [])]).extract_text_blocks() == []
    block = ComposedBlock("", 1, 1, 1, 1, [])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_text_blocks() == []
    tb = TextBlock("", 1, 1, 1, 1, [])
    block = ComposedBlock("", 1, 1, 1, 1, [tb])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_text_blocks() == [tb]


def test_page_extract_strings():
    assert Page("page_0", 2339, 1654, 0, None, []).extract_strings() == []
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [])]).extract_strings() == []
    block = ComposedBlock("", 1, 1, 1, 1, [])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_strings() == []
    tb = TextBlock("", 1, 1, 1, 1, [])
    block = ComposedBlock("", 1, 1, 1, 1, [tb])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_strings() == []
    tb = TextBlock("", 1, 1, 1, 1, [TextLine("", 1, 1, 1, 1, [String("", 1, 1, 1, 1, "", 0, [])])])
    block = ComposedBlock("", 1, 1, 1, 1, [tb])
    page = Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])])
    assert page.extract_strings() == [String("", 1, 1, 1, 1, "", 0, [])]


def test_page_extract_lines():
    assert Page("page_0", 2339, 1654, 0, None, []).extract_lines() == []
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [])]).extract_lines() == []
    block = ComposedBlock("", 1, 1, 1, 1, [])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_lines() == []
    tb = TextBlock("", 1, 1, 1, 1, [])
    block = ComposedBlock("", 1, 1, 1, 1, [tb])
    assert Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])]).extract_lines() == []
    line = TextLine("", 1, 1, 1, 1, [String("", 1, 1, 1, 1, "", 0, [])])
    tb = TextBlock("", 1, 1, 1, 1, [line])
    block = ComposedBlock("", 1, 1, 1, 1, [tb])
    page = Page("page_0", 2339, 1654, 0, None, [PrintSpace(1, 1, 1, 1, 1, [block])])
    assert page.extract_lines() == [line]


def test_build_layout():
    element = _build_xml("""<Layout></Layout>""")
    Layout.from_xml(element) == Layout([])


def _get_test_data_file() -> str:
    to_replace = "test_alto.py"
    if not __file__.endswith(to_replace):
        raise ValueError(f"Expecting __file__ to end with {to_replace}, got {__file__}")
    return __file__.replace(to_replace, "data/alto_example.xml")


def test_build_alto(real_life_example: str):
    res = Alto.from_xml(ElementTree.fromstring(real_life_example))
    assert len(res.layout.pages) == 1


def test_alto_from_str():
    res = Alto.parse_file(_get_test_data_file())
    assert len(res.layout.pages) == 1


def test_alto_extract_words():
    res = Alto.parse_file(_get_test_data_file())
    assert res.extract_words()[:3] == ["7", "EJ", "."]


def test_alto_extract_grouped_words():
    res = Alto.parse_file(_get_test_data_file())
    assert res.extract_grouped_words('TextBlock')[:2] == [
        ['7', 'EJ', '.'],
        ['Liberté', '<', 'Égalité', '«', 'Fraternité', 'RÉPUBLIQUE', 'FRANÇAISE'],
    ]

    assert res.extract_grouped_words('ComposedBlock')[:2] == [
        ['7', 'EJ', '.'],
        ['Liberté', '<', 'Égalité', '«', 'Fraternité', 'RÉPUBLIQUE', 'FRANÇAISE'],
    ]

    assert res.extract_grouped_words('TextLine')[:2] == [['7'], ['EJ', '.']]
