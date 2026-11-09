Approved isolated JSmol lifecycle prototype + requested before/after video.
Main production source/data/MOL/core/React are unchanged.

Source:
base-source.js.gz: pinned top-level CDN bundle, license headers retained.
lifecycle-helper.js: new per-applet lifecycle helper.
build.py: deterministic three-site patch plus helper; run from repository root.
It defaults to /tmp/namelecule-jsmol-lifecycle-prototype-20261031; override with
NAMELECULE_JSMOL_PROTOTYPE_ROOT. It creates only that isolated app/vendor layout,
reads the archived base/helper and Main HTML, and writes the candidate/diff/hash
manifest. It does not launch a browser, edit production or pin all remote j2s.
candidate-source.js.gz is the exact tested generated candidate.

Browser diagnostics used a separate Firefox profile/BiDi9237 and server8029;
user browser/server8013 untouched. /slow/ adds0.5s SDF/SPT response delay only.
Archived browser scripts preserve original absolute /tmp paths and are not
standalone tests against a user browser. Recreate an isolated environment first.
All browser checks, video capture/encoding/decoding are Developer evidence.

summarize.py build() reads/recomputes stored evidence without writing.
Direct execution writes summary.json. test-ownership.js is a deterministic JSC
unit with mocked schedulers/panels, not two actual Jmol engines. It reads the
helper and generated candidate under the preserved /tmp prototype path.

Video:
watch.html uses only the adjacent MP4/poster, and works as a local page.
video.html + video-child.html are the live comparison harness source, not Main.
record-video.py captured105actual viewport PNGs with monotonic times. Their
original relative names/times/SHA256 are in video-frame-manifest.json and
video-frames.zip. To re-encode, extract to a chosen temporary directory and
create an array {path:absolutePNG,seconds:recordedSeconds} for encode-video.m.
Native macOS compilation:
clang -fobjc-arc -framework Foundation -framework AVFoundation -framework CoreMedia -framework CoreVideo -framework CoreGraphics -framework ImageIO encode-video.m -o /tmp/namelecule-encode-video
Encoding uses native video services and may require permission outside sandbox.
No dependencies installed. Actual frame times are offset to zero; encoded output
is H.264 MP4 without audio. Full decode and all-source-time checks are stored.
extract-frame.m (same native frameworks) extracts an exact-time preview.
Bit-identical re-encoding is not claimed. Source code rebuild is deterministic.

No production integration, universal reliability, model-completion-contract fix,
full337-step/Safari/BFCache/offline/conference certification is claimed.
Review/final verification/cleanup are recorded separately.
