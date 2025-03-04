+++
title = "Zulu"
description = "Did you know that zulu is part of the phonetic alphabet?"
authors = []
date = 2024-09-30

[taxonomies]
categories = ["warmups"]
+++

## Description

Did you know that zulu is part of the phonetic alphabet?

----

Extract the archive with the correct software:

```bash
$ file zulu
zulu: compress'd data 16 bits
```

```bash
$ 7z x zulu

7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,16 CPUs AMD Ryzen 7 PRO 6850U with Radeon Graphics      (A40F41),ASM,AES-NI)

Scanning the drive for archives:
1 file, 46 bytes (1 KiB)

Extracting archive: zulu
--
Path = zulu
Type = Z

Everything is Ok

Size:       39
Compressed: 46
~/D/h/h/zulu $ ls -la
.rw-r--r--@  46 acm 13 oct 09:30 zulu
.rw-r--r--@  39 acm 13 oct 09:30 zulu~
~/D/h/h/zulu $ cat zulu~
flag{74235a9216ee609538022e6689b4de5c}
```
