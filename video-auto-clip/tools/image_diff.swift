#!/usr/bin/env swift

import Foundation
import CoreGraphics
import ImageIO

let targetSize = 48

func usage() {
    let text = """
    用法:
      image_diff.swift reference_image image1 [image2 ...]

    输出:
      path<TAB>score

    说明:
      - score 越小越相似，范围 0.0 ~ 1.0
      - 内部会缩放到 \(targetSize)x\(targetSize) 灰度图后计算平均绝对差
    """
    FileHandle.standardError.write(Data(text.utf8))
}

func loadImage(_ path: String) -> CGImage? {
    let url = URL(fileURLWithPath: path)
    guard let src = CGImageSourceCreateWithURL(url as CFURL, nil) else {
        return nil
    }
    return CGImageSourceCreateImageAtIndex(src, 0, nil)
}

func grayscalePixels(from image: CGImage) -> [UInt8]? {
    let width = targetSize
    let height = targetSize
    let bytesPerRow = width
    var pixels = [UInt8](repeating: 0, count: width * height)

    guard let colorSpace = CGColorSpace(name: CGColorSpace.genericGrayGamma2_2),
          let ctx = CGContext(
            data: &pixels,
            width: width,
            height: height,
            bitsPerComponent: 8,
            bytesPerRow: bytesPerRow,
            space: colorSpace,
            bitmapInfo: CGImageAlphaInfo.none.rawValue
          ) else {
        return nil
    }

    ctx.interpolationQuality = .medium
    ctx.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    return pixels
}

func meanAbsoluteDiff(_ lhs: [UInt8], _ rhs: [UInt8]) -> Double {
    guard lhs.count == rhs.count, !lhs.isEmpty else {
        return 1.0
    }
    var total = 0.0
    for i in 0..<lhs.count {
        total += abs(Double(lhs[i]) - Double(rhs[i]))
    }
    return total / Double(lhs.count) / 255.0
}

let args = Array(CommandLine.arguments.dropFirst())
if args.count < 2 || args.contains("-h") || args.contains("--help") {
    usage()
    exit(args.count < 2 ? 1 : 0)
}

let referencePath = args[0]
let targetPaths = Array(args.dropFirst())

guard let referenceImage = loadImage(referencePath),
      let referencePixels = grayscalePixels(from: referenceImage) else {
    FileHandle.standardError.write(Data("无法读取参考图片: \(referencePath)\n".utf8))
    exit(2)
}

for path in targetPaths {
    guard let image = loadImage(path),
          let pixels = grayscalePixels(from: image) else {
        FileHandle.standardError.write(Data("无法读取图片: \(path)\n".utf8))
        exit(3)
    }
    let score = meanAbsoluteDiff(referencePixels, pixels)
    FileHandle.standardOutput.write(Data("\(path)\t\(String(format: "%.6f", score))\n".utf8))
}
