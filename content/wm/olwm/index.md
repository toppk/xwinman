---
title: OLWM
logo:
  file: olwm.gif
  alt: '[LOGO]'
  width: 160
  height: 70
heading: The OpenLook Window Manager
heading_style: table
license: Custom
activity: Low
build:
  render: never
  list: never
  publishResources: false
---

Olwm implements parts of the OPEN LOOK graphical user interface. It was once
the standard window manager for Sun's OpenWindows, before Sun adopted Motif,
CDE, and then more recently, GNOME, instead.

See this full sized (1152x900) [screenshot](screenshots/olwm.gif) (26k). This
was obtained using the default configuration. This should be called after
running <kbd>openwin</kbd>, and not <kbd>startx</kbd>. Also the environment variable <kbd>OPENWINHOME</kbd> should
be set appropriately - usually to <kbd>/usr/openwin</kbd>.
