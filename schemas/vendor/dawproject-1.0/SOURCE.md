# DAWproject 1.0 vendored specification source

- Upstream: `https://github.com/bitwig/dawproject`
- Pinned upstream commit: `ee4dcdde75940f30e14e55401a26955a58b8322b`
- Evidence date: `2026-09-11`
- Upstream license: MIT

Vendored source identity:

| File | Upstream Git blob SHA | Local Git blob SHA | Status |
|---|---|---|---|
| `Project.xsd` | `ef4055976e0ea5615567c363a5c83a13e79b768c` | `9e888c050e1905a33ba905310ecd3c9a6baa41e0` | semantic byte snapshot differs only by the final LF after `</xs:schema>`; XML/XSD content is otherwise identical |
| `MetaData.xsd` | `cc60f065821b54c7daac6ffbeabe93376329b0cf` | `cc60f065821b54c7daac6ffbeabe93376329b0cf` | byte-exact |
| `LICENSE` | `21ab3d9e328e2872bfda60f1d3caaf7869b0508d` | `21ab3d9e328e2872bfda60f1d3caaf7869b0508d` | byte-exact |

`Project.xsd` upstream size is 27,904 bytes and the local snapshot is 27,903 bytes. The only observed difference is the trailing newline at EOF. MUSICA therefore does **not** claim byte-exact identity for that one file; implementation evidence records the pinned upstream revision and the local XSD content hash used at runtime.

이 파일들은 일반 MUSICA 계약 테스트가 네트워크에 의존하지 않도록 vendoring 합니다. `Project.xsd`의 1바이트 EOF newline 차이는 숨기지 않고 provenance에 명시하며, 실제 검증은 로컬 XSD의 exact hash와 pinned upstream revision을 함께 기록합니다. 원본 MIT 라이선스는 변경 없이 보존합니다.
