---
title: SCWM
build:
  publishResources: false
logo_sm:
  file: scwm_sm.gif
  alt: scwm
  width: 90
  height: 30
logo:
  file: scwm.gif
  alt: '[LOGO]'
  width: 255
  height: 85
heading: SCWM
heading_sep: ' '
license: GPL
activity: Low
---

Scwm is the Scheme Constraints Window Manager. It is a highly dynamic and
extensible window manager and scripting facility for the X Window System. It
was originally based on fvwm2, but has since been enhanced with Guile Scheme
as the configuration and extension language. Nearly all of the decorations can
be changed at runtime or on a per-window basic, and eventually many decoration
styles and additional features will be supported through dynamically loaded
code. A powerful protocol is provided for interacting with the window manager
whilst it is running.

Some of the key features of Scwm are:

- Full programmability using Guile Scheme.
- GUI configurability.
- Support for GUI scripting using guile-gtk.
- Theme support including themes for mwm, fvwm, win95, afterstep and many
  more.
- A powerful external control protocol, allowing commands to be sent to the
  window manager.
- An emacs interaction mode: edit your .scwmrc in emacs, and evaluate the
  results immediately, without restarting.
- Support for fvwm2 modules.
- An XTest extension module that permits scripting interactions with
  applications.

The code is fairly portable and is known to work on a large number of
platforms.

For further information and downloads, see the [Official SCWM
site.](http://scwm.sourceforge.net/)

Here is a [screenshot](screenshots/scwm-xpm.gif) (129k) of Scwm, showing
different decorations being used at the same time. More screenshosts are
available from the official site.
