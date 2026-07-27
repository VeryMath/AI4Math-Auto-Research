# LaTeX Report Guidelines

## Project and File Safety

Create a new per-paper project directory and preserve source, bibliography, figures, build logs, and rendered-page images together. Never overwrite a user file: choose a new directory or versioned filename when a target exists. Keep generated artifacts separate from supplied originals.

## Typesetting and Build

Use Unicode-capable Chinese typesetting with XeLaTeX and appropriate installed CJK fonts or packages. Prefer `latexmk -xelatex` when available. Otherwise run the required `xelatex` passes and, when bibliography processing is needed, run `biber` followed by enough `xelatex` passes to resolve references. Preserve the command transcript and build logs. Treat missing citations, unresolved references, unavailable fonts, and overfull boxes as issues to investigate rather than harmless noise.

## Diagrams and Accessibility

Use TikZ for dependency diagrams and mathematical figures when it is reliable and maintainable. Also provide a text-tree fallback so theorem dependencies remain readable when TikZ is unavailable, fails to compile, or is inaccessible to the reader. Keep notation, labels, and captions consistent with the report body.

## Delivery Gate

Compile without fatal errors, render every page to images, inspect formulas, tables, diagrams, bibliography, clipping, overflow, and blank pages, then revise and repeat until the artifact passes.

Deliver the `.tex` sources, bibliography and required assets, compiled PDF, preserved logs, and the verified final render. Do not claim completion from compilation alone; visual inspection of every page is mandatory.
