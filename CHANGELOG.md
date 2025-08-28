# CHANGELOG


## v1.1.2 (2025-08-28)

### Bug Fixes

- **theme**: Prevent reapplying the same theme if already set
  ([`bc9ddcf`](https://github.com/bec-project/bec_qthemes/commit/bc9ddcfdee9e6f88cb9ff1445f93b85dab36e44a))


## v1.1.1 (2025-08-26)

### Bug Fixes

- **update**: Fix bug that prevented widgets from receiving theme updates
  ([`2e7117d`](https://github.com/bec-project/bec_qthemes/commit/2e7117d3468700f953fb9471e77e17dd7bda0ae8))


## v1.1.0 (2025-08-25)

### Bug Fixes

- Vim icon added
  ([`d9cfce4`](https://github.com/bec-project/bec_qthemes/commit/d9cfce45e3dda98a9d9d9417d1a9c2306d7f0cd8))

- **qss**: Styling review
  ([`cfbca4f`](https://github.com/bec-project/bec_qthemes/commit/cfbca4fc079f4f804e08829ea1d43b6f1993a863))

### Features

- **pyqtgraph**: Pyqtgraph options added to qss
  ([`69b0204`](https://github.com/bec-project/bec_qthemes/commit/69b0204ae532613c1cb85e70928399b6a193884a))


## v1.0.0 (2025-08-22)

### Features

- **bec_qthemes**: Whole repo rewritten
  ([`341cd47`](https://github.com/bec-project/bec_qthemes/commit/341cd4729d9f22f144826f456df740f7633c87c4))


## v0.7.1 (2025-08-22)

### Bug Fixes

- **accent colors**: Set default accent colors for light and dark themes
  ([`3a47101`](https://github.com/bec-project/bec_qthemes/commit/3a47101e4468bb4d5b12a9c730b661e2885180b8))

### Continuous Integration

- Add semantic_release job
  ([`cc7a7e9`](https://github.com/bec-project/bec_qthemes/commit/cc7a7e962e3038d2fcf40cf1d080e9cd74626593))

- Fix release vars for github
  ([`fdfe252`](https://github.com/bec-project/bec_qthemes/commit/fdfe252fe11c5bc870bd0f4deb478c9f5a20a7c9))

### Documentation

- Add logo
  ([`862cf5c`](https://github.com/bec-project/bec_qthemes/commit/862cf5c9283923b023b3b2f10e4d999f21816d67))


## v0.7.0 (2024-09-05)

### Bug Fixes

- **theme**: Fixed theme container for linux
  ([`48dc8e6`](https://github.com/bec-project/bec_qthemes/commit/48dc8e6a397d312900c07721eda7052cf3b9fc32))

### Features

- **accent colors**: Added custom accent colors and transitioned to themecontainer
  ([`7a203f8`](https://github.com/bec-project/bec_qthemes/commit/7a203f8cff8993e9f99c1bed292658f685833b0f))


## v0.6.0 (2024-08-31)

### Features

- **event filter**: Added option to disable the event filter
  ([`6afb9d3`](https://github.com/bec-project/bec_qthemes/commit/6afb9d3954775c25bd612b19096f4508c10fba23))


## v0.5.1 (2024-08-31)

### Bug Fixes

- **theme_signal**: Do not recreate theme signal instance on repeated calls
  ([`9a4afda`](https://github.com/bec-project/bec_qthemes/commit/9a4afdac4459414b7bc635bc80c5a3214f1eb2e1))


## v0.5.0 (2024-08-30)

### Features

- Added theme signal to qapp
  ([`bb71cba`](https://github.com/bec-project/bec_qthemes/commit/bb71cba8e17ca8d5b7b91d4f6115c3e618c63237))


## v0.4.3 (2024-08-28)

### Bug Fixes

- Fixed self.color typo
  ([`5c93b01`](https://github.com/bec-project/bec_qthemes/commit/5c93b01f2e3dc9418901f12ddd9b9008a8e24dd6))


## v0.4.2 (2024-08-23)

### Bug Fixes

- Fixed icon update
  ([`a5918a3`](https://github.com/bec-project/bec_qthemes/commit/a5918a3a0d4927ed43529e427d1300ce76a6ee33))


## v0.4.1 (2024-08-23)

### Bug Fixes

- Theme fallback
  ([`640911a`](https://github.com/bec-project/bec_qthemes/commit/640911a4afc07020c666b06ebd5322ba58328757))


## v0.4.0 (2024-08-23)

### Bug Fixes

- Use currently selected theme for icons
  ([`2a0c73e`](https://github.com/bec-project/bec_qthemes/commit/2a0c73ec5fcb5fb6ea97fe31ab719f3687f26f95))

### Features

- Store theme and theme mode in qapp
  ([`6761281`](https://github.com/bec-project/bec_qthemes/commit/67612811ba077ae823a6c4f7d84b0f2edafdf760))


## v0.3.0 (2024-08-23)

### Features

- Added fft and log_scale icons; removed duplicates
  ([`35a4a8d`](https://github.com/bec-project/bec_qthemes/commit/35a4a8db39f96340e306701a352836e3639038af))

- Added support for stoke color replacement
  ([`d26db16`](https://github.com/bec-project/bec_qthemes/commit/d26db16d3596484f497da0869add12ebf2945606))

- Fall back to non-filled icons if filled icons are not found
  ([`1705a9d`](https://github.com/bec-project/bec_qthemes/commit/1705a9df0984b7f545f0dc36dfcfcce9e24305cc))


## v0.2.1 (2024-08-23)

### Bug Fixes

- Fixed render update for custom icons
  ([`72190c4`](https://github.com/bec-project/bec_qthemes/commit/72190c45884ecda5dc9c5ef109d8730f286f8f0e))


## v0.2.0 (2024-08-21)

### Features

- Added option to create filled icons
  ([`538893d`](https://github.com/bec-project/bec_qthemes/commit/538893d898825a18f01d47c705d3c2869016d892))


## v0.1.1 (2024-08-21)

### Bug Fixes

- Fixed material icon width
  ([`da2381d`](https://github.com/bec-project/bec_qthemes/commit/da2381d8abaa40e7aedf2f9b9c2d94b6a1625ab7))


## v0.1.0 (2024-08-21)

### Build System

- Import material icons by default
  ([`d1dcbfd`](https://github.com/bec-project/bec_qthemes/commit/d1dcbfdd48fc4f67d69d17cf12f6e084df26cf90))

### Features

- Added material_icons engine
  ([`3a1a37e`](https://github.com/bec-project/bec_qthemes/commit/3a1a37e241a7f32e0ab209c7ce2ffc18160ed9f6))


## v0.0.2 (2024-07-22)

### Bug Fixes

- Removed webengine deps
  ([`2b887ff`](https://github.com/bec-project/bec_qthemes/commit/2b887ffabc6932ffc3b8518ba065223f828c2f88))


## v0.0.1 (2024-07-22)

### Bug Fixes

- Fixed darkdetect dependency
  ([`93d3561`](https://github.com/bec-project/bec_qthemes/commit/93d35616b6fc4198edc9c5de57e8c7272ecac454))

### Continuous Integration

- Fixed install of qt deps
  ([`ae1eae3`](https://github.com/bec-project/bec_qthemes/commit/ae1eae360cf23e95d81e91fb54b73ca659291d33))

- Fixed test job name
  ([`c1f83d2`](https://github.com/bec-project/bec_qthemes/commit/c1f83d242e585e6be1aef7fdaf660fd3bb2fc38e))

- Fixed test stage and removed outdated jobs
  ([`a33e36d`](https://github.com/bec-project/bec_qthemes/commit/a33e36d660501a4ac785762839872f19d44bd756))
