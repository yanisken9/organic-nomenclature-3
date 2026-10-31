// macOS icon packaging of the existing logo's molecule; no new artwork.
ObjC.import("AppKit");

function run(argv) {
    const source = $.NSImage.alloc.initWithContentsOfFile(argv[0]);
    if (!source || !source.valid) throw new Error("Cannot read Namelecule logo");
    const size = 1024;
    const available = 944;
    // Isolate the methane emblem to the left of the wordmark in the fixed v1
    // asset (2172 x 724). AppKit uses bottom-left source coordinates.
    const sourceRect = $.NSMakeRect(20, 70, 510, 590);
    const scale = Math.min(available / sourceRect.size.width, available / sourceRect.size.height);
    const width = sourceRect.size.width * scale;
    const height = sourceRect.size.height * scale;
    const canvas = $.NSImage.alloc.initWithSize($.NSMakeSize(size, size));
    canvas.lockFocus;
    $.NSColor.clearColor.set;
    $.NSRectFill($.NSMakeRect(0, 0, size, size));
    source.drawInRectFromRectOperationFraction(
        $.NSMakeRect((size - width) / 2, (size - height) / 2, width, height),
        sourceRect, $.NSCompositingOperationSourceOver, 1);
    canvas.unlockFocus;
    const bitmap = $.NSBitmapImageRep.imageRepWithData(canvas.TIFFRepresentation);
    const png = bitmap.representationUsingTypeProperties($.NSBitmapImageFileTypePNG, $.NSDictionary.dictionary);
    if (!png.writeToFileAtomically(argv[1], true)) throw new Error("Cannot write icon PNG");
}
