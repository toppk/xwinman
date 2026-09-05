---
title: Comparisons
features:
  columns:
  - - Virtual
    - Desktops
  - - Workspaces
    - or Screens
  - - XPM
    - Support
  - - Pinnable
    - Menus
  - - Session
    - Management
  rows:
  - name: TWM
    has:
    - false
    - false
    - false
    - false
    - false
  - name: VTWM
    has:
    - true
    - false
    - false
    - false
    - false
  - name: FVWM
    has:
    - true
    - true
    - true
    - true
    - true
  - name: FVWM-95
    has:
    - true
    - true
    - true
    - false
    - false
  - name: AfterStep
    has:
    - true
    - true
    - true
    - true
    - false
  - name: CDE (dtwm)
    has:
    - false
    - true
    - true
    - false
    - true
  - name: AmiWM
    has:
    - false
    - true
    - false
    - false
    - false
  - name: OLWM
    has:
    - false
    - false
    - false
    - true
    - false
  - name: OLVWM
    has:
    - true
    - false
    - true
    - true
    - false
  - name: GWM
    has:
    - true
    - true
    - true
    - false
    - false
  - note: 1
    name: MWM
    has:
    - true
    - true
    - true
    - true
    - false
  - name: CTWM
    has:
    - true
    - true
    - true
    - true
    - false
  - name: Enlightenment
    has:
    - true
    - true
    - true
    - true
    - false
  - name: WM2
    has:
    - false
    - false
    - false
    - false
    - false
  - name: Window Maker
    has:
    - false
    - true
    - true
    - true
    - false
  - name: KDE
    has:
    - true
    - true
    - true
    - false
    - true
  - name: ICEWM
    has:
    - false
    - true
    - true
    - false
    - false
  - name: SCWM
    has:
    - true
    - true
    - true
    - true
    - true
resources:
  columns:
  - label: Binary Size
    note: 2
    sub: (SunOS 5.x)
  - label: Binary Size
    note: 2
    sub: (Linux 2.x)
  - label: Memory Size
    note: 3
    sub: (SunOS 5.x)
  - label: Memory Size
    note: 3
    sub: (Linux 2.x)
  rows:
  - name: twm
    values:
    - 154K
    - 128K
    - 2672K
    - 1504K
  - name: vtwm
    values:
    - N/A
    - N/A
    - N/A
    - N/A
  - note: 4
    name: fvwm
    values:
    - 154K / 209K
    - 109K / N/A
    - "2232K\n\t    / 2264K"
    - N/A
  - note: 5
    name: FvwmPager
    values:
    - 57K
    - 30K
    - 1848K
    - 1436K
  - note: 5
    name: FvwmButtons
    sub: (GoodStuff)
    values:
    - 81K
    - 23K
    - 2072K
    - 712K
  - name: fvwm95
    values:
    - 148K
    - 115K
    - 2192K
    - 1032K
  - name: afterstep
    values:
    - N/A
    - 122K
    - N/A
    - 1648K
  - note: 6
    name: Wharf
    values:
    - N/A
    - 37K
    - N/A
    - 1556K
  - name: CDE (dtwm)
    values:
    - 513K
    - 433K
    - 6600K
    - 6672K
  - name: amiwm
    values:
    - N/A
    - 468K
    - N/A
    - 376K
  - name: olwm
    values:
    - 231K
    - 193K
    - 2232K
    - N/A
  - name: olvwm
    values:
    - N/A
    - 280K
    - N/A
    - N/A
  - name: gwm
    values:
    - 337K
    - N/A
    - 3352K
    - N/A
  - name: mwm
    values:
    - 247K
    - 293K
    - 4050K
    - N/A
  - name: ctwm
    values:
    - 293K
    - 241K
    - 2936K
    - 2180K
  - name: icewm
    values:
    - N/A
    - 211K
    - N/A
    - 916K
  - name: scwm
    values:
    - N/A
    - 516K
    - N/A
    - 6708K
---

## Comparisons

It is difficult to compare window managers fairly, because many factors are
involved, such as range of features, customization, documentation, stability,
ease of installation, and hardware/software requirements, not to mention
personal preferences. However, the following tables attempt to give a broad
indication of some of the relative merits of the featured window managers. The
figures in the resource requirements table shouldn't be taken too seriously as
they are dependent to some extent on the particular machine involved, and the
way it's configured.

### Features

<p>

{{< features >}}

Pinnable menus are ones which you can leave on the desktop, for easy access.
They are also known as tear-off menus, particularly in relation to the Motif
toolkit. <br><br><br>

      

### Resource Requirements

{{< resources >}}

<p>

### Notes

1.  Only under Motif 2.0 - previous versions of mwm support none of the listed
    features.
2.  The binary size is taken to be the size of the executable, stripped and
    not including shared libraries.
3.  The memory size is taken to be the memory taken up by the window manager
    when running. It is the size of the program's text area + data area +
    stack.
4.  The two values in each column are for version 1 of fvwm and version 2
    respectively.
5.  These are modules for fvwm and derivatives (fvwm95 & afterstep), and
    should be added to the data for the appropriate window manager itself, if
    they are used. There are numerous other modules available, all of which
    will increase the resource requirements.
6.  This is a module for afterstep, which is similar to FvwmButtons. See note
    5.
