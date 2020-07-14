#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import sys
import argparse
from lxml import etree
import regex as re
import json
# import hunspell
import unicodedata

CACHE_REQUESTS = True


class WebDict(object):
    work_dir = ""
    cache_dir = ""
    styles = ""

    def __init__(self):
        self.work_dir = os.path.dirname(os.path.realpath(__file__))
        self.cache_dir = self.work_dir + "/cache"
        if not os.path.isdir(self.cache_dir):
            os.mkdir(self.cache_dir)
        with open(f"{self.work_dir}/styles.css", "r") as f:
            self.styles = f.read()

    def load(self, word):
        # word = "abagio"
        url = f"http://lexica.linguax.com/forc2.php?searchedLG={word}"
        cookies = {"LinguaxMsg": "3"}

        try:
            r = requests.get(url, cookies=cookies, timeout=5)
        except requests.exceptions.Timeout as e:
            return {
                "success": False,
                "message": f"Stopped by timeout: {e}"
            }
        except requests.ConnectionError as e:
            return {
                "success": False,
                "message": f"Internet request error: {e}"
            }
        except requests.HTTPError as e:
            return {
                "success": False,
                "message": f"Server error code: {e}"
            }

        if "Nothing has been found." in r.text or "searched Lat. word" not in r.text:
            return {
                "success": False,
                "message": "Word not found."
            }

        text = r.text.replace("<!--  <script src='https://www.google.com/recaptcha/api.js'></script> --!>", "")
        root = etree.HTML(text)

        # magic line identifying dictionary articles
        MAGIC_LINE = "font-family: Palatino Linotype, sans-serif, MS Reference Sans Serif, Microsoft Sans Serif, Verdana, Arial; font-size: 16pt;"

        definitions = []
        for el in root.xpath(f'//div[@style="{MAGIC_LINE}"]'):
            # text = etree.tostring(el, encoding="unicode", method="html")
            definitions.append(el)

        if len(definitions) == 0:
            with open("debug.html", "w") as f:
                f.write(r.text)
            return {
                "success": False,
                "content": "Cannot parse answer! See `debug.html` for content."
            }
        else:
            return {
                "success": True,
                "content": definitions,
            }

    def parse(self, doc):
        doc.tag = "entryFree"
        doc.attrib.pop("style")
        doc.text = ""
        doc.remove(doc[0])

        # header
        el = doc.xpath("//entryFree/span/span/span/span/div")[0]
        text = el.tail
        el = doc.xpath("//entryFree/span[1]/span[1]")[0]
        tail = el.tail
        el.clear()
        el.tag = "hi"
        el.set("rend", "bold")
        el.text = text
        el.tail = tail

        # fix hi-elements (bold, italic)
        for el in doc.xpath("//entryFree//span"):
            el.tag = "hi"
            if "style" not in el.attrib:
                continue
            style = el.attrib.pop("style")
            # self.dbg_styles.add(style)
            if "bold" in style:
                el.attrib["rend"] = "bold"
            elif "italic" in style:
                el.attrib["rend"] = "italic"
            else:
                print(f"DBG: unknown span style >>> {style}")

        # fix references: "forc2.php?searchedLG=POR" > "POR"
        for el in doc.xpath("//entryFree//a"):
            el.attrib["href"] = el.attrib["href"][21:].lower()

        etree.strip_tags(doc, "font")

        html = etree.tostring(doc, encoding="unicode", method="html")
        html = html[11:-12]

        # separate level markers from bold text, see #spes
        html = re.sub(
            r'<hi rend=\"bold\">([^<]*?[!?.])(\s*)([IVX]+\.\))([^<]*?)<\/hi>',
            r'<hi rend="bold">\1</hi>\2<hi rend="bold">\3</hi><hi rend="bold">\4</hi>',
            html
        )

        # find level marks
        html = re.sub(  # A)
            r'([!?.])\s*<hi rend=\"italic\">\s*([A-Z]\))',
            r'\1 <sense level="1" marker="\2"><hi rend="italic">',
            html)
        html = re.sub(  # I.)
            r'([!?.](?:<[^<]*>){0,1})\s*<hi rend=\"bold\">\s*([IVX]+\.\))',
            r'\1 <sense level="2" marker="\2"><hi rend="bold">',
            html)
        html = re.sub(  # 1.
            r'¶\s*<hi rend=\"bold\">\s*(\d+\.)',
            r'<sense level="3" marker="\1"><hi rend="bold">',
            html)
        html = re.sub(  # 1.°)
            r'[-—]\s*<hi rend=\"bold\">\s*([0-9]+\.°\))',
            r'<sense level="4" marker="\1"><hi rend="bold">',
            html)
        html = re.sub(  # 1)
            r'[-—]\s*<hi rend=\"bold\">\s*([0-9]+\))',
            r'<sense level="5" marker="\1"><hi rend="bold">',
            html)
        html = re.sub(  # a)
            r'[-—]\s*<hi rend=\"italic\">\s*([a-z]\))',
            r'<sense level="6" marker="\1"><hi rend="italic">',
            html)
        html = re.sub(  # α)
            r'[-—]\s*([α-ω]\))',
            r'<sense level="7" marker="\1">',
            html)

        # split into senses
        parts = html.split("<sense level=")
        for i in range(1, len(parts)):
            parts[i] = "<sense level=" + parts[i].strip() + "</sense>"
        html = "".join(parts)

        # small fixes
        # html = html.replace("AE", "Æ")
        html = re.sub(r"([>.]) [—-] ", r"\1<br/>", html)

        html = re.sub(r"(\p{IsGreek}{2,}(?: \p{IsGreek}+)*)", r"<span lang='gr'>\1</span>", html)

        # translations
        html = re.sub(r"((?:It|Fr|Hisp|Germ|Angl)\.) <hi rend=\"italic\">", r'<span class="lang">\1</span><hi rend="italic"> ', html)
        html = re.sub(r"(<span class=\"lang\">\w+\.</span><hi rend=\"italic\">[\w ]+);(</hi>)", r"\1\2;", html)

        try:
            doc = etree.fromstring(f"<entryFree>{html}</entryFree>")
        except etree.XMLSyntaxError as e:
            print(f"ERROR: {e}")
            print(">", html)
            sys.exit(2)

        # collate `sense` tags into sub-tree
        senses = doc.xpath("//sense")
        level_prev = 0
        for i in range(len(senses)-1, -1, -1):
            parent = senses[i]
            level_curr = int(senses[i].get("level"))
            if level_curr < level_prev:
                child = parent.getnext()
                while child is not None:
                    if int(child.get("level")) <= level_curr:
                        break
                    parent.append(child)
                    child = parent.getnext()
            level_prev = level_curr

        def remove_element(node):
            parent = node.getparent()
            if node.tail is not None:
                prev = node.getprevious()
                if prev is not None:
                    prev.tail = (prev.tail or '') + node.tail
                else:
                    parent.text = (parent.text or '') + node.tail
            parent.remove(node)

        for el in doc.xpath("//hi"):
            if el.text is None and len(el) == 0:
                remove_element(el)

        table_repl = [
            ("AE", "Æ"), ("ae", "æ"),
            ("OE", "Œ"), ("oe", "œ"),
        ]
        for el in doc.xpath("//*"):
            for patt, repl in table_repl:
                if el.text is not None:
                    el.text = el.text.replace(patt, repl)
                if el.tail is not None:
                    el.tail = el.tail.replace(patt, repl)

        return doc

    def read_cache(self, word):
        filename = f"{self.cache_dir}/{word}.json"
        if not os.path.isfile(filename):
            return None
        with open(filename, "r") as f:
            cache = json.load(f)
        definitions = []
        for item in cache:
            el = etree.HTML(item)
            el = el.xpath("//div")[0]
            definitions.append(el)
        return definitions

    def save_cache(self, word, definitions):
        if len(definitions) == 0:
            return
        filename = f"{self.cache_dir}/{word}.json"
        def_txt = []
        for el in definitions:
            text = etree.tostring(el, encoding="unicode", method="html")
            def_txt.append(text)
        with open(filename, "w") as f:
            json.dump(def_txt, f, ensure_ascii=False)

    def make_html(self, definitions):
        root = etree.Element("dictionary", {"id": "DigitalForcellini"})
        el = etree.SubElement(root, "style", {"type": "text/css"})
        el.text = self.styles
        for subdef in definitions:
            el = self.parse(subdef)
            root.append(el)
        html = etree.tostring(root, encoding="unicode", method="html")
        return html

    def normalize(self, word):
        subs = [
            ("æ", "ae"),
            ("œ", "oe"),
        ]
        word = word.lower()
        word = unicodedata.normalize("NFD", word)
        word = re.sub("[\u0300-\u036f]", "", word)
        for patt, repl in subs:
            word = word.replace(patt, repl)
        return [word]

    # def normalize(self, word):
    #     hspell = hunspell.HunSpell(
    #         "/usr/share/hunspell/la_LA.dic",
    #         "/usr/share/hunspell/la_LA.aff"
    #     )
    #     lemmas = hspell.analyze(word)
    #     for i in range(len(lemmas)):
    #         l = lemmas[i].decode().strip()
    #         lemmas[i] = re.sub(r"st:(.*?)(( fl:.+)|$)", r"\1", l)
    #     iu_lemmas = lemmas
    #     for lemma in lemmas:
    #         iu_lemma = lemma.replace("v", "u")
    #         if (iu_lemma != lemma) and (iu_lemma in lemmas):
    #             iu_lemmas.remove(lemma)
    #     return list(set(iu_lemmas))


def main():
    arg_parser = argparse.ArgumentParser(description='Forcellini for GoldenDict <http://lexica.linguax.com/forc2.php>')
    arg_parser.add_argument('text', type=str, nargs='*',
                            help='a word to look for in the dictionary')
    args = arg_parser.parse_args()
    text = " ".join(args.text).lower()

    if len(text) == 0:
        arg_parser.print_help()
        sys.exit()

    d = WebDict()

    html = ""
    lemmas = d.normalize(text)
    for lemma in lemmas:
        definitions = None
        if CACHE_REQUESTS:
            definitions = d.read_cache(lemma)
        if definitions is None:
            res = d.load(lemma)
            if not res["success"]:
                continue
            definitions = res["content"]
            if CACHE_REQUESTS:
                d.save_cache(lemma, definitions)
        html += d.make_html(definitions)
    if len(html) > 0:
        print(html)


if __name__ == "__main__":
    main()
