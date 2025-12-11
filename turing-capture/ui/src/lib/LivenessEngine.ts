// TuringIdentity™ Liveness Engine
// MediaPipe FaceMesh + Blink/Motion Detection + Adaptive Thresholds

export interface LivenessResult {
  livenessScore: number;
  blinkScore: number;
  motionScore: number;
  facePresent: boolean;
  faceCentered: boolean;
  faceSize: number;
  landmarks: any[];
  confidence: number;
}

export interface LivenessConfig {
  minBlinkScore: number;
  minMotionScore: number;
  minLivenessScore: number;
  minFaceSize: number;
  maxFaceSize: number;
  centerTolerance: number;
}

const DEFAULT_CONFIG: LivenessConfig = {
  minBlinkScore: 0.3,
  minMotionScore: 0.2,
  minLivenessScore: 0.75,
  minFaceSize: 0.15,
  maxFaceSize: 0.85,
  centerTolerance: 0.15,
};

export class LivenessEngine {
  private lastLandmarks: number[][] | null = null;
  private blinkHistory: number[] = [];
  private motionHistory: number[] = [];
  private config: LivenessConfig;
  private frameCount: number = 0;

  constructor(config: Partial<LivenessConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Compute liveness score from face landmarks
   * Returns comprehensive liveness analysis
   */
  computeLiveness(landmarks: any[]): LivenessResult {
    this.frameCount++;

    if (!landmarks || landmarks.length === 0) {
      return {
        livenessScore: 0,
        blinkScore: 0,
        motionScore: 0,
        facePresent: false,
        faceCentered: false,
        faceSize: 0,
        landmarks: [],
        confidence: 0,
      };
    }

    // Extract coordinate arrays
    const xs = landmarks.map((l: any) => l.x);
    const ys = landmarks.map((l: any) => l.y);
    const zs = landmarks.map((l: any) => l.z || 0);

    // Calculate face bounding box
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const faceWidth = maxX - minX;
    const faceHeight = maxY - minY;
    const faceSize = Math.max(faceWidth, faceHeight);

    // Check if face is centered
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    const faceCentered =
      Math.abs(centerX - 0.5) < this.config.centerTolerance &&
      Math.abs(centerY - 0.5) < this.config.centerTolerance;

    // Heuristic 1: Eye aspect ratio for blink detection
    // Using eye landmarks (left eye: 33, 160, 158, 133; right eye: 362, 385, 387, 263)
    const blinkScore = this.computeBlinkScore(landmarks);
    this.blinkHistory.push(blinkScore);
    if (this.blinkHistory.length > 30) this.blinkHistory.shift();

    // Heuristic 2: Head micro-motion detection
    let motionScore = 0;
    if (this.lastLandmarks && this.frameCount > 5) {
      motionScore = this.computeMotionScore(landmarks);
      this.motionHistory.push(motionScore);
      if (this.motionHistory.length > 30) this.motionHistory.shift();
    }

    this.lastLandmarks = landmarks.map((l: any) => [l.x, l.y, l.z || 0]);

    // Calculate average blink and motion over time
    const avgBlink =
      this.blinkHistory.length > 0
        ? this.blinkHistory.reduce((a, b) => a + b, 0) / this.blinkHistory.length
        : blinkScore;

    const avgMotion =
      this.motionHistory.length > 0
        ? this.motionHistory.reduce((a, b) => a + b, 0) / this.motionHistory.length
        : motionScore;

    // Weighted final liveness score
    // Blink: 40%, Motion: 40%, Face positioning: 20%
    const positionScore = faceCentered && faceSize > this.config.minFaceSize && faceSize < this.config.maxFaceSize ? 1 : 0;
    const livenessScore = 0.4 * avgBlink + 0.4 * avgMotion + 0.2 * positionScore;

    // Overall confidence based on frame count and consistency
    const confidence = Math.min(1, this.frameCount / 30) * (faceCentered ? 1 : 0.7);

    return {
      livenessScore: Math.min(1, Math.max(0, livenessScore)),
      blinkScore: avgBlink,
      motionScore: avgMotion,
      facePresent: true,
      faceCentered,
      faceSize,
      landmarks,
      confidence,
    };
  }

  /**
   * Compute blink score using eye aspect ratio
   */
  private computeBlinkScore(landmarks: any[]): number {
    try {
      // Left eye landmarks (simplified)
      const leftEyeTop = landmarks[159];
      const leftEyeBottom = landmarks[145];
      const leftEyeLeft = landmarks[33];
      const leftEyeRight = landmarks[133];

      // Right eye landmarks (simplified)
      const rightEyeTop = landmarks[386];
      const rightEyeBottom = landmarks[374];
      const rightEyeLeft = landmarks[362];
      const rightEyeRight = landmarks[263];

      // Calculate eye aspect ratios
      const leftEAR = this.calculateEAR(leftEyeTop, leftEyeBottom, leftEyeLeft, leftEyeRight);
      const rightEAR = this.calculateEAR(rightEyeTop, rightEyeBottom, rightEyeLeft, rightEyeRight);

      // Average EAR
      const avgEAR = (leftEAR + rightEAR) / 2;

      // Detect blink (EAR drops below threshold)
      // Normal EAR ~0.3, blink EAR ~0.1
      const blinkDetected = avgEAR < 0.2;

      // Return normalized score (higher = more blink activity)
      return blinkDetected ? 1 : Math.max(0, 1 - avgEAR * 2);
    } catch (e) {
      return 0;
    }
  }

  /**
   * Calculate Eye Aspect Ratio (EAR)
   */
  private calculateEAR(top: any, bottom: any, left: any, right: any): number {
    const verticalDist = Math.sqrt(
      Math.pow(top.x - bottom.x, 2) + Math.pow(top.y - bottom.y, 2)
    );
    const horizontalDist = Math.sqrt(
      Math.pow(left.x - right.x, 2) + Math.pow(left.y - right.y, 2)
    );
    return verticalDist / (horizontalDist + 0.001); // Avoid division by zero
  }

  /**
   * Compute motion score using landmark displacement
   */
  private computeMotionScore(landmarks: any[]): number {
    if (!this.lastLandmarks) return 0;

    try {
      // Use nose tip (landmark 1) and chin (landmark 152) for motion detection
      const noseTip = landmarks[1];
      const chin = landmarks[152];

      const lastNose = this.lastLandmarks[1];
      const lastChin = this.lastLandmarks[152];

      // Calculate displacement
      const noseDx = Math.abs(noseTip.x - lastNose[0]);
      const noseDy = Math.abs(noseTip.y - lastNose[1]);
      const chinDx = Math.abs(chin.x - lastChin[0]);
      const chinDy = Math.abs(chin.y - lastChin[1]);

      const totalMotion = noseDx + noseDy + chinDx + chinDy;

      // Normalize motion (typical micro-motion is 0.001-0.01)
      const normalizedMotion = Math.min(1, totalMotion * 50);

      return normalizedMotion;
    } catch (e) {
      return 0;
    }
  }

  /**
   * Check if liveness requirements are met
   */
  isLivenessValid(result: LivenessResult): boolean {
    return (
      result.livenessScore >= this.config.minLivenessScore &&
      result.facePresent &&
      result.faceCentered &&
      result.faceSize >= this.config.minFaceSize &&
      result.faceSize <= this.config.maxFaceSize &&
      result.confidence >= 0.8
    );
  }

  /**
   * Reset engine state
   */
  reset(): void {
    this.lastLandmarks = null;
    this.blinkHistory = [];
    this.motionHistory = [];
    this.frameCount = 0;
  }

  /**
   * Get guidance message based on liveness result
   */
  getGuidanceMessage(result: LivenessResult): string {
    if (!result.facePresent) {
      return "Position your face in the frame";
    }
    if (result.faceSize < this.config.minFaceSize) {
      return "Move closer to the camera";
    }
    if (result.faceSize > this.config.maxFaceSize) {
      return "Move back from the camera";
    }
    if (!result.faceCentered) {
      return "Center your face in the frame";
    }
    if (result.blinkScore < this.config.minBlinkScore) {
      return "Blink naturally";
    }
    if (result.motionScore < this.config.minMotionScore) {
      return "Move your head slightly";
    }
    if (result.livenessScore < this.config.minLivenessScore) {
      return "Hold still... capturing soon";
    }
    return "Perfect! Capturing...";
  }
}
