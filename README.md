# aegean-licensing

[![Built with AIKit](https://img.shields.io/badge/built%20with-AIKit-6f42c1)](https://github.com/AegeanWorks/AIKit)

Official licensing framework, commercial agreements, and certificate tooling for AegeanWorks

## ⚡ 30-Second Cold-Start Quick Reference

- **Runtime Prerequisites**: <FILL: each runtime this project needs and its minimum version>
- **Canonical Regression Shield Gate**:
  ```bash
  <FILL: the command that runs the whole test suite from this project root>
  ```

### 🛠️ AIKit Commands (run from the AIKit folder)
| Role | Command |
|---|---|
| Status, task and gates | `python aikit.py status aegean-licensing` |
| Phase 4: every gate | `python aikit.py check aegean-licensing` |
| Repair memory and map, then check | `python aikit.py fix aegean-licensing` |
| Resume an interrupted task | `python aikit.py resume aegean-licensing` |

## 📦 What's Inside

```text
aegean-licensing/
├── .gitignore                <- transient AIKit state excluded
├── LICENSE                   <- GNU AGPL-3.0
├── COMMERCIAL.md             <- Commercial licensing terms
├── README.md
└── .aikit/                   <- this project's memory: record, ledger, decisions
```

## 📜 License

GNU Affero General Public License v3.0; see [LICENSE](LICENSE). For commercial licensing and proprietary rights, see [COMMERCIAL.md](COMMERCIAL.md).
