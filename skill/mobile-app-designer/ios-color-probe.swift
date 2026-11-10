// Prints the RGB of UIKit system colors, resolved for each appearance, on the simulator it runs on.
import UIKit

let colors: [(String, UIColor)] = [
    ("systemBackground", .systemBackground),
    ("secondarySystemBackground", .secondarySystemBackground),
    ("tertiarySystemBackground", .tertiarySystemBackground),
    ("systemGroupedBackground", .systemGroupedBackground),
    ("secondarySystemGroupedBackground", .secondarySystemGroupedBackground),
    ("tertiarySystemGroupedBackground", .tertiarySystemGroupedBackground),
    ("label", .label),
    ("secondaryLabel", .secondaryLabel),
    ("separator", .separator),
    ("systemFill", .systemFill),
    ("secondarySystemFill", .secondarySystemFill),
    ("tertiarySystemFill", .tertiarySystemFill),
    ("tertiaryLabel", .tertiaryLabel),
    ("opaqueSeparator", .opaqueSeparator),
    ("systemGray", .systemGray),
    ("systemRed", .systemRed),
    ("systemOrange", .systemOrange),
    ("systemYellow", .systemYellow),
    ("systemGreen", .systemGreen),
    ("systemMint", .systemMint),
    ("systemTeal", .systemTeal),
    ("systemCyan", .systemCyan),
    ("systemBlue", .systemBlue),
    ("systemIndigo", .systemIndigo),
    ("systemPurple", .systemPurple),
    ("systemPink", .systemPink),
    ("systemBrown", .systemBrown),
]
func traits(_ style: UIUserInterfaceStyle, _ contrast: UIAccessibilityContrast, _ level: UIUserInterfaceLevel) -> UITraitCollection {
    UITraitCollection { t in t.userInterfaceStyle = style; t.accessibilityContrast = contrast; t.userInterfaceLevel = level }
}
let cases: [(String, UITraitCollection)] = [
    ("light", traits(.light, .normal, .base)), ("dark", traits(.dark, .normal, .base)),
    ("dark-elevated", traits(.dark, .normal, .elevated)),
    ("light-hc", traits(.light, .high, .base)), ("dark-hc", traits(.dark, .high, .base)),
    ("dark-elevated-hc", traits(.dark, .high, .elevated)),
]
func hex(_ c: UIColor) -> String {
    var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
    c.getRed(&r, green: &g, blue: &b, alpha: &a)
    return String(format: "#%02X%02X%02X a=%.3f", Int((r * 255).rounded()), Int((g * 255).rounded()), Int((b * 255).rounded()), a)
}
print("os", UIDevice.current.systemVersion)
for (name, color) in colors {
    print(name, cases.map { "\($0.0)=\(hex(color.resolvedColor(with: $0.1)))" }.joined(separator: " "))
}
