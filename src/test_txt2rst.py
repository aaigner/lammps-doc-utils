import io
import tempfile
import unittest
import txt2rst

class TestBasicFormatting(unittest.TestCase):
    def setUp(self):
        self.txt2rst = txt2rst.Txt2Rst()

    def test_empty_string(self):
        self.assertEqual(self.txt2rst.convert(""), "")

    def test_single_paragraph(self):
        self.assertEqual("Hello World!\n\n", self.txt2rst.convert("Hello World!\n"))

    def test_two_paragraphs(self):
        s = self.txt2rst.convert("Hello World!\n\nBye World!\n")
        self.assertEqual("Hello World!\n\n"
                         "Bye World!\n\n", s)

    def test_line_concat(self):
        s = self.txt2rst.convert("Hello World!\\\nBye World!\n")
        self.assertEqual(s, "Hello World!Bye World!\n\n")

    def test_html_pass_through(self):
        s = self.txt2rst.convert("<div>Raw HTML</div>\n")
        self.assertEqual(s, ".. raw:: html\n\n"
                            "   <div>Raw HTML</div>\n\n")

    def test_ignore_html_only_block(self):
        s = self.txt2rst.convert(".. HTML_ONLY\n\n"
                                  "content :p\n"
                                  ".. END_HTML_ONLY\n")
        self.assertEqual("", s)

    def test_pass_through_raw_rst(self):
        raw_rst = ".. toctree::\n" \
                  "   :maxdepth: 2\n" \
                  "   :numbered:\n" \
                  "\n" \
                  "   Introduction\n"

        s = self.txt2rst.convert(".. RST\n" + raw_rst + ".. END_RST\n")
        self.assertEqual(raw_rst, s)

class TestMarkup(unittest.TestCase):
    def setUp(self):
        self.markup = txt2rst.RSTMarkup()
        self.txt2rst = txt2rst.Txt2Rst()

    def test_bold(self):
        self.assertEqual("**bold**", self.markup.convert("[bold]"))

    def test_italic(self):
        self.assertEqual("*italic*", self.markup.convert("{italic}"))

    def test_escape_markup(self):
        s = self.markup.convert("[bold] = \\[bold\\]\n"
                                "{italic} = \\{italic\\}\n")
        self.assertEqual("**bold** = [bold]\n"
                         "*italic* = {italic}\n", s)

    def test_link_markup(self):
        self.assertEqual("`Text <link>`_", self.markup.convert('"Text"_link'))

    def test_document_cross_reference_link(self):
        self.assertEqual(":doc:`Text <link>`", self.markup.convert('"Text"_link.html'))

    def test_external_link(self):
        self.assertEqual("`Text <http://site/index.html>`_", self.markup.convert('"Text"_http://site/index.html'))

    def test_multiline_link_markup(self):
        s = self.txt2rst.convert('"Te\n'
                                  'xt"_link\n')
        self.assertEqual("`Te xt <link>`_\n\n", s)

    def test_ignore_punctuation_in_link(self):
        self.assertEqual("`Text <link>`_.", self.markup.convert('"Text"_link.'))
        self.assertEqual("`Text <link>`_,", self.markup.convert('"Text"_link,'))
        self.assertEqual("`Text <link>`_;", self.markup.convert('"Text"_link;'))
        self.assertEqual("`Text <link>`_:", self.markup.convert('"Text"_link:'))
        self.assertEqual("`Text <link>`_?", self.markup.convert('"Text"_link?'))
        self.assertEqual("`Text <link>`_!", self.markup.convert('"Text"_link!'))
        self.assertEqual("`Text <link>`_(", self.markup.convert('"Text"_link('))
        self.assertEqual("`Text <link>`_)", self.markup.convert('"Text"_link)'))

class TestFormatting(unittest.TestCase):
    def setUp(self):
        self.txt2rst = txt2rst.Txt2Rst()

    def test_paragraph_formatting(self):
        s = self.txt2rst.convert("Hello :p\n")
        self.assertEqual("Hello\n\n", s)

    def test_two_paragraphs_through_formatting(self):
        text = "Hello :p\nBye :p\n"
        p = list(self.txt2rst.paragraphs(text))
        s = self.txt2rst.convert(text)
        self.assertEqual(len(p), 2)
        self.assertEqual(s, "Hello\n"
                            "\n"
                            "Bye\n"
                            "\n")

    def test_break_formatting(self):
        s = self.txt2rst.convert("Hello :b\n")
        self.assertEqual("Hello\n", s)

    def test_preformat_formatting(self):
        s = self.txt2rst.convert("Hello :pre\n")
        self.assertEqual(".. parsed-literal::\n\n"
                         "   Hello\n\n", s)

    def test_header_formatting(self):
        s = self.txt2rst.convert("Level 1 :h1\n"
                                 "Level 2 :h2\n"
                                 "Level 3 :h3\n"
                                 "Level 4 :h4\n"
                                 "Level 5 :h5\n"
                                 "Level 6 :h6\n")
        self.assertEqual("Level 1\n"
                         "#######\n"
                         "\n"
                         "Level 2\n"
                         "*******\n"
                         "\n"
                         "Level 3\n"
                         "=======\n"
                         "\n"
                         "Level 4\n"
                         "-------\n"
                         "\n"
                         "Level 5\n"
                         "^^^^^^^\n"
                         "\n"
                         "Level 6\n"
                         '"""""""\n'
                         '\n', s)

    def test_filter_header_numbers(self):
        s = self.txt2rst.convert("1.1 Level :h1\n")
        self.assertEqual("Level\n"
                         "#####\n\n", s)

