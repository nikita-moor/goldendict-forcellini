# Forcellini for GoldenDict

"Lexicon Totius Latinitatis" is a monolingual Latin dictionary, though, most of the articles have short translations into Italian, French, Spanish, German and English languages.

Source:

* Forcellini, Egidio; Furlanetto, Giuseppe; Corradini, Francesco; Perin, Josephus. Lexicon Totius Latinitatis. Padua, 1771, 1940 (reprint). URL: <http://www.documentacatholicaomnia.eu/25_90_1688-1768-_Forcellini_Aeg.html>.

Dictionary was digitized by Martin Holan (@Godmy) and is available for free use from the website online: <www.lexica.linguax.com>.

This addon for GoldenDict downloads articles from the website and slightly reformat them for better representation.

**N.B.:** Addon is made for _desktop_ version of the GoldenDict, it does not work with _mobile_ application.

Raw requests are saved into the local cache (`code/cache`) to reduce website traffic and improve responce to the frequent queries. Directory of the cache can be safely cleaned or completely removed.


### Install

Following documentation is written for Linux users. If your operation system is Windows or MacOS and you are not an experienced user, [make request](/issues), please, for additional instructions.

Required Python libraries: requests, lxml, regex. Use your package manager (preferred) or `pip`:

```sh
pip install --user requests lxml regex 

```

Download files from the folder "code" and save on your computer.

In GoldenDict, open menu Edit|Dictionaries, tab Programs. Add new item:

- type: Html
- name: Forcellini (on your choice)
- command line: python /path/to/main.py %GDWORD%

Press "OK" button.


### Known limitations

General structure of the articles is the following:

```
A)
  I.)
    1.
      1.°)
        1)
          a)
            α)
```

However, authors does not always follow this agreement. For example, in "adhibeo", `A)` is subordinate to "II.)". We can't take into account every particular deviation, so the application does fail in such cases.


### License

Public Domain or CC0.

