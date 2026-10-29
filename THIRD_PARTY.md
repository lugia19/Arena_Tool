# Third-party software

Arena Maker itself is GPL-3.0 (see [LICENSE](LICENSE)).

## Tools (tools.zip)

Downloaded on first run from this repo's releases (`tools-N` tags) into `tools/`. Each tool is unmodified apart from
the configuration noted; the zip's `LICENSES` folder holds the license texts and `SOURCES.txt`.

| Tool | Version | License | Source |
|---|---|---|---|
| WitchyBND | 3.0.1.0 | GPL-3.0 | https://github.com/ividyon/WitchyBND/tree/3.0.1.0 |
| rewwise bnk2json | 0.3.2 | MIT or Apache-2.0 | https://github.com/vswarte/rewwise/tree/v0.3.2 |
| texconv (DirectXTex) | 2024.6.5.1 (June 2024) | MIT | https://github.com/microsoft/DirectXTex/tree/jun2024 |
| me3 | 0.13.0 | Apache-2.0 or MIT | https://github.com/garyttierney/me3/tree/v0.13.0 |

WitchyBND configuration added by Arena Maker: `appsettings.override.json`, the Paramdex extracted from
`Assets/Paramdex.zip`, and `Assets/Paramdex/AC6/Upgrader/version.txt` raised to `1_09_1_0042L`. Oodle
(`oo2core_*.dll`) is not distributed; it is copied from the game folder.

## Python packages (requirements.txt)

| Package | License |
|---|---|
| PyQt6 | GPL-3.0 |
| cryptography | Apache-2.0 or BSD-3-Clause |
| numpy | BSD-3-Clause |
| Pillow | MIT-CMU |
| soundfile | BSD-3-Clause (bundles libsndfile, LGPL-2.1) |

## Fonts

`resources/Jura-SemiBold.ttf`: Jura by Daniel Johnson, SIL Open Font License 1.1
(https://github.com/ossobuffo/jura).