class TestListFormatting(unittest.TestCase):
    def setUp(self):
        self.txt2rst = txt2rst.Txt2Rst()

    def test_unordered_list(self):
        s = self.txt2rst.convert("one\n"
                                  "two\n"
                                  "three :ul\n")
        self.assertEqual("* one\n"
                         "* two\n"
                         "* three\n\n", s)

    def test_elementwise_unordered_list(self):
        s = self.txt2rst.convert("one :ulb,l\n"
                                 "two :l\n"
                                 "three :ule,l\n")
        self.assertEqual("* one\n"
                         "* two\n"
                         "* three\n", s)

    def test_multi_line_unordered_list_elements(self):
        s = self.txt2rst.convert("one :ulb,l\n"
                                 "two\n"
                                 "words :l\n"
                                 "three :ule,l\n")
        self.assertEqual("* one\n"
                         "* two\n"
                         "  words\n"
                         "* three\n", s)

    def test_ordered_list(self):
        s = self.txt2rst.convert("one\n"
                                  "two\n"
                                  "three :ol\n")
        self.assertEqual("1. one\n"
                         "2. two\n"
                         "3. three\n\n", s)

    def test_elementwise_ordered_list(self):
        s = self.txt2rst.convert("one :olb,l\n"
                                 "two :l\n"
                                 "three :ole,l\n")
        self.assertEqual("#. one\n"
                         "#. two\n"
                         "#. three\n", s)

    def test_multi_line_ordered_list_elements(self):
        s = self.txt2rst.convert("one :olb,l\n"
                                 "two\n"
                                 "words :l\n"
                                 "three :ole,l\n")
        self.assertEqual("#. one\n"
                         "#. two\n"
                         "   words\n"
                         "#. three\n", s)

    def test_definition_list(self):
        s = self.txt2rst.convert("A\n"
                                  "first\n"
                                  "B\n"
                                  "second :dl\n")
        self.assertEqual("A\n"
                         "   first\n"
                         "\n"
                         "B\n"
                         "   second\n"
                         "\n\n", s)

class TestSpecialCommands(unittest.TestCase):
    def setUp(self):
        self.txt2rst = txt2rst.Txt2Rst()

    def test_line(self):
        self.txt2rst.document_filters = []
        s = self.txt2rst.convert("one :line\n")
        self.assertEqual("\n"
                         "----------\n"
                         "\n"
                         "one\n", s)

    def test_image(self):
        s = self.txt2rst.convert("one :image(file)\n")
        self.assertEqual(".. image:: file\n"
                         "one\n", s)

    def test_centered_image(self):
        s = self.txt2rst.convert(":image(file),c\n")
        self.assertEqual(".. image:: file\n"
                         "   :align: center\n\n", s)

    def test_image_with_link(self):
        s = self.txt2rst.convert("one :image(file,link)\n")
        self.assertEqual(s, ".. image:: file\n"
                            "   :target: link\n"
                            "one\n")

    def test_thumbnail_image(self):
        # requires sphinxcontrib-images extension
        s = self.txt2rst.convert("one :image(file,large_file.jpg)\n")
        self.assertEqual(s, ".. thumbnail:: large_file.jpg\n"
                            "one\n")

    def test_internal_reference_link(self):
        s = self.txt2rst.convert("one :link(name)\n"
                                  "a \"link\"_name to above\n")
        self.assertEqual(".. _name:\n"
                         "\n"
                         "one \n\n"
                         "a :ref:`link <name>` to above\n\n", s)

    def test_local_anchor_link(self):
        s = self.txt2rst.convert("one :link(name)\n"
                                  "a \"link\"_#name to above\n")
        self.assertEqual(".. _name:\n"
                         "\n"
                         "one \n\n"
                         "a :ref:`link <name>` to above\n\n", s)

    def test_define_link_alias(self):
        s = self.txt2rst.convert("one :link(alias,value)\n"
                                 "\"test\"_alias\n")
        self.assertEqual(".. _alias: value\n\n"
                         "one \n"
                         "\n"
                         "`test <alias_>`_\n\n", s)

class TestTableCommand(unittest.TestCase):
    def setUp(self):
        self.txt2rst = txt2rst.Txt2Rst()

    def disable_test_pass_table_as_raw_html(self):
        s = self.txt2rst.convert("a,b,c :tb")
        self.assertEqual(".. raw:: html\n\n"
                         "   <DIV ALIGN=center><TABLE  BORDER=1 >\n"
                         "   <TR><TD >a</TD><TD >b</TD><TD >c \n"
                         "   </TD></TR></TABLE></DIV>\n"
                         "\n", s)

    def test_convert_table_to_grid_table(self):
        s = self.txt2rst.convert("a,b,c :tb")
        table = "+---+---+---+\n" \
                "| a | b | c |\n" \
                "+---+---+---+\n\n"
        self.assertEqual(table, s)

    def test_avoid_rst_syntax_conflicts_with_table_separator(self):
        s = self.txt2rst.convert("\"a\"_test.html: b: c :tb(s=:)")
        table = "+-----------------+---+---+\n" \
                "| :doc:`a <test>` | b | c |\n" \
                "+-----------------+---+---+\n\n"
        self.assertEqual(table, s)

class TestTxt2RstCLI(unittest.TestCase):
    def setUp(self):
        self.out = io.StringIO()
        self.err = io.StringIO()
        self.app = txt2rst.Txt2RstConverter()

    def test_convert_single_file(self):
        with tempfile.NamedTemporaryFile(mode='w+t') as f:
            f.write('Hello World!\n')
            f.flush()
            args = [f.name]
            self.app.run(args=args, out=self.out, err=self.err)
            self.assertEqual("Hello World!\n\n", self.out.getvalue())
            self.assertEqual("Converting " + f.name + " ...\n", self.err.getvalue())

if __name__ == '__main__':
    unittest.main()