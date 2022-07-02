# -*- mode: python ; coding: utf-8 -*-

import sys; sys.path.insert(0, '.')
import specs
if specs.is_osx: exit()

# Create the analysis
a = specs.get_analysis(Analysis, TOC)
pyz = specs.get_pyz(PYZ, a)
exe = specs.get_exe(EXE, pyz, a, True)

# Save to zip
# specs.save_zip('PDFConvert.exe', 'PDFConvert.Win64')