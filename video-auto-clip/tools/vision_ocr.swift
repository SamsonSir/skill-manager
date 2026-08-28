#!/usr/bin/env swift

import Foundation
import Vision
import ImageIO

struct OCRResult: Encodable {
    let path: String
    let text: String
    let lines: [String]
}

struct OCRRegion: Encodable {
    let text: String
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct OCRRegionsResult: Encodable {
    let path: String
    let text: String
    let regions: [OCRRegion]
}

func usage() {
    let text = """
    用法:
      vision_ocr.swift [--jsonl|--tsv|--regions-jsonl] image1 [image2 ...]

    说明:
      - 默认单文件输出纯文本
      - 多文件或显式 --jsonl 时输出 JSON Lines
      - --tsv 输出: path<TAB>text
      - --regions-jsonl 输出每个识别块的文本与归一化坐标
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

func recognizeTextRegions(in image: CGImage) throws -> [OCRRegion] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["zh-Hans", "en-US"]

    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try handler.perform([request])

    guard let results = request.results else {
        return []
    }

    return results.compactMap { observation in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }
        let text = candidate.string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return nil
        }
        let box = observation.boundingBox
        return OCRRegion(
            text: text,
            x: Double(box.origin.x),
            y: Double(box.origin.y),
            width: Double(box.width),
            height: Double(box.height)
        )
    }
}

func recognizeText(in image: CGImage) throws -> [String] {
    return try recognizeTextRegions(in: image).map(\.text).filter { !$0.isEmpty }
}

func recognizeRegionsResult(in image: CGImage, path: String) throws -> OCRRegionsResult {
    let regions = try recognizeTextRegions(in: image)
    let text = regions.map(\.text).joined(separator: "\n")
    return OCRRegionsResult(path: path, text: text, regions: regions)
}

var emitRegionsJSONL = false
var emitJSONL = false
var emitTSV = false
var imagePaths: [String] = []

for arg in CommandLine.arguments.dropFirst() {
    if arg == "--jsonl" {
        emitJSONL = true
    } else if arg == "--tsv" {
        emitTSV = true
    } else if arg == "--regions-jsonl" {
        emitRegionsJSONL = true
    } else if arg == "-h" || arg == "--help" {
        usage()
        exit(0)
    } else {
        imagePaths.append(arg)
    }
}

if imagePaths.isEmpty {
    usage()
    exit(1)
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.withoutEscapingSlashes]

for path in imagePaths {
    guard let image = loadImage(path) else {
        FileHandle.standardError.write(Data("无法读取图片: \(path)\n".utf8))
        exit(2)
    }

    let lines: [String]
    do {
        lines = try recognizeText(in: image)
    } catch {
        FileHandle.standardError.write(Data("OCR 失败: \(path) | \(error)\n".utf8))
        exit(3)
    }

    let text = lines.joined(separator: "\n")

    if emitRegionsJSONL {
        let result: OCRRegionsResult
        do {
            result = try recognizeRegionsResult(in: image, path: path)
        } catch {
            FileHandle.standardError.write(Data("OCR 失败: \(path) | \(error)\n".utf8))
            exit(3)
        }
        let data = try encoder.encode(result)
        FileHandle.standardOutput.write(data)
        FileHandle.standardOutput.write(Data("\n".utf8))
    } else if emitTSV {
        let flatText = text
            .replacingOccurrences(of: "\t", with: " ")
            .replacingOccurrences(of: "\n", with: " ")
        FileHandle.standardOutput.write(Data("\(path)\t\(flatText)\n".utf8))
    } else if emitJSONL || imagePaths.count > 1 {
        let result = OCRResult(path: path, text: text, lines: lines)
        let data = try encoder.encode(result)
        FileHandle.standardOutput.write(data)
        FileHandle.standardOutput.write(Data("\n".utf8))
    } else {
        FileHandle.standardOutput.write(Data(text.utf8))
    }
}
