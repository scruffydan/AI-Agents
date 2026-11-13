# Third-party notices

Some agents, shared instructions, and skills in this repository adapt material
from the MIT-licensed projects below. None of them is a dependency.

Agents and shared prompts are single files whose whole text is sent to the model,
so their notices are kept here. Skills are folders, so each adapted skill carries
the upstream `LICENSE` beside its `SKILL.md`; they are listed under
[Adapted skills](#adapted-skills).

Builds copy this file unchanged beside each harness's base instructions, and
installs place it in `~/.codex/`, `~/.claude/`, or `~/.config/opencode/`.
The `source/` links below identify repository files. Installed skill licenses
are beside their `SKILL.md` files in `~/.agents/skills/` (Codex),
`~/.claude/skills/`, or `~/.config/opencode/skills/`.

Each upstream link below is pinned to the last upstream commit that changed the
linked skill before the adaptation landed here.

## Ponytail

- Used in: [source/agents/code-simplifier.md](source/agents/code-simplifier.md)
  and [source/prompts/AGENTS.md](source/prompts/AGENTS.md), which adapt selected
  practices (adapted 2026-11-10).
- Upstream: [Ponytail skill](https://github.com/DietrichGebert/ponytail/blob/df9e89941d50419fd5bcf1de41e28097f1db49b2/skills/ponytail/SKILL.md)
- Upstream license: [LICENSE](https://github.com/DietrichGebert/ponytail/blob/df9e89941d50419fd5bcf1de41e28097f1db49b2/LICENSE)

```text
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## pstack blast-radius skill

- Used in: [source/agents/code-blast-radius.md](source/agents/code-blast-radius.md),
  which adapts selected ideas (adapted 2026-11-12).
- Upstream: [pstack blast-radius skill](https://github.com/cursor/plugins/blob/df581122cde17e6e27686b5a448bde23e4ad4318/pstack/skills/blast-radius/SKILL.md)
- Upstream license: [pstack/LICENSE](https://github.com/cursor/plugins/blob/df581122cde17e6e27686b5a448bde23e4ad4318/pstack/LICENSE)

```text
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Adapted skills

Each skill's `SKILL.md` links the upstream file it adapts, and its `LICENSE` is
an unchanged copy of the upstream license file.

| Skill | Upstream project | Copyright | Notice |
|---|---|---|---|
| `teach` | [pstack](https://github.com/cursor/plugins) (`pstack/` in cursor/plugins) | Lauren Tan | [LICENSE](source/skills/teach/LICENSE) |
| `technical-writing` | [pstack](https://github.com/cursor/plugins) (`pstack/` in cursor/plugins) | Lauren Tan | [LICENSE](source/skills/technical-writing/LICENSE) |
| `unslop` | [pstack](https://github.com/cursor/plugins) (`pstack/` in cursor/plugins) | Lauren Tan | [LICENSE](source/skills/unslop/LICENSE) |
| `why` | [pstack](https://github.com/cursor/plugins) (`pstack/` in cursor/plugins) | Lauren Tan | [LICENSE](source/skills/why/LICENSE) |
| `to-tickets` | [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | [LICENSE](source/skills/to-tickets/LICENSE) |
| `writing-for-agents` | [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | [LICENSE](source/skills/writing-for-agents/LICENSE) |
| `file-pr` | [tstack](https://github.com/t3dotgg/tstack) | Theo Browne | [LICENSE](source/skills/file-pr/LICENSE) |
| `leaving-pr-comments` | [tstack](https://github.com/t3dotgg/tstack) | Theo Browne | [LICENSE](source/skills/leaving-pr-comments/LICENSE) |
| `modernize` | [tstack](https://github.com/t3dotgg/tstack) | Theo Browne | [LICENSE](source/skills/modernize/LICENSE) |
| `takeover` | [tstack](https://github.com/t3dotgg/tstack) | Theo Browne | [LICENSE](source/skills/takeover/LICENSE) |
