# Forcellini for GoldenDict

"Lexicon Totius Latinitatis" is a monolingual Latin dictionary, though, most of the articles have short translations into Italian, French, Spanish, German and English languages.

This addon for GoldenDict downloads articles from the website and slightly reformat them for better representation.

**N.B.:** Addon is made for _desktop_ version of the GoldenDict, it does not work with _mobile_ application.

Raw requests are saved into the local cache (`code/cache`) to reduce website traffic and improve response to the frequent queries. Directory of the cache can be safely cleaned or completely removed.


### Exemplum

[![screenshot](https://user-images.githubusercontent.com/13879891/74778171-1649a880-52ac-11ea-9292-44cce3f3642b.png)
](https://user-images.githubusercontent.com/13879891/74778078-e00c2900-52ab-11ea-80c1-f6c48dd42b71.png)


### Source

* Forcellini, Egidio; Furlanetto, Giuseppe; Corradini, Francesco; Perin, Josephus. _Lexicon Totius Latinitatis_. Padua, 1771, 1940 (reprint). URL: <http://www.documentacatholicaomnia.eu/25_90_1688-1768-_Forcellini_Aeg.html>.

Dictionary was digitized by Martin Holan (@Godmy) and is available for free use from the website online: [www.lexica.linguax.com](http://www.lexica.linguax.com/).


### Install

***Windows***: special version and instructions are [here](../../releases/tag/1.1).

***Linux***:

Required:
* Python 3
* Python libraries: requests, lxml, regex
  
Use your package manager (preferred) to install these libraries or run the following command in console:

```sh
pip install --user requests lxml regex 

```

Download "Source code" of the [last release](../../releases/tag/v1.0) and save to your computer. Extract archive.

In GoldenDict, open menu Edit|Dictionaries, tab Programs. Add new item:

- type: Html
- name: Forcellini (on your choice)
- command line: `python /path/to/code/main.py %GDWORD%` (correct the path)

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

