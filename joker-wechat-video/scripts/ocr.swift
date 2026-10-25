import Foundation
import Vision
import ImageIO

// Batch OCR with actual Vision confidence and normalized coordinates.
for file in CommandLine.arguments.dropFirst() {
    autoreleasepool {
        do {
            let req = VNRecognizeTextRequest()
            req.recognitionLevel = .accurate
            req.recognitionLanguages = ["zh-Hans", "zh-Hant", "en-US"]
            req.usesLanguageCorrection = true
            try VNImageRequestHandler(url: URL(fileURLWithPath:file)).perform([req])
            let lines: [[String:Any]] = (req.results ?? []).compactMap { obs in
                guard let c = obs.topCandidates(1).first else { return nil }
                let b=obs.boundingBox
                return ["text":c.string,"confidence":c.confidence,"bbox":[b.minX,b.minY,b.width,b.height]]
            }
            let data=try JSONSerialization.data(withJSONObject:["file":file,"lines":lines],options:[.sortedKeys])
            print(String(data:data,encoding:.utf8)!)
        } catch {
            let data=try! JSONSerialization.data(withJSONObject:["file":file,"error":String(describing:error)])
            print(String(data:data,encoding:.utf8)!)
        }
    }
}
